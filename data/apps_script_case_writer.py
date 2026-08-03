"""透過 Google Apps Script Web App 寫回 CASE 工作表。"""

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from data.case_writer import (
    CaseJudgementUpdate,
    CaseWriteError,
    CaseWriteResult,
)


class AppsScriptCaseWriter:
    """將 V11 的判定更新送到既有 Apps Script 後台。"""

    def __init__(
        self,
        endpoint_url: str,
        api_token: str,
        timeout_seconds: float = 15.0,
    ) -> None:
        self._endpoint_url = endpoint_url.strip()
        self._api_token = api_token.strip()
        self._timeout_seconds = timeout_seconds

    def update_judgement(
        self,
        update: CaseJudgementUpdate,
    ) -> CaseWriteResult:
        payload = {
            "action": "update_case_judgement",
            "token": self._api_token,
            "case_no": update.case_no,
            "classification_id": update.classification_id,
            "judgement_result": update.judgement_result,
        }
        request = Request(
            self._endpoint_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urlopen(
                request,
                timeout=self._timeout_seconds,
            ) as response:
                body: dict[str, Any] = json.loads(
                    response.read().decode("utf-8")
                )
        except (HTTPError, URLError, TimeoutError) as exc:
            raise CaseWriteError(f"寫回服務連線失敗：{exc}") from exc
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            raise CaseWriteError("寫回服務回傳格式錯誤。") from exc

        if not body.get("ok"):
            message = str(body.get("message") or "案件寫回失敗。")
            raise CaseWriteError(message)

        return CaseWriteResult(
            case_no=str(body.get("case_no") or update.case_no),
            updated_at=str(body.get("updated_at") or ""),
            stage=str(body.get("stage") or ""),
        )
