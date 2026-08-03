"""案件 D+1 警示與 D+3 工作日逾期規則。"""

from dataclasses import dataclass
from datetime import time
from enum import StrEnum


class OverdueStatus(StrEnum):
    """看板使用的逾期結果。"""

    NORMAL = "NORMAL"
    WARNING = "WARNING"
    OVERDUE = "OVERDUE"


@dataclass(frozen=True)
class OverdueRule:
    """工作日門檻與每日截止時間。"""

    warning_after_business_days: int | None
    overdue_after_business_days: int | None
    cutoff_time: time

# D+1 截止後進入警示，D+3 截止後判定逾期。
# 工作日依台灣週休二日與國定假日判斷。
# 每日截止時間可依實際下班或案件受理規則調整。
DEFAULT_OVERDUE_RULE = OverdueRule(
    warning_after_business_days=1,
    overdue_after_business_days=3,
    cutoff_time=time(hour=17, minute=0),
)

# 若不同異常類型要採不同門檻，可在此加入「異常類型: OverdueRule」。
OVERDUE_RULES_BY_ABNORMAL_TYPE: dict[str, OverdueRule] = {}
