"""Streamlit 應用程式啟動入口。"""

from data.google_sheet_repository import GoogleSheetCaseRepository
from data.google_sheet_sop_repository import GoogleSheetSopRepository
from services.case_service import CaseService
from services.sop_service import SopService
from ui.dashboard import render_dashboard


def main() -> None:
    """組合相依元件並啟動看板。"""
    repository = GoogleSheetCaseRepository()
    sop_repository = GoogleSheetSopRepository()
    case_service = CaseService(repository=repository)
    sop_service = SopService(repository=sop_repository)
    render_dashboard(case_service=case_service, sop_service=sop_service)


if __name__ == "__main__":
    main()
