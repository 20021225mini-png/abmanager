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
            "備註",
            "本案判定",
            "主類型",
            "判斷結果",
        ):
            with self.subTest(label=label):
                self.assertIn(label, source)

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
        self.assertIn("先依第一個模組判斷", components)
