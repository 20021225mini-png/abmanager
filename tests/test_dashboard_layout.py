"""看板控制列順序與狀態按鈕測試。"""

import ast
from pathlib import Path
from unittest import TestCase

from config.texts import STAGE_FILTER_ORDER


class DashboardLayoutTest(TestCase):
    def test_search_filters_are_rendered_before_stage_buttons(self) -> None:
        dashboard_path = (
            Path(__file__).resolve().parents[1] / "ui" / "dashboard.py"
        )
        tree = ast.parse(dashboard_path.read_text(encoding="utf-8"))
        call_lines: dict[str, int] = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name):
                continue
            if node.func.id not in {
                "_render_search_and_filters",
                "_render_stage_filter",
            }:
                continue
            call_lines[node.func.id] = min(
                call_lines.get(node.func.id, node.lineno),
                node.lineno,
            )

        self.assertLess(
            call_lines["_render_search_and_filters"],
            call_lines["_render_stage_filter"],
        )

    def test_stage_buttons_use_four_lifecycle_groups(self) -> None:
        self.assertEqual(
            STAGE_FILTER_ORDER,
            ("全部", "待處理", "處理中", "已結案"),
        )
