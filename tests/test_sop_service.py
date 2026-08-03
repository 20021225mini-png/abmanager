"""SOP 分類比對與跨模組路徑測試。"""

from datetime import datetime
from unittest import TestCase

from config.overdue_rules import OverdueStatus
from data.sop_repository import SopDataset
from services.models import DashboardCase
from services.sop_service import SopService


class StubSopRepository:
    def __init__(
        self,
        rules: tuple[dict[str, object], ...],
        nodes: tuple[dict[str, object], ...],
    ) -> None:
        self._dataset = SopDataset(rules=rules, nodes=nodes)

    def load_sop_data(self) -> SopDataset:
        return self._dataset


class SopServiceTest(TestCase):
    def setUp(self) -> None:
        rules = (
            {
                "classification_id": "IN-10",
                "report_scenario": "地上撿到",
                "main_type": "其他",
                "sub_type": "地上撿到",
                "display_type": "地上撿到",
                "condition_text": "確認零件可用性後分流",
                "entry_node_id": "SOP-01-S01",
            },
            {
                "classification_id": "IN-06",
                "report_scenario": "",
                "main_type": "轉台車",
                "sub_type": "資料尚未轉入 WES",
                "display_type": "資料尚未轉入 WES",
                "condition_text": "系統資料待修復",
                "entry_node_id": "SOP-02-S01",
            },
            {
                "classification_id": "IN-07",
                "report_scenario": "",
                "main_type": "轉台車",
                "sub_type": "資料尚未轉入 WES",
                "display_type": "資料尚未轉入 WES",
                "condition_text": "台車仍有未完成任務",
                "entry_node_id": "SOP-02-S01",
            },
        )
        nodes = (
            self._node(
                node_id="SOP-01-S01",
                sop_id="SOP-01",
                step_no="1",
                flow_name="可用性確認",
                instruction="確認零件是否可正常使用",
                node_type="DECISION",
                option_order="1",
                option_label="可用",
                next_type="SOP",
                next_node_id="SOP-03-S01",
            ),
            self._node(
                node_id="SOP-01-S01",
                sop_id="SOP-01",
                step_no="1",
                flow_name="可用性確認",
                instruction="確認零件是否可正常使用",
                node_type="DECISION",
                option_order="2",
                option_label="不可用",
                next_type="END",
                end_result="確認溢品並結案",
            ),
            self._node(
                node_id="SOP-03-S01",
                sop_id="SOP-03",
                step_no="1",
                flow_name="補上架",
                instruction="執行補上架",
                node_type="TERMINAL",
                end_result="補上架完成",
            ),
            self._node(
                node_id="SOP-02-S01",
                sop_id="SOP-02",
                step_no="1",
                flow_name="資料修復",
                instruction="請資訊部修正資料",
                node_type="TERMINAL",
                end_result="資料修復完成",
            ),
        )
        self.service = SopService(StubSopRepository(rules, nodes))
        self.catalog = self.service.load_catalog()

    def test_classification_id_builds_cross_module_sop(self) -> None:
        case = self._case(
            abnormal_type="地上撿到",
            classification_id="IN-10",
        )

        detail = self.service.build_case_detail(case, self.catalog)

        self.assertEqual(
            [module.flow_name for module in detail.modules],
            ["可用性確認", "補上架"],
        )
        self.assertEqual(detail.main_type, "其他")
        self.assertEqual(detail.case_judgement, "地上撿到")
        self.assertEqual(
            detail.modules[0].steps[0].branches[0].destination,
            "進入「補上架」",
        )

    def test_same_entry_node_keeps_shared_sop_without_guessing_condition(self) -> None:
        case = self._case(abnormal_type="資料尚未轉入 WES")

        detail = self.service.build_case_detail(case, self.catalog)

        self.assertEqual(
            [module.flow_name for module in detail.modules],
            ["資料修復"],
        )
        self.assertEqual(detail.main_type, "轉台車")
        self.assertEqual(detail.condition_text, "")
        self.assertIn("共用 SOP", detail.mapping_message)

    def test_unknown_case_shows_mapping_message(self) -> None:
        detail = self.service.build_case_detail(
            self._case(abnormal_type="尚未定義"),
            self.catalog,
        )

        self.assertEqual(detail.modules, ())
        self.assertIn("找不到對應", detail.mapping_message)

    @staticmethod
    def _case(
        abnormal_type: str,
        classification_id: str = "",
    ) -> DashboardCase:
        return DashboardCase(
            case_no="A260803-001",
            block="2F-中",
            part_no="759220D130",
            cart_no="AS047",
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
            note="測試備註",
            classification_id=classification_id,
            case_judgement="",
            judgement_result="",
            actual_scenario="",
            data_errors=(),
            occurred_at=datetime(2026, 8, 3, 10, 0),
            is_completed=False,
            is_awaiting_shelving=False,
        )

    @staticmethod
    def _node(**values: object) -> dict[str, object]:
        row: dict[str, object] = {
            "node_id": "",
            "sop_id": "",
            "step_no": "",
            "flow_name": "",
            "node_type": "ACTION",
            "instruction": "",
            "required_data": "",
            "option_order": "1",
            "option_label": "下一步",
            "next_type": "",
            "next_node_id": "",
            "end_result": "",
            "pending_confirmation": "",
        }
        row.update(values)
        return row
