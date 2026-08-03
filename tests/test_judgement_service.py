"""V11 中文分類候選與代碼保存邏輯測試。"""

from datetime import datetime
from unittest import TestCase

from config.overdue_rules import OverdueStatus
from services.judgement_service import JudgementService
from services.models import DashboardCase
from services.sop_models import SopCatalog


class JudgementServiceTest(TestCase):
    def setUp(self) -> None:
        self.catalog = SopCatalog(
            rules=(
                {
                    "classification_id": "IN-06",
                    "report_scenario": "",
                    "main_type": "轉台車",
                    "sub_type": "資料尚未轉入 WES",
                    "display_type": "資料尚未轉入 WES",
                    "condition_text": "系統資料待修復",
                    "entry_node_id": "SOP-COM-04-S01",
                },
                {
                    "classification_id": "IN-07",
                    "report_scenario": "",
                    "main_type": "轉台車",
                    "sub_type": "資料尚未轉入 WES",
                    "display_type": "資料尚未轉入 WES",
                    "condition_text": "台車仍有未完成任務",
                    "entry_node_id": "SOP-COM-04-S01",
                },
                {
                    "classification_id": "IN-08A",
                    "report_scenario": "上架完仍有剩餘",
                    "main_type": "數量異常",
                    "sub_type": "混料上錯／儲位數量不符",
                    "display_type": "混料上錯／儲位數量不符",
                    "condition_text": "盤點儲位數量不符",
                    "entry_node_id": "SOP-COM-11-S01",
                },
                {
                    "classification_id": "IN-08B",
                    "report_scenario": "上架完仍有剩餘",
                    "main_type": "數量異常",
                    "sub_type": "儲位數量皆正確／確認溢品",
                    "display_type": "儲位數量皆正確／確認溢品",
                    "condition_text": "全部相關儲位數量皆正確",
                    "entry_node_id": "SOP-COM-11-S01",
                },
                {
                    "classification_id": "IN-08C",
                    "report_scenario": "上架完仍有剩餘",
                    "main_type": "數量異常",
                    "sub_type": "系統數量未對上",
                    "display_type": "HOPES／WES 數量不一致，WES 查無資料",
                    "condition_text": "WES 查無該筆資料",
                    "entry_node_id": "SOP-COM-11-S01",
                },
                {
                    "classification_id": "IN-08D",
                    "report_scenario": "上架完仍有剩餘",
                    "main_type": "數量異常",
                    "sub_type": "包裝件疑似少開",
                    "display_type": "包裝件疑似少開",
                    "condition_text": "由開箱組查核",
                    "entry_node_id": "SOP-COM-11-S01",
                },
                {
                    "classification_id": "IN-08E",
                    "report_scenario": "上架完仍有剩餘",
                    "main_type": "數量異常",
                    "sub_type": "HOPES 暫存未結",
                    "display_type": "HOPES 暫存未結",
                    "condition_text": "HOPES 與 WES 數量正確且有暫存",
                    "entry_node_id": "SOP-COM-11-S01",
                },
            ),
            nodes=(),
        )
        self.service = JudgementService()

    def test_report_scenario_lists_all_five_remaining_part_outcomes(self) -> None:
        choices = self.service.build_choices(
            self._case("上架完仍有剩餘"),
            self.catalog,
        )

        self.assertEqual(
            [option.classification_id for option in choices.recommended],
            ["IN-08A", "IN-08B", "IN-08C", "IN-08D", "IN-08E"],
        )

    def test_shared_display_type_keeps_multiple_conditions_for_user_choice(self) -> None:
        choices = self.service.build_choices(
            self._case("資料尚未轉入 WES"),
            self.catalog,
        )

        self.assertEqual(
            [option.classification_id for option in choices.recommended],
            ["IN-06", "IN-07"],
        )
        self.assertIn("系統資料待修復", choices.recommended[0].label)

    def test_unknown_situation_still_exposes_complete_catalog(self) -> None:
        choices = self.service.build_choices(
            self._case("新情境"),
            self.catalog,
        )

        self.assertEqual(choices.recommended, ())
        self.assertEqual(len(choices.all_options), 7)

    @staticmethod
    def _case(abnormal_type: str) -> DashboardCase:
        return DashboardCase(
            case_no="A001",
            block="2F-A",
            part_no="P001",
            cart_no="C01",
            quantity="1",
            abnormal_type=abnormal_type,
            occurred_at_text="2026-08-03 10:00",
            current_stage="待處理",
            stage_nodes=(),
            on_site_instruction="未開放",
            waiting_time_text="00:30:00",
            waiting_seconds=1800,
            overdue_status=OverdueStatus.NORMAL,
            handler="",
            product_type="",
            location_text="",
            sop_text="",
            note="",
            classification_id="",
            case_judgement="",
            judgement_result="",
            actual_scenario="",
            data_errors=(),
            occurred_at=datetime(2026, 8, 3, 10, 0),
            is_completed=False,
            is_awaiting_shelving=False,
        )
