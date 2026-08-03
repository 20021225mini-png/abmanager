"""Apps Script CASE 寫回用戶端測試。"""

from unittest import TestCase
import json
from unittest.mock import Mock, patch

from data.apps_script_case_writer import AppsScriptCaseWriter
from data.case_writer import CaseJudgementUpdate, CaseWriteError


class AppsScriptCaseWriterTest(TestCase):
    @patch("data.apps_script_case_writer.urlopen")
    def test_success_sends_only_approved_case_fields(self, open_url: Mock) -> None:
        response = Mock()
        response.read.return_value = json.dumps({
            "ok": True,
            "case_no": "A001",
            "updated_at": "2026-08-03 15:00:00",
            "stage": "處理中",
        }).encode("utf-8")
        open_url.return_value.__enter__.return_value = response
        writer = AppsScriptCaseWriter("https://example.test/exec", "secret")

        result = writer.update_judgement(
            CaseJudgementUpdate(
                case_no="A001",
                classification_id="IN-08E",
                judgement_result="一筆成立、一筆未成立",
            )
        )

        request = open_url.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(
            set(payload),
            {
                "action",
                "token",
                "case_no",
                "classification_id",
                "judgement_result",
            },
        )
        self.assertEqual(payload["classification_id"], "IN-08E")
        self.assertEqual(result.stage, "處理中")

    @patch("data.apps_script_case_writer.urlopen")
    def test_api_error_is_shown_as_case_write_error(self, open_url: Mock) -> None:
        response = Mock()
        response.read.return_value = json.dumps({
            "ok": False,
            "message": "案件編號重複",
        }).encode("utf-8")
        open_url.return_value.__enter__.return_value = response
        writer = AppsScriptCaseWriter("https://example.test/exec", "secret")

        with self.assertRaisesRegex(CaseWriteError, "案件編號重複"):
            writer.update_judgement(
                CaseJudgementUpdate("A001", "IN-08E", "查詢完成")
            )
