"""逾期判斷測試。"""

from datetime import datetime, time
from unittest import TestCase
from unittest.mock import patch
from zoneinfo import ZoneInfo

from config.overdue_rules import OverdueRule, OverdueStatus
import services.overdue_service as overdue_service

TAIPEI = ZoneInfo("Asia/Taipei")


class OverdueServiceTest(TestCase):
    def setUp(self) -> None:
        rule = OverdueRule(
            warning_after_business_days=1,
            overdue_after_business_days=3,
            cutoff_time=time(17, 0),
        )
        self.rule_patch = patch.object(
            overdue_service,
            "get_overdue_rule",
            return_value=rule,
        )
        self.rule_patch.start()

    def tearDown(self) -> None:
        self.rule_patch.stop()

    def test_d1_warning_and_d3_overdue_skip_weekend(self) -> None:
        created_at = datetime(2026, 7, 30, 14, 0, tzinfo=TAIPEI)

        self.assertEqual(
            overdue_service.determine_overdue_status(
                created_at,
                datetime(2026, 7, 31, 16, 59, tzinfo=TAIPEI),
                "測試",
            ),
            OverdueStatus.NORMAL,
        )
        self.assertEqual(
            overdue_service.determine_overdue_status(
                created_at,
                datetime(2026, 7, 31, 17, 0, tzinfo=TAIPEI),
                "測試",
            ),
            OverdueStatus.WARNING,
        )
        self.assertEqual(
            overdue_service.determine_overdue_status(
                created_at,
                datetime(2026, 8, 4, 17, 0, tzinfo=TAIPEI),
                "測試",
            ),
            OverdueStatus.OVERDUE,
        )

    def test_after_cutoff_uses_next_business_day_as_d0(self) -> None:
        created_at = datetime(2026, 7, 31, 18, 0, tzinfo=TAIPEI)

        deadline = overdue_service.calculate_business_deadline(
            created_at=created_at,
            business_days=3,
            rule=overdue_service.get_overdue_rule("測試"),
        )

        self.assertEqual(
            deadline,
            datetime(2026, 8, 6, 17, 0, tzinfo=TAIPEI),
        )

    def test_taiwan_public_holidays_are_skipped(self) -> None:
        rule = overdue_service.get_overdue_rule("測試")
        created_at = datetime(2026, 9, 24, 14, 0, tzinfo=TAIPEI)

        deadline = overdue_service.calculate_business_deadline(
            created_at=created_at,
            business_days=3,
            rule=rule,
        )

        self.assertEqual(
            deadline,
            datetime(2026, 10, 1, 17, 0, tzinfo=TAIPEI),
        )

    def test_weekend_is_not_a_business_day(self) -> None:
        rule = overdue_service.get_overdue_rule("測試")

        self.assertFalse(
            overdue_service.is_business_day(
                datetime(2026, 8, 1).date(),
                rule,
            )
        )
