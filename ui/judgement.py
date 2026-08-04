"""停用的案件判定 UI 相容層。

舊版 ``ui/dashboard.py`` 仍可能呼叫此函式。保留相同函式名稱與參數，
但不建立任何 Streamlit 元件，使混合版本也不會再顯示案件判定與寫回區塊。
"""


def render_judgement_workspace(
    cases: object,
    catalog: object | None,
    judgement_service: object,
    case_writer: object | None,
) -> bool:
    """維持舊版呼叫相容；現行查閱版不顯示或寫回案件判定。"""
    _ = cases, catalog, judgement_service, case_writer
    return False
