"""SOP 詳細列左右欄內容測試。"""

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
            "實際情境",
            "判定條件",
            "判斷結果",
        ):
            with self.subTest(label=label):
                self.assertIn(label, source)

    def test_styles_use_left_sop_and_right_summary_columns(self) -> None:
        source = (
            Path(__file__).resolve().parents[1] / "ui" / "styles.py"
        ).read_text(encoding="utf-8")

        self.assertIn("grid-template-columns: minmax(0, 1.65fr)", source)
        self.assertIn(".sop-scroll", source)
        self.assertIn(".summary-grid", source)
