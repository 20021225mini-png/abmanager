"""SOP 詳細列緊湊版內容測試。"""

from pathlib import Path
from unittest import TestCase


class SopDetailLayoutTest(TestCase):
    def test_components_include_requested_summary_fields(self) -> None:
        source = (
            Path(__file__).resolve().parents[1] / "ui" / "components.py"
        ).read_text(encoding="utf-8")

        for label in (
            "案件編號",
            "件號",
            "異常類型",
            "備註",
        ):
            with self.subTest(label=label):
                self.assertIn(label, source)

        self.assertNotIn('_summary_item_html("本案判定"', source)
        self.assertNotIn('_summary_item_html("判斷結果"', source)

    def test_styles_use_compact_summary_and_collapsible_sop(self) -> None:
        source = (
            Path(__file__).resolve().parents[1] / "ui" / "styles.py"
        ).read_text(encoding="utf-8")
        components = (
            Path(__file__).resolve().parents[1] / "ui" / "components.py"
        ).read_text(encoding="utf-8")

        self.assertIn("grid-template-columns: repeat(4", source)
        self.assertIn(".summary-half", source)
        self.assertIn(".sop-scroll", source)
        self.assertIn('details class="sop-module"', components)
        self.assertIn("依案件既有異常類型自動顯示", components)

    def test_manual_judgement_workspace_is_not_rendered(self) -> None:
        dashboard = (
            Path(__file__).resolve().parents[1] / "ui" / "dashboard.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("render_judgement_workspace", dashboard)
        self.assertIn("judgement_service: JudgementService | None = None", dashboard)
        self.assertIn("case_writer: CaseWriter | None = None", dashboard)
