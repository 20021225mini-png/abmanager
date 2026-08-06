"""等待時間測試。"""

from datetime import datetime
from unittest import TestCase
from zoneinfo import ZoneInfo

from services.waiting_time_service import (
    calculate_waiting_time,
    format_elapsed_time,
)

TAIPEI = ZoneInfo("Asia/Taipei")


class WaitingTimeServiceTest(TestCase):
    def test_elapsed_time_can_exceed_24_hours(self) -> None:
        self.assertEqual(
            format_elapsed_time(51 * 3600 + 30 * 60 + 25),
            "2天 03時",
        )

    def test_elapsed_time_under_24_hours_uses_chinese_units(self) -> None:
        self.assertEqual(
            format_elapsed_time(23 * 3600 + 59 * 60 + 59),
            "23時 59分",
        )

    def test_exactly_24_hours_starts_day_format(self) -> None:
        self.assertEqual(format_elapsed_time(24 * 3600), "1天 00時")

    def test_open_case_uses_current_time(self) -> None:
        result = calculate_waiting_time(
            created_at_value="2026-07-27 10:00:00",
            now=datetime(2026, 7, 29, 13, 30, 25, tzinfo=TAIPEI),
        )
        self.assertEqual(result.display_text, "2天 03時")

    def test_closed_case_uses_closed_at(self) -> None:
        result = calculate_waiting_time(
            created_at_value="2026-07-27 10:00:00",
            closed_at_value="2026-07-27 12:30:25",
        )
        self.assertEqual(result.display_text, "02時 30分")

    def test_invalid_created_at_does_not_raise(self) -> None:
        result = calculate_waiting_time(created_at_value="錯誤時間")
        self.assertEqual(result.display_text, "資料錯誤")
        self.assertEqual(result.error, "CREATED_AT 缺少或格式錯誤")

    def test_completion_field_name_is_used_in_error(self) -> None:
        result = calculate_waiting_time(
            created_at_value="2026-07-27 10:00:00",
            closed_at_value="錯誤時間",
            completion_field_name="SHELVING_COMPLETED_AT",
        )
        self.assertEqual(
            result.error,
            "SHELVING_COMPLETED_AT 格式錯誤",
        )
