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

    def test_stage_buttons_and_waiting_legend_share_second_row(self) -> None:
        dashboard = (
            Path(__file__).resolve().parents[1] / "ui" / "dashboard.py"
        ).read_text(encoding="utf-8")

        stage_function = dashboard[
            dashboard.index("def _render_stage_filter"):
            dashboard.index("def _render_search_and_filters")
        ]
        self.assertIn("stage_col, legend_col = st.columns", stage_function)
        self.assertIn("with stage_col:", stage_function)
        self.assertIn("with legend_col:", stage_function)
        self.assertIn("waiting-legend", stage_function)
        self.assertIn('selected_label = st.radio(', stage_function)
        self.assertIn('"案件階段"', stage_function)
        self.assertIn('label_visibility="collapsed"', stage_function)
        self.assertNotIn("title_col, options_col = st.columns", stage_function)
        self.assertNotIn("案件篩選", stage_function)
        self.assertNotIn(
            '<span class="secondary-control-title">等待時間</span>',
            stage_function,
        )
        self.assertIn(
            'waiting-legend-status overdue">逾期',
            stage_function,
        )
        self.assertIn("達 3 個工作日", stage_function)
        self.assertIn(
            'waiting-legend-status warning">警示',
            stage_function,
        )
        self.assertIn("達 1 個工作日", stage_function)
        self.assertIn(
            'waiting-legend-status normal">正常',
            stage_function,
        )
        self.assertIn("未滿 1 個工作日", stage_function)
        self.assertNotIn("<strong>", stage_function)

    def test_stage_filter_and_legend_use_compact_single_row_layout(self) -> None:
        styles = (
            Path(__file__).resolve().parents[1] / "ui" / "styles.py"
        ).read_text(encoding="utf-8")

        radio_rule = styles[
            styles.index('div[data-testid="stRadio"] {'):
            styles.index(".waiting-legend-item")
        ]
        self.assertIn("min-height: 34px", radio_rule)
        self.assertIn("display: flex", radio_rule)
        self.assertIn("align-items: center", radio_rule)
        self.assertIn("flex-wrap: nowrap", radio_rule)
        self.assertIn("gap: .7rem", radio_rule)

    def test_waiting_legend_and_completed_time_styles_are_clear(self) -> None:
        styles = (
            Path(__file__).resolve().parents[1] / "ui" / "styles.py"
        ).read_text(encoding="utf-8")

        self.assertIn("font-size: .94rem", styles)
        secondary_title_rule = styles[
            styles.index(".secondary-control-title"):
            styles.index(".waiting-legend-item")
        ]
        self.assertIn("font-size: .84rem", secondary_title_rule)
        self.assertIn("font-weight: 500", secondary_title_rule)
        legend_rule = styles[
            styles.index(".waiting-legend-status"):
            styles.index(".case-table-wrap")
        ]
        self.assertIn("min-width: 52px", legend_rule)
        self.assertIn("font-weight: 400", legend_rule)
        self.assertIn("background: #eef3f9", legend_rule)
        self.assertIn("background: #fff2cb", legend_rule)
        self.assertIn("background: #ffe2e2", legend_rule)
        completed_rule = styles[
            styles.index(".waiting-badge.completed"):
            styles.index(".stage-flow")
        ]
        self.assertIn("background: transparent", completed_rule)
        self.assertIn("font-weight: 800", completed_rule)
