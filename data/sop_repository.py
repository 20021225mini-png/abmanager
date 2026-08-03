"""SOP 分類規則與步驟資料來源介面。"""

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class SopDataset:
    """兩張 SOP 程式表的讀取結果。"""

    rules: tuple[Mapping[str, Any], ...]
    nodes: tuple[Mapping[str, Any], ...]
    warnings: tuple[str, ...] = ()


class SopRepository(Protocol):
    """SOP 資料來源需實作的介面。"""

    def load_sop_data(self) -> SopDataset:
        """讀取分類規則與 SOP 節點。"""


class SopDataSourceError(RuntimeError):
    """SOP 資料來源無法讀取或欄位不完整。"""
