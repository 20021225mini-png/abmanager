"""案件欄位整理測試。"""

from datetime import datetime
from unittest import TestCase
from zoneinfo import ZoneInfo

from config.texts import (
    ALL_FILTER,
    COMPLETED_FILTER,
    FINAL_RESOLUTION_OPTIONS,
    PENDING_FILTER,
    PROCESSING_FILTER,
)
from data.case_repository import CaseDataset
from services.case_service import CaseService
from services.models import DashboardFilters

TAIPEI = ZoneInfo("Asia/Taipei")


class StubCaseRepository:
    """提供測試資料的案件來源。"""

    def __init__(self, rows: tuple[dict[str, object], ...]) -> None:
        self._rows = rows

    def load_cases(self) -> CaseDataset:
        return CaseDataset(rows=self._rows)


class CaseServiceTest(TestCase):
    def test_situation_is_used_as_abnormal_type(self) -> None:
        service = CaseService(
            StubCaseRepository(
                rows=(
                    {
                        "CASE_NO": "A260729-001",
                        "CREATED_AT": "2026-07-29 10:33:00",
                        "PART_NO": "759220D130",
                        "QTY": "4",
                        "SITUATION": "地上撿到",
                        "STAGE": "待處理",
                        "FLOOR": "2F",
                        "LAYER": "中",
                    },
                )
            )
        )

        snapshot = service.load_snapshot(
            now=datetime(2026, 7, 29, 14, 0, tzinfo=TAIPEI)
        )

        self.assertEqual(snapshot.cases[0].abnormal_type, "地上撿到")

    def test_missing_source_values_stay_blank(self) -> None:
        service = CaseService(
            StubCaseRepository(
                rows=(
                    {
                        "CASE_NO": "A260729-001",
                        "CREATED_AT": "2026-07-29 10:33:00",
                        "PART_NO": "759220D130",
                        "QTY": "4",
                        "SITUATION": "地上撿到",
                        "STAGE": "待處理",
                        "FLOOR": "2F",
                        "LAYER": "中",
                        "ORIGINAL_CART": None,
                        "HANDLER": None,
                    },
                )
            )
        )

        snapshot = service.load_snapshot(
            now=datetime(2026, 7, 29, 14, 0, tzinfo=TAIPEI)
        )
        case = snapshot.cases[0]

        self.assertEqual(case.cart_no, "")
        self.assertEqual(case.handler, "")
        self.assertEqual(case.on_site_instruction, "未開放")
        self.assertEqual(case.block, "2F-中")

    def test_pending_stage_marks_first_node_as_current(self) -> None:
        case = self._load_single_case(
            {
                "STAGE": "待處理",
                "FINAL_RESOLUTION": None,
            }
        )

        self.assertEqual(
            [(node.label, node.state) for node in case.stage_nodes],
            [
                ("待處理", "current"),
                ("處理中", "pending"),
                ("處理結果", "pending"),
            ],
        )

    def test_processing_stage_marks_previous_node_as_completed(self) -> None:
        case = self._load_single_case(
            {
                "STAGE": "處理中",
                "FINAL_RESOLUTION": None,
            }
        )

        self.assertEqual(
            [(node.label, node.state) for node in case.stage_nodes],
            [
                ("待處理", "completed"),
                ("處理中", "current"),
                ("處理結果", "pending"),
            ],
        )

    def test_each_final_resolution_replaces_result_node(self) -> None:
        for final_resolution in FINAL_RESOLUTION_OPTIONS:
            with self.subTest(final_resolution=final_resolution):
                values = {
                    "STAGE": "處理結果",
                    "FINAL_RESOLUTION": final_resolution,
                    "SHELVING_STATUS": "已完成",
                }
                if final_resolution in (
                    "重新丈量",
                    "請資訊部修正異常系統資料",
                ):
                    values["SHELVING_COMPLETED_AT"] = "2026-07-29 13:00:00"
                case = self._load_single_case(
                    values
                )

                self.assertEqual(
                    [(node.label, node.state) for node in case.stage_nodes],
                    [
                        ("待處理", "completed"),
                        ("處理中", "completed"),
                        (final_resolution, "completed"),
                    ],
                )

    def test_remeasure_and_system_data_fix_show_shelving_status(self) -> None:
        for final_resolution in (
            "重新丈量",
            "請資訊部修正異常系統資料",
        ):
            with self.subTest(final_resolution=final_resolution):
                case = self._load_single_case(
                    {
                        "STAGE": "處理結果",
                        "FINAL_RESOLUTION": final_resolution,
                        "SHELVING_STATUS": "待上架",
                    }
                )

                self.assertEqual(case.on_site_instruction, "待上架")
                self.assertEqual(case.stage_nodes[-1].state, "followup")

    def test_shelving_completion_turns_result_node_blue(self) -> None:
        case = self._load_single_case(
            {
                "STAGE": "處理結果",
                "FINAL_RESOLUTION": "重新丈量",
                "SHELVING_STATUS": "已完成",
                "SHELVING_COMPLETED_AT": "2026-07-29 13:00:00",
            }
        )

        self.assertEqual(case.stage_nodes[-1].state, "completed")

    def test_shelving_case_keeps_waiting_until_shelving_completed(self) -> None:
        open_case = self._load_single_case(
            {
                "FINAL_RESOLUTION": "重新丈量",
                "CLOSED_AT": "2026-07-29 11:00:00",
                "SHELVING_COMPLETED_AT": None,
            }
        )
        completed_case = self._load_single_case(
            {
                "FINAL_RESOLUTION": "重新丈量",
                "CLOSED_AT": "2026-07-29 11:00:00",
                "SHELVING_COMPLETED_AT": "2026-07-29 13:00:00",
            }
        )

        self.assertEqual(open_case.waiting_time_text, "03時 27分")
        self.assertEqual(completed_case.waiting_time_text, "02時 27分")

    def test_storage_and_overflow_confirmation_are_closed(self) -> None:
        for final_resolution in (
            "零件放入儲位",
            "確認溢品",
        ):
            with self.subTest(final_resolution=final_resolution):
                case = self._load_single_case(
                    {
                        "STAGE": "處理結果",
                        "FINAL_RESOLUTION": final_resolution,
                        "SHELVING_STATUS": "待上架",
                    }
                )

                self.assertEqual(case.on_site_instruction, "已結案")
                self.assertTrue(case.is_completed)
                self.assertEqual(case.waiting_time_text, "時間待補")

    def test_completed_cases_remain_available_under_closed_filter(self) -> None:
        active_row = self._base_row()
        active_row["CASE_NO"] = "ACTIVE-001"
        completed_row = self._base_row()
        completed_row.update(
            {
                "CASE_NO": "DONE-001",
                "FINAL_RESOLUTION": "確認溢品",
                "CLOSED_AT": "2026-07-29 12:00:00",
            }
        )
        service = CaseService(
            StubCaseRepository(rows=(completed_row, active_row))
        )
        snapshot = service.load_snapshot(
            now=datetime(2026, 7, 29, 14, 0, tzinfo=TAIPEI)
        )

        all_cases = service.filter_and_sort(
            snapshot.cases,
            DashboardFilters(),
        )
        completed_cases = service.filter_and_sort(
            snapshot.cases,
            DashboardFilters(stage=COMPLETED_FILTER),
        )

        self.assertEqual(
            [case.case_no for case in all_cases],
            ["ACTIVE-001", "DONE-001"],
        )
        self.assertEqual(
            [case.case_no for case in completed_cases],
            ["DONE-001"],
        )

    def test_all_filter_keeps_completed_cases_at_the_end(self) -> None:
        active_row = self._base_row()
        active_row["CASE_NO"] = "ACTIVE-001"
        completed_row = self._base_row()
        completed_row.update(
            {
                "CASE_NO": "DONE-001",
                "FINAL_RESOLUTION": "確認溢品",
                "CLOSED_AT": "2026-07-29 12:00:00",
            }
        )
        service = CaseService(
            StubCaseRepository(rows=(completed_row, active_row))
        )
        snapshot = service.load_snapshot(
            now=datetime(2026, 7, 29, 14, 0, tzinfo=TAIPEI)
        )

        all_cases = service.filter_and_sort(
            snapshot.cases,
            DashboardFilters(stage=ALL_FILTER),
        )

        self.assertEqual(
            [case.case_no for case in all_cases],
            ["ACTIVE-001", "DONE-001"],
        )

    def test_terminal_resolution_uses_updated_at_and_sorts_last(self) -> None:
        active_row = self._base_row()
        active_row["CASE_NO"] = "ACTIVE-001"
        completed_row = self._base_row()
        completed_row.update(
            {
                "CASE_NO": "DONE-WITHOUT-CLOSED-AT",
                "STAGE": "處理結果",
                "FINAL_RESOLUTION": "零件放入儲位",
                "UPDATED_AT": "2026-07-29 12:00:00",
                "CLOSED_AT": None,
            }
        )
        service = CaseService(
            StubCaseRepository(rows=(completed_row, active_row))
        )
        snapshot = service.load_snapshot(
            now=datetime(2026, 7, 29, 14, 0, tzinfo=TAIPEI)
        )

        all_cases = service.filter_and_sort(
            snapshot.cases,
            DashboardFilters(stage=ALL_FILTER),
        )
        completed_case = next(
            case
            for case in snapshot.cases
            if case.case_no == "DONE-WITHOUT-CLOSED-AT"
        )

        self.assertTrue(completed_case.is_completed)
        self.assertEqual(completed_case.waiting_time_text, "01時 27分")
        self.assertEqual(completed_case.data_errors, ())
        self.assertEqual(
            [case.case_no for case in all_cases],
            ["ACTIVE-001", "DONE-WITHOUT-CLOSED-AT"],
        )

    def test_shelving_case_does_not_use_updated_at_as_completion(self) -> None:
        case = self._load_single_case(
            {
                "STAGE": "處理結果",
                "FINAL_RESOLUTION": "重新丈量",
                "UPDATED_AT": "2026-07-29 12:00:00",
                "SHELVING_COMPLETED_AT": None,
            }
        )

        self.assertFalse(case.is_completed)
        self.assertTrue(case.is_awaiting_shelving)
        self.assertEqual(case.waiting_time_text, "03時 27分")

    def test_operational_stage_filters_use_case_lifecycle(self) -> None:
        pending_row = self._base_row()
        pending_row["CASE_NO"] = "PENDING-001"
        processing_row = self._base_row()
        processing_row.update(
            {
                "CASE_NO": "PROCESSING-001",
                "STAGE": "處理中",
            }
        )
        on_site_row = self._base_row()
        on_site_row.update(
            {
                "CASE_NO": "ONSITE-001",
                "STAGE": "處理結果",
                "FINAL_RESOLUTION": "重新丈量",
                "SHELVING_STATUS": "待上架",
            }
        )
        completed_row = self._base_row()
        completed_row.update(
            {
                "CASE_NO": "DONE-001",
                "STAGE": "處理結果",
                "FINAL_RESOLUTION": "確認溢品",
                "CLOSED_AT": "2026-07-29 12:00:00",
            }
        )
        service = CaseService(
            StubCaseRepository(
                rows=(
                    pending_row,
                    processing_row,
                    on_site_row,
                    completed_row,
                )
            )
        )
        snapshot = service.load_snapshot(
            now=datetime(2026, 7, 29, 14, 0, tzinfo=TAIPEI)
        )

        pending_cases = service.filter_and_sort(
            snapshot.cases,
            DashboardFilters(stage=PENDING_FILTER),
        )
        processing_cases = service.filter_and_sort(
            snapshot.cases,
            DashboardFilters(stage=PROCESSING_FILTER),
        )
        counts = service.stage_counts(snapshot.cases)

        self.assertEqual(
            [case.case_no for case in pending_cases],
            ["PENDING-001"],
        )
        self.assertEqual(
            [case.case_no for case in processing_cases],
            ["PROCESSING-001", "ONSITE-001"],
        )
        self.assertEqual(counts["待處理"], 1)
        self.assertEqual(counts["處理中"], 2)
        self.assertEqual(counts["已結案"], 1)
        self.assertEqual(counts["全部"], 4)
        self.assertEqual(
            counts["全部"],
            counts["待處理"] + counts["處理中"] + counts["已結案"],
        )

    def _load_single_case(
        self,
        values: dict[str, object],
    ):
        row = self._base_row()
        row.update(values)
        service = CaseService(StubCaseRepository(rows=(row,)))
        return service.load_snapshot(
            now=datetime(2026, 7, 29, 14, 0, tzinfo=TAIPEI)
        ).cases[0]

    @staticmethod
    def _base_row() -> dict[str, object]:
        return {
            "CASE_NO": "A260729-001",
            "CREATED_AT": "2026-07-29 10:33:00",
            "PART_NO": "759220D130",
            "QTY": "4",
            "SITUATION": "地上撿到",
            "STAGE": "待處理",
            "FLOOR": "2F",
            "LAYER": "中",
        }
