from __future__ import annotations

import app


def test_compatibility_call_keeps_old_dashboard_signature(monkeypatch) -> None:
    received = {}

    def old_dashboard(*, case_service, sop_service) -> None:
        received.update(
            case_service=case_service,
            sop_service=sop_service,
        )

    monkeypatch.setattr(app, "render_dashboard", old_dashboard)
    app._render_dashboard_compatibly(
        case_service="case",
        sop_service="sop",
        judgement_service="judgement",
        case_writer="writer",
    )

    assert received == {
        "case_service": "case",
        "sop_service": "sop",
    }


def test_compatibility_call_enables_full_v11_dashboard(monkeypatch) -> None:
    received = {}

    def v11_dashboard(
        *,
        case_service,
        sop_service,
        judgement_service,
        case_writer,
    ) -> None:
        received.update(
            case_service=case_service,
            sop_service=sop_service,
            judgement_service=judgement_service,
            case_writer=case_writer,
        )

    monkeypatch.setattr(app, "render_dashboard", v11_dashboard)
    app._render_dashboard_compatibly(
        case_service="case",
        sop_service="sop",
        judgement_service="judgement",
        case_writer="writer",
    )

    assert received == {
        "case_service": "case",
        "sop_service": "sop",
        "judgement_service": "judgement",
        "case_writer": "writer",
    }
