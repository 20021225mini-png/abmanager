"""V11 案件判定與 CASE 寫回畫面。"""

from collections.abc import Sequence

import streamlit as st

from data.case_writer import CaseJudgementUpdate, CaseWriteError, CaseWriter
from services.judgement_models import ClassificationOption
from services.judgement_service import JudgementService
from services.models import DashboardCase
from services.sop_models import SopCatalog


def render_judgement_workspace(
    cases: Sequence[DashboardCase],
    catalog: SopCatalog | None,
    judgement_service: JudgementService,
    case_writer: CaseWriter | None,
) -> bool:
    """顯示案件分類表單；成功寫回時回傳 True。"""
    with st.expander("案件判定與寫回", expanded=False):
        st.caption(
            "依 SOP 查詢後選擇中文判定，系統會自動保存 "
            "CLASSIFICATION_ID，並記錄本案的 JUDGEMENT_RESULT。"
        )

        if catalog is None:
            st.warning("SOP 分類資料載入後即可進行案件判定。")
            return False

        editable_cases = tuple(
            case
            for case in cases
            if not case.is_completed and case.case_no
        )
        if not editable_cases:
            st.info("目前所有案件皆已完成。")
            return False

        case_by_no = {case.case_no: case for case in editable_cases}
        case_numbers = tuple(case_by_no)
        selected_case_no = st.selectbox(
            "選擇案件",
            options=case_numbers,
            format_func=lambda case_no: _case_option_label(case_by_no[case_no]),
            key="v11_selected_case_no",
        )
        case = case_by_no[selected_case_no]
        choices = judgement_service.build_choices(case=case, catalog=catalog)

        show_all = st.checkbox(
            "顯示全部分類",
            value=not bool(choices.recommended),
            key=f"v11_show_all_{case.case_no}",
        )
        options = choices.all_options if show_all else choices.recommended
        st.caption(choices.message)
        if not options:
            st.warning("CLASSIFICATION_RULES 目前沒有可選擇的分類。")
            return False

        option_by_id = {
            option.classification_id: option
            for option in options
        }
        option_ids = tuple(option_by_id)
        current_id = case.classification_id
        default_index = (
            option_ids.index(current_id)
            if current_id in option_by_id
            else 0
        )
        selected_id = st.selectbox(
            "本案判定",
            options=option_ids,
            index=default_index,
            format_func=lambda option_id: option_by_id[option_id].label,
            key=f"v11_classification_{case.case_no}_{show_all}",
        )
        selected = option_by_id[selected_id]
        _render_classification_preview(selected)

        judgement_result = st.text_area(
            "本案實際判斷結果",
            value=case.judgement_result,
            placeholder="例如：HOPES 顯示相近時間刷入兩筆，其中一筆未成立",
            help="請記錄這筆案件實際查詢、盤點或確認到的結果。",
            key=f"v11_judgement_result_{case.case_no}",
        )

        if case_writer is None:
            st.info(
                "V11 寫回設定完成後即可使用儲存功能；"
                "目前仍可先查看分類與 SOP。"
            )

        submitted = st.button(
            "儲存判定",
            type="primary",
            disabled=case_writer is None,
            key=f"v11_save_{case.case_no}",
        )
        if not submitted or case_writer is None:
            return False

        judgement_result = judgement_result.strip()
        if not judgement_result:
            st.error("請填寫本案實際判斷結果後再儲存。")
            return False

        try:
            result = case_writer.update_judgement(
                CaseJudgementUpdate(
                    case_no=case.case_no,
                    classification_id=selected.classification_id,
                    judgement_result=judgement_result,
                )
            )
        except CaseWriteError as exc:
            st.error(str(exc))
            return False

        st.session_state["v11_write_success"] = (
            f"案件 {result.case_no} 已完成判定並寫回 CASE。"
        )
        return True


def _case_option_label(case: DashboardCase) -> str:
    parts = [case.case_no, case.part_no, case.abnormal_type]
    return "｜".join(part for part in parts if part)


def _render_classification_preview(option: ClassificationOption) -> None:
    st.markdown(
        f"""
        <div class="judgement-preview">
            <div><span>本案判定</span><strong>{_html(option.case_judgement)}</strong></div>
            <div><span>主類型</span><strong>{_html(option.main_type)}</strong></div>
            <div><span>實際情境</span><strong>{_html(option.actual_scenario)}</strong></div>
            <div class="judgement-preview-wide"><span>判定條件</span><strong>{_html(option.condition_text)}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _html(value: str) -> str:
    from html import escape

    return escape(value or "尚未填寫")
