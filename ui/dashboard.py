"""Streamlit 看板主畫面。"""

from typing import Sequence

import streamlit as st

from config import settings as app_settings
from config.texts import (
    APP_TITLE,
    OVERDUE_FILTER_LABELS,
    SORT_OPTIONS,
    STAGE_FILTER_ORDER,
)
from services.case_service import CaseService, DashboardLoadError
from services.models import DashboardCase, DashboardFilters, DashboardSnapshot
from services.sop_models import SopCatalog
from services.sop_service import SopLoadError, SopService
from ui.components import render_case_table
from ui.styles import DASHBOARD_CSS


CACHE_TTL_SECONDS = getattr(app_settings, "CACHE_TTL_SECONDS", 60)
SOP_CACHE_TTL_SECONDS = getattr(app_settings, "SOP_CACHE_TTL_SECONDS", 300)
PAGE_TITLE = getattr(
    app_settings,
    "PAGE_TITLE",
    "進出異常案件 Follow 看板",
)
PAGE_LAYOUT = getattr(app_settings, "PAGE_LAYOUT", "wide")
DEPLOY_VERSION = "V11.11-COMPACT-CONTROL-ROW-LOCAL"

# 顯示於 Streamlit Manage app 紀錄，方便確認實際部署版本。
print(f"ABMANAGER_DEPLOY_VERSION={DEPLOY_VERSION}")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def _load_snapshot(_case_service: CaseService) -> DashboardSnapshot:
    """透過服務層取得資料；UI 不直接接觸 Excel 或 Google Sheet。"""
    return _case_service.load_snapshot()


@st.cache_data(ttl=SOP_CACHE_TTL_SECONDS, show_spinner=False)
def _load_sop_catalog(_sop_service: SopService) -> SopCatalog:
    """SOP 每五分鐘更新一次，與 CASE 的分鐘級更新分開。"""
    return _sop_service.load_catalog()


def render_dashboard(
    case_service: CaseService,
    sop_service: SopService,
    judgement_service: object | None = None,
    case_writer: object | None = None,
) -> None:
    """顯示現場查閱看板；保留舊參數以維持 V11 啟動接線相容。"""
    _ = judgement_service, case_writer
    st.set_page_config(
        page_title=PAGE_TITLE,
        layout=PAGE_LAYOUT,
    )
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.markdown(f'<h1 class="dashboard-title">{APP_TITLE}</h1>', unsafe_allow_html=True)

    try:
        snapshot = _load_snapshot(case_service)
    except DashboardLoadError as exc:
        st.error(str(exc))
        st.info("請確認 CASE 工作表為可檢視，且欄位名稱與設定一致。")
        return

    for warning in snapshot.source_warnings:
        st.warning(warning)

    sop_catalog: SopCatalog | None = None
    sop_error = ""
    try:
        sop_catalog = _load_sop_catalog(sop_service)
    except SopLoadError as exc:
        sop_error = str(exc)
        st.warning(
            "案件列表可正常使用；SOP 資料目前無法讀取。"
            "請確認兩張 SOP 工作表為可檢視，且欄位名稱未變更。"
        )
    if sop_catalog is not None:
        for warning in sop_catalog.warnings:
            st.warning(warning)

    (
        search_text,
        abnormal_type,
        overdue_status,
        sort_by,
    ) = _render_search_and_filters(
        case_service=case_service,
        cases=snapshot.cases,
    )
    stage = _render_stage_filter(
        case_service=case_service,
        cases=snapshot.cases,
    )
    filters = DashboardFilters(
        search_text=search_text,
        stage=stage,
        abnormal_type=abnormal_type,
        overdue_status=overdue_status,
        sort_by=sort_by,
    )
    filtered_cases = case_service.filter_and_sort(
        cases=snapshot.cases,
        filters=filters,
    )
    st.markdown(
        (
            '<div class="dashboard-meta">'
            f"顯示 {len(filtered_cases)}／{len(snapshot.cases)} 筆｜"
            f"更新時間 {snapshot.loaded_at:%Y-%m-%d %H:%M:%S}｜"
            f"版本 {DEPLOY_VERSION}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    render_case_table(
        cases=filtered_cases,
        sop_service=sop_service,
        sop_catalog=sop_catalog,
        sop_error=sop_error,
    )


def _render_stage_filter(
    case_service: CaseService,
    cases: Sequence[DashboardCase],
) -> str:
    counts = case_service.stage_counts(cases)
    labels = {
        stage: f"{stage} {counts.get(stage, 0)}"
        for stage in STAGE_FILTER_ORDER
    }
    stage_col, legend_col = st.columns(
        [3.15, 3.5],
        gap="small",
        vertical_alignment="center",
    )
    with stage_col:
        selected_label = st.radio(
            "案件階段",
            options=[labels[stage] for stage in STAGE_FILTER_ORDER],
            horizontal=True,
            label_visibility="collapsed",
            key="stage_filter",
        )
    with legend_col:
        st.markdown(
            (
                '<div class="waiting-legend" aria-label="等待時間顏色說明">'
                '<span class="waiting-legend-item" '
                'title="D+3 工作日 17:00 起">'
                '<span class="waiting-legend-status overdue">逾期</span>'
                '<span>達 3 個工作日</span>'
                '</span>'
                '<span class="waiting-legend-item" '
                'title="D+1 工作日 17:00 起">'
                '<span class="waiting-legend-status warning">警示</span>'
                '<span>達 1 個工作日</span>'
                '</span>'
                '<span class="waiting-legend-item">'
                '<span class="waiting-legend-status normal">正常</span>'
                '<span>未滿 1 個工作日</span>'
                '</span>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )
    return next(
        stage for stage, label in labels.items() if label == selected_label
    )


def _render_search_and_filters(
    case_service: CaseService,
    cases: Sequence[DashboardCase],
) -> tuple[str, str, str, str]:
    search_col, type_col, overdue_col, sort_col, refresh_col = st.columns(
        [2.4, 1.3, 1.1, 1.3, 0.55],
        vertical_alignment="bottom",
    )

    with search_col:
        search_text = st.text_input(
            "搜尋案件",
            placeholder="搜尋案件編號、件號、台車號、區塊或處理人員",
        )
    with type_col:
        abnormal_type = st.selectbox(
            "異常類型",
            options=case_service.abnormal_type_options(cases),
        )
    with overdue_col:
        overdue_label = st.selectbox(
            "逾期狀態",
            options=list(OVERDUE_FILTER_LABELS.values()),
        )
        overdue_status = next(
            value
            for value, label in OVERDUE_FILTER_LABELS.items()
            if label == overdue_label
        )
    with sort_col:
        sort_by = st.selectbox("排序方式", options=SORT_OPTIONS)
    with refresh_col:
        if st.button("重新整理", use_container_width=True):
            _load_snapshot.clear()
            _load_sop_catalog.clear()
            st.rerun()

    return search_text, abnormal_type, overdue_status, sort_by
