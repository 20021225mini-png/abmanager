"""V11 寫回設定載入測試。"""

import os
from unittest import TestCase
from unittest.mock import patch

from config.writeback import load_case_write_settings


class WritebackSettingsTest(TestCase):
    def test_streamlit_secrets_enable_writer(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = load_case_write_settings(
                {
                    "CASE_WRITE_API_URL": "https://example.test/exec",
                    "CASE_WRITE_API_TOKEN": "secret",
                }
            )

        self.assertTrue(settings.is_configured)

    def test_partial_settings_keep_writer_disabled(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = load_case_write_settings(
                {"CASE_WRITE_API_URL": "https://example.test/exec"}
            )

        self.assertFalse(settings.is_configured)
