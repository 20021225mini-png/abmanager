"""Streamlit 應用程式啟動入口。"""

import streamlit as st

from config.writeback import load_case_write_settings
from data.apps_script_case_writer import AppsScriptCaseWriter
from data.google_sheet_repository import GoogleSheetCaseRepository
from data.google_sheet_sop_repository import GoogleSheetSopRepository
from services.case_service import CaseService
from services.judgement_service import JudgementService
from services.sop_service import SopService
from ui.dashboard import render_dashboard


def main() -> None:
    """組合相依元件並啟動看板。"""
    repository = GoogleSheetCaseRepository()
    sop_repository = GoogleSheetSopRepository()
    case_service = CaseService(repository=repository)
    sop_service = SopService(repository=sop_repository)
    judgement_service = JudgementService()

    write_settings = load_case_write_settings(st.secrets)
    case_writer = None
    if write_settings.is_configured:
        case_writer = AppsScriptCaseWriter(
            endpoint_url=write_settings.endpoint_url,
            api_token=write_settings.api_token,
        )

    render_dashboard(
        case_service=case_service,
        sop_service=sop_service,
        judgement_service=judgement_service,
        case_writer=case_writer,
    )


if __name__ == "__main__":
    main()
