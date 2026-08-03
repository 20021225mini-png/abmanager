"""V11 寫回介面的執行環境設定。"""

from collections.abc import Mapping
from dataclasses import dataclass
import os
from typing import Any


@dataclass(frozen=True)
class CaseWriteSettings:
    """Apps Script 寫回網址與共用驗證碼。"""

    endpoint_url: str = ""
    api_token: str = ""

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint_url and self.api_token)


def load_case_write_settings(
    secret_source: Mapping[str, Any] | None = None,
) -> CaseWriteSettings:
    """先讀環境變數，再讀 Streamlit secrets 的同名設定。"""
    endpoint_url = os.getenv("CASE_WRITE_API_URL", "").strip()
    api_token = os.getenv("CASE_WRITE_API_TOKEN", "").strip()

    if secret_source is not None:
        if not endpoint_url:
            endpoint_url = _secret_text(secret_source, "CASE_WRITE_API_URL")
        if not api_token:
            api_token = _secret_text(secret_source, "CASE_WRITE_API_TOKEN")

    return CaseWriteSettings(
        endpoint_url=endpoint_url,
        api_token=api_token,
    )


def _secret_text(source: Mapping[str, Any], key: str) -> str:
    try:
        value = source.get(key, "")
    except Exception:
        return ""
    return str(value).strip() if value is not None else ""
