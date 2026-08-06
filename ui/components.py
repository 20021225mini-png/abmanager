"""看板 UI 元件。"""

from html import escape
from typing import Sequence

import streamlit as st

from config.overdue_rules import OverdueStatus
from config.texts import COMPLETION_TIME_MISSING_TEXT, DATA_ERROR_TEXT
from services.models import DashboardCase, StageNode
from services.sop_models import CaseSopDetail, SopCatalog, SopModule, SopStep
from services.sop_service import SopService


def render_case_table(
    cases: Sequence[DashboardCase],
    sop_service: SopService,
    sop_catalog: SopCatalog | None,
    sop_error: str = "",
) -> None:
    """顯示雙層表頭、案件列與可展開說明。"""
    rows: list[str] = []
    for case in cases:
        if sop_catalog is None:
            sop_detail = CaseSopDetail(
                case_judgement=case.case_judgement or case.abnormal_type,
                actual_scenario=case.actual_scenario or case.abnormal_type,
                mapping_message=(
                    f"SOP 資料讀取失敗：{sop_error}"
                    if sop_error
                    else "SOP 資料目前無法讀取。"
                ),
            )
        else:
            sop_detail = sop_service.build_case_detail(
                case=case,
                catalog=sop_catalog,
            )
        rows.append(_case_row_html(case, sop_detail))

    body = "".join(rows)
    if not body:
        body = '<div class="empty-state">目前沒有符合篩選條件的案件</div>'

    table_html = (
        '<div class="case-table-wrap">'
        '<div class="case-table">'
        '<div class="case-group-header">'
        '<div class="group-title group-info">異常零件資訊</div>'
        '<div class="group-title group-progress">處理進度</div>'
        '<div class="group-title group-state">處理情形</div>'
        "</div>"
        '<div class="case-column-header">'
        "<span>區塊</span>"
        "<span>件號</span>"
        "<span>台車號</span>"
        "<span>數量</span>"
        "<span>異常類型</span>"
        "<span>異常發生時間</span>"
        "<span>前處理</span>"
        "<span>現場處理指示</span>"
        "<span>等待時間</span>"
        "<span>處理人員</span>"
        "</div>"
        f"{body}"
        "</div>"
        "</div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


def _case_row_html(case: DashboardCase, sop_detail: CaseSopDetail) -> str:
    status_class = {
        OverdueStatus.NORMAL: "normal",
        OverdueStatus.WARNING: "warning",
        OverdueStatus.OVERDUE: "overdue",
    }[case.overdue_status]
    waiting_title = "數字為實際經過時間；底色依 D+1／D+3 工作日判斷"
    if case.is_completed:
        status_class = "completed"
        waiting_title = "已結案案件以實際完成時間計算"
        if case.waiting_time_text == COMPLETION_TIME_MISSING_TEXT:
            waiting_title = "案件已結案，但完成時間欄位待補"
    if case.waiting_time_text == DATA_ERROR_TEXT:
        status_class = "error"
        waiting_title = "等待時間資料格式錯誤"

    errors = ""
    if case.data_errors:
        error_text = "；".join(escape(error) for error in case.data_errors)
        errors = f'<div class="data-errors">{error_text}</div>'

    return (
        '<details class="case-row">'
        f'<summary class="case-summary" aria-label="展開案件 {escape(case.case_no)}">'
        f'<span class="case-no">{escape(case.block)}</span>'
        f"<span>{escape(case.part_no)}</span>"
        f"<span>{escape(case.cart_no)}</span>"
        f"<span>{escape(case.quantity)}</span>"
        f'<span>{_badge_html("abnormal-badge", case.abnormal_type)}</span>'
        f"<span>{escape(case.occurred_at_text)}</span>"
        f"<span>{_stage_flow_html(case.stage_nodes)}</span>"
        f'<span>{_badge_html("instruction-badge", case.on_site_instruction)}</span>'
        f'<span><span class="waiting-badge {status_class}" '
        f'title="{waiting_title}">'
        f"{escape(case.waiting_time_text)}</span></span>"
        f"<span>{escape(case.handler)}</span>"
        "</summary>"
        '<div class="case-details-layout">'
        f"{_sop_panel_html(sop_detail)}"
        f"{_case_summary_panel_html(case, sop_detail)}"
        "</div>"
        f"{errors}"
        "</details>"
    )


def _stage_flow_html(nodes: Sequence[StageNode]) -> str:
    node_html = "".join(
        (
            f'<span class="stage-node {escape(node.state)}">'
            '<span class="stage-dot"></span>'
            f"<span>{escape(node.label)}</span>"
            "</span>"
        )
        for node in nodes
    )
    return f'<span class="stage-flow">{node_html}</span>'


def _badge_html(css_class: str, value: str) -> str:
    """有資料才顯示標籤；缺值欄位維持空白。"""
    if not value:
        return ""
    return f'<span class="{css_class}">{escape(value)}</span>'


def _sop_panel_html(detail: CaseSopDetail) -> str:
    if detail.modules:
        step_count = sum(len(module.steps) for module in detail.modules)
        modules = "".join(
            _sop_module_html(index=index, module=module)
            for index, module in enumerate(detail.modules, start=1)
        )
        route_summary = (
            '<div class="sop-route-summary">'
            '<span>本案處理 SOP</span>'
            f'<strong>{len(detail.modules)} 個模組／{step_count} 個步驟</strong>'
            '<small>依案件既有異常類型自動顯示，請按順序查看</small>'
            "</div>"
        )
    else:
        modules = '<div class="sop-empty">目前找不到可顯示的處理 SOP</div>'
        route_summary = ""

    message = ""
    if detail.mapping_message:
        displayed_message = _mapping_message_for_display(detail)
        message = (
            '<div class="sop-message">'
            f"{escape(displayed_message)}"
            "</div>"
        )

    return (
        '<section class="detail-panel sop-panel">'
        '<div class="detail-panel-title" role="heading" aria-level="2">處理 SOP</div>'
        f"{route_summary}"
        '<div class="sop-scroll">'
        f"{modules}"
        "</div>"
        f"{message}"
        "</section>"
    )


def _sop_module_html(index: int, module: SopModule) -> str:
    steps = "".join(_sop_step_html(step) for step in module.steps)
    opened = " open" if index == 1 else ""
    return (
        f'<details class="sop-module"{opened}>'
        '<summary class="sop-module-heading">'
        '<span class="sop-module-title">'
        f'<span class="sop-module-index">{index}</span>'
        '<span class="sop-module-copy">'
        f'<strong>{escape(module.flow_name)}</strong>'
        f'<small>{escape(module.sop_id)}／{len(module.steps)} 個步驟</small>'
        "</span></span>"
        '<span class="sop-module-toggle">展開</span>'
        "</summary>"
        f'<div class="sop-steps">{steps}</div>'
        "</details>"
    )


def _sop_step_html(step: SopStep) -> str:
    required_data = ""
    if step.required_data:
        required_data = (
            '<div class="sop-required">'
            '<span>所需資料</span>'
            f"{escape(step.required_data)}"
            "</div>"
        )

    branches = ""
    if step.branches:
        branch_rows = "".join(
            (
                '<div class="sop-branch">'
                f'<span>若 <strong>{escape(branch.label)}</strong></span>'
                f'<span class="branch-arrow">→</span>'
                f'<span>{escape(branch.destination)}</span>'
                "</div>"
            )
            for branch in step.branches
        )
        branches = f'<div class="sop-branches">{branch_rows}</div>'

    result = ""
    if step.result:
        result = f'<div class="sop-result">{escape(step.result)}</div>'

    notice = ""
    if step.notice:
        notice = f'<div class="sop-notice">{escape(step.notice)}</div>'

    return (
        '<div class="sop-step">'
        '<div class="sop-step-head">'
        f'<span class="sop-step-number">步驟 {escape(step.step_no)}</span>'
        f'<span class="sop-instruction">{escape(step.instruction)}</span>'
        "</div>"
        f"{required_data}{branches}{result}{notice}"
        "</div>"
    )


def _case_summary_panel_html(
    case: DashboardCase,
    detail: CaseSopDetail,
) -> str:
    _ = detail
    items = "".join(
        (
            _summary_item_html("案件編號", case.case_no),
            _summary_item_html("件號", case.part_no),
            _summary_item_html("異常類型", case.abnormal_type),
            _summary_item_html("備註", case.note, span="full"),
        )
    )
    return (
        '<aside class="detail-panel case-summary-panel">'
        '<div class="detail-panel-title" role="heading" aria-level="2">案件摘要</div>'
        f'<div class="summary-grid">{items}</div>'
        "</aside>"
    )


def _summary_item_html(label: str, value: str, span: str = "") -> str:
    css_class = "summary-item"
    if span:
        css_class += f" summary-{span}"
    displayed_value = value or "尚未填寫"
    return (
        f'<div class="{css_class}">'
        f'<span class="summary-label">{escape(label)}</span>'
        f'<span class="summary-value">{escape(displayed_value)}</span>'
        "</div>"
    )


def _mapping_message_for_display(detail: CaseSopDetail) -> str:
    """將資料層的分類維護提示轉為現場可理解的查閱訊息。"""
    message = detail.mapping_message
    if "classification_id" not in message.casefold() and "CASE 補入" not in message:
        return message
    if detail.modules:
        return "已依案件異常類型顯示共用 SOP，請依實際情況查看對應分支。"
    return "目前案件資訊可對應多條 SOP，請依異常類型與現場情況確認適用流程。"
