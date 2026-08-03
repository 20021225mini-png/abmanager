"""從公開 Google Sheet CASE 工作表讀取案件資料。"""

from typing import Any
import time

import pandas as pd

from config import settings as app_settings
from config.columns import (
    ALL_SOURCE_COLUMNS,
    REQUIRED_SOURCE_COLUMNS,
    SOURCE_COLUMN_ALIASES,
)
from data.case_repository import CaseDataset, DataSourceError


_CASE_GOOGLE_SHEET_ID = "1MTPfTw0i-DWZbNzfXtKUOS56UI_xaedKIAzM9E7ecD4"
_DEFAULT_CASE_SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{_CASE_GOOGLE_SHEET_ID}"
    "/export?format=csv&gid=1219451878"
)
CASE_SHEET_CSV_URL = getattr(
    app_settings,
    "CASE_SHEET_CSV_URL",
    _DEFAULT_CASE_SHEET_CSV_URL,
)


class GoogleSheetCaseRepository:
    """公開 Google Sheet 的案件資料來源。"""

    def __init__(self, csv_url: str = CASE_SHEET_CSV_URL) -> None:
        self._csv_url = csv_url

    def load_cases(self) -> CaseDataset:
        """讀取 CASE 工作表，並將缺少欄位補為空值。"""
        try:
            csv_url = self._csv_url
            if csv_url.startswith(("http://", "https://")):
                separator = "&" if "?" in csv_url else "?"
                csv_url = f"{csv_url}{separator}_v11={time.time_ns()}"
            frame = pd.read_csv(csv_url, dtype=object)
        except Exception as exc:
            raise DataSourceError(f"CASE 工作表讀取失敗：{exc}") from exc

        frame.columns = [str(column).strip() for column in frame.columns]
        for canonical_name, aliases in SOURCE_COLUMN_ALIASES.items():
            if canonical_name in frame.columns:
                continue
            source_name = next(
                (alias for alias in aliases if alias in frame.columns),
                None,
            )
            if source_name is not None:
                frame[canonical_name] = frame[source_name]
        warnings: list[str] = []

        missing_required = [
            column for column in REQUIRED_SOURCE_COLUMNS if column not in frame.columns
        ]
        if missing_required:
            warnings.append(
                "CASE 工作表缺少必要欄位：" + "、".join(missing_required)
            )

        for column in ALL_SOURCE_COLUMNS:
            if column not in frame.columns:
                frame[column] = None

        normalized = frame.loc[:, ALL_SOURCE_COLUMNS].where(
            pd.notna(frame.loc[:, ALL_SOURCE_COLUMNS]),
            None,
        )
        rows: tuple[dict[str, Any], ...] = tuple(
            normalized.to_dict(orient="records")
        )
        return CaseDataset(rows=rows, warnings=tuple(warnings))
