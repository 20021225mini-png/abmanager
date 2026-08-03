"""案件判定寫回介面與資料模型。"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CaseJudgementUpdate:
    """看板送往 CASE 工作表的一次判定更新。"""

    case_no: str
    classification_id: str
    judgement_result: str


@dataclass(frozen=True)
class CaseWriteResult:
    """寫回成功後回傳的案件狀態。"""

    case_no: str
    updated_at: str
    stage: str


class CaseWriter(Protocol):
    """案件寫回來源需實作的介面。"""

    def update_judgement(
        self,
        update: CaseJudgementUpdate,
    ) -> CaseWriteResult:
        """更新分類編號與每案判斷結果。"""


class CaseWriteError(RuntimeError):
    """案件無法安全寫回時使用的例外。"""
