"""案件逾期狀態判斷。"""

from datetime import date, datetime, timedelta
from functools import lru_cache

import holidays

from config.overdue_rules import (
    DEFAULT_OVERDUE_RULE,
    OVERDUE_RULES_BY_ABNORMAL_TYPE,
    OverdueRule,
    OverdueStatus,
)


def get_overdue_rule(abnormal_type: str) -> OverdueRule:
    """取得異常類型規則；未設定時使用預設規則。"""
    return OVERDUE_RULES_BY_ABNORMAL_TYPE.get(
        abnormal_type,
        DEFAULT_OVERDUE_RULE,
    )


@lru_cache(maxsize=8)
def _taiwan_public_holidays(year: int) -> holidays.HolidayBase:
    """取得指定年度的台灣國定假日與補假。"""
    return holidays.TW(years=year)


def is_business_day(day: date, rule: OverdueRule) -> bool:
    """依週休二日與台灣國定假日判斷是否為工作日。"""
    if day.weekday() >= 5:
        return False
    return day not in _taiwan_public_holidays(day.year)


def next_business_day(day: date, rule: OverdueRule) -> date:
    """取得指定日期之後的下一個工作日。"""
    candidate = day + timedelta(days=1)
    while not is_business_day(candidate, rule):
        candidate += timedelta(days=1)
    return candidate


def add_business_days(
    start_day: date,
    business_days: int,
    rule: OverdueRule,
) -> date:
    """從起算日之後開始累加指定工作日數。"""
    if business_days < 0:
        raise ValueError("business_days 不可小於 0")

    result = start_day
    for _ in range(business_days):
        result = next_business_day(result, rule)
    return result


def get_acceptance_day(created_at: datetime, rule: OverdueRule) -> date:
    """取得案件期限的起算工作日。

    工作日截止時間內建立，以當日為 D0；非工作日或截止時間後建立，
    以下一個工作日為 D0。
    """
    created_day = created_at.date()
    created_time = created_at.timetz().replace(tzinfo=None)
    if (
        not is_business_day(created_day, rule)
        or created_time > rule.cutoff_time
    ):
        return next_business_day(created_day, rule)
    return created_day


def calculate_business_deadline(
    created_at: datetime,
    business_days: int | None,
    rule: OverdueRule,
) -> datetime | None:
    """計算 D+n 工作日的截止時間。"""
    if business_days is None:
        return None

    acceptance_day = get_acceptance_day(created_at, rule)
    deadline_day = add_business_days(
        start_day=acceptance_day,
        business_days=business_days,
        rule=rule,
    )
    return datetime.combine(
        deadline_day,
        rule.cutoff_time,
        tzinfo=created_at.tzinfo,
    )


def determine_overdue_status(
    created_at: datetime | None,
    evaluated_at: datetime | None,
    abnormal_type: str,
) -> OverdueStatus:
    """依 D+1／D+3 工作日截止時間回傳案件狀態。"""
    if created_at is None or evaluated_at is None:
        return OverdueStatus.NORMAL

    rule = get_overdue_rule(abnormal_type)
    warning_at = calculate_business_deadline(
        created_at=created_at,
        business_days=rule.warning_after_business_days,
        rule=rule,
    )
    overdue_at = calculate_business_deadline(
        created_at=created_at,
        business_days=rule.overdue_after_business_days,
        rule=rule,
    )

    if overdue_at is not None and evaluated_at >= overdue_at:
        return OverdueStatus.OVERDUE
    if warning_at is not None and evaluated_at >= warning_at:
        return OverdueStatus.WARNING
    return OverdueStatus.NORMAL
