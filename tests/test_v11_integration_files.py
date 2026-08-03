"""V11 畫面、Apps Script 與設定檔的靜態整合檢查。"""

from pathlib import Path
from unittest import TestCase


class V11IntegrationFilesTest(TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]

    def test_judgement_ui_contains_required_inputs_and_save_action(self) -> None:
        source = (self.root / "ui" / "judgement.py").read_text(
            encoding="utf-8"
        )
        for text in (
            "案件判定與寫回",
            "本案判定",
            "本案實際判斷結果",
            "儲存判定",
        ):
            self.assertIn(text, source)

    def test_apps_script_updates_only_expected_case_columns(self) -> None:
        source = (self.root / "gas" / "CaseJudgementApi.gs").read_text(
            encoding="utf-8"
        )
        for header in (
            "CASE_NO",
            "UPDATED_AT",
            "STAGE",
            "CLASSIFICATION_ID",
            "JUDGEMENT_RESULT",
        ):
            self.assertIn(header, source)
        self.assertIn("CASE_API_TOKEN", source)

    def test_v10_import_failure_is_documented(self) -> None:
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("SOP_NODES_CSV_URL", readme)
        self.assertIn("與 CASE 新增欄位無關", readme)
