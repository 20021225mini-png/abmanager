"""從獨立的公開 Google Sheet 讀取 SOP 程式表。"""

from typing import Any

import pandas as pd

from config import settings as app_settings
from data.sop_repository import SopDataset, SopDataSourceError


# 保留內建資料來源，避免 Streamlit Cloud 在部署更新期間暫時讀到舊版
# config/settings.py 時，因缺少 V10 新增常數而直接 ImportError。
_SOP_GOOGLE_SHEET_ID = "1sWFKUs2yDYKAyOTxPQeVqN6H9Ta00gq8VGOfzuoM_AM"
_DEFAULT_SOP_RULES_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{_SOP_GOOGLE_SHEET_ID}"
    "/gviz/tq?tqx=out:csv&sheet=CLASSIFICATION_RULES"
)
_DEFAULT_SOP_NODES_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{_SOP_GOOGLE_SHEET_ID}"
    "/gviz/tq?tqx=out:csv&sheet=SOP_NODES"
)
SOP_RULES_CSV_URL = getattr(
    app_settings,
    "SOP_RULES_CSV_URL",
    _DEFAULT_SOP_RULES_CSV_URL,
)
SOP_NODES_CSV_URL = getattr(
    app_settings,
    "SOP_NODES_CSV_URL",
    _DEFAULT_SOP_NODES_CSV_URL,
)


REQUIRED_RULE_COLUMNS: frozenset[str] = frozenset(
    {
        "classification_id",
        "report_scenario",
        "main_type",
        "sub_type",
        "display_type",
        "condition_text",
        "entry_node_id",
    }
)

REQUIRED_NODE_COLUMNS: frozenset[str] = frozenset(
    {
        "node_id",
        "sop_id",
        "step_no",
        "flow_name",
        "node_type",
        "instruction",
        "required_data",
        "option_order",
        "option_label",
        "next_type",
        "next_node_id",
        "end_result",
        "pending_confirmation",
    }
)


class GoogleSheetSopRepository:
    """獨立 Google Sheet 的 SOP 資料來源。"""

    def __init__(
        self,
        rules_csv_url: str = SOP_RULES_CSV_URL,
        nodes_csv_url: str = SOP_NODES_CSV_URL,
    ) -> None:
        self._rules_csv_url = rules_csv_url
        self._nodes_csv_url = nodes_csv_url

    def load_sop_data(self) -> SopDataset:
        """讀取兩張程式表並驗證必要欄位。"""
        rules = self._read_csv(self._rules_csv_url, "CLASSIFICATION_RULES")
        nodes = self._read_csv(self._nodes_csv_url, "SOP_NODES")

        self._validate_columns(
            frame=rules,
            required=REQUIRED_RULE_COLUMNS,
            sheet_name="CLASSIFICATION_RULES",
        )
        self._validate_columns(
            frame=nodes,
            required=REQUIRED_NODE_COLUMNS,
            sheet_name="SOP_NODES",
        )

        return SopDataset(
            rules=self._to_rows(rules),
            nodes=self._to_rows(nodes),
        )

    @staticmethod
    def _read_csv(csv_url: str, sheet_name: str) -> pd.DataFrame:
        try:
            frame = pd.read_csv(csv_url, dtype=object)
        except Exception as exc:
            raise SopDataSourceError(
                f"{sheet_name} 工作表讀取失敗：{exc}"
            ) from exc
        frame.columns = [str(column).strip() for column in frame.columns]
        return frame

    @staticmethod
    def _validate_columns(
        frame: pd.DataFrame,
        required: frozenset[str],
        sheet_name: str,
    ) -> None:
        missing = sorted(required - set(frame.columns))
        if missing:
            raise SopDataSourceError(
                f"{sheet_name} 缺少必要欄位：{'、'.join(missing)}"
            )

    @staticmethod
    def _to_rows(frame: pd.DataFrame) -> tuple[dict[str, Any], ...]:
        normalized = frame.where(pd.notna(frame), None)
        return tuple(normalized.to_dict(orient="records"))
