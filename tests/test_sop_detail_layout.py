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

    def test_styles_use_sop_left_summary_right_and_collapsible_sop(self) -> None:
        source = (
            Path(__file__).resolve().parents[1] / "ui" / "styles.py"
        ).read_text(encoding="utf-8")
        components = (
            Path(__file__).resolve().parents[1] / "ui" / "components.py"
        ).read_text(encoding="utf-8")

        self.assertIn("grid-template-columns: minmax(0, 3fr) minmax(320px, 2fr)", source)
        self.assertIn("grid-template-columns: repeat(2", source)
        self.assertIn(".summary-full", source)
        self.assertIn(".sop-scroll", source)
        self.assertIn('details class="sop-module"', components)
        self.assertIn("依案件既有異常類型自動顯示", components)

    def test_sop_panel_is_rendered_before_case_summary(self) -> None:
        components = (
            Path(__file__).resolve().parents[1] / "ui" / "components.py"
        ).read_text(encoding="utf-8")

        details_start = components.index("'<div class=\"case-details-layout\">'")
        details_end = components.index('"</div>"', details_start)
        details_source = components[details_start:details_end]
        self.assertLess(
            details_source.index("_sop_panel_html"),
            details_source.index("_case_summary_panel_html"),
        )

    def test_manual_judgement_workspace_is_not_rendered(self) -> None:
        dashboard = (
            Path(__file__).resolve().parents[1] / "ui" / "dashboard.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("render_judgement_workspace", dashboard)
        self.assertNotIn("from ui.judgement", dashboard)
        self.assertNotIn("from services.judgement_service", dashboard)
        self.assertIn("judgement_service: object | None = None", dashboard)
        self.assertIn("case_writer: object | None = None", dashboard)
        self.assertIn("ABMANAGER_DEPLOY_VERSION", dashboard)
