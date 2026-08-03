"""看板外觀設定。"""

DASHBOARD_CSS = """
<style>
    :root {
        --hotai-blue: #004caa;
        --hotai-blue-dark: #082c68;
        --hotai-red: #ee1c25;
        --line: #dce8f8;
        --soft-blue: #eef5ff;
        --muted: #7c8ba1;
        --table-columns:
            minmax(72px, .75fr)
            minmax(112px, 1.25fr)
            minmax(96px, 1fr)
            minmax(62px, .55fr)
            minmax(120px, 1.15fr)
            minmax(138px, 1.35fr)
            minmax(210px, 2fr)
            minmax(148px, 1.45fr)
            minmax(112px, 1.05fr)
            minmax(100px, 1fr);
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 0%, #f3f7ff 0, transparent 34%),
            #ffffff;
    }

    .block-container {
        max-width: none;
        width: 100%;
        padding-top: 1.6rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2.5rem;
    }

    .dashboard-title {
        margin: 0 0 1.2rem;
        color: var(--hotai-blue-dark);
        font-size: 2rem;
        font-weight: 800;
        text-align: center;
        letter-spacing: .06em;
    }

    .dashboard-meta {
        color: var(--muted);
        font-size: .86rem;
        text-align: right;
    }

    .case-table-wrap {
        width: 100%;
        overflow-x: auto;
        border: 1px solid #cfe0f7;
        border-radius: 18px;
        background: rgba(255, 255, 255, .96);
        box-shadow: 0 16px 40px rgba(15, 57, 117, .08);
    }

    .case-table {
        min-width: 1200px;
        padding: 16px 8px 10px;
    }

    .case-group-header,
    .case-column-header,
    .case-summary {
        display: grid;
        grid-template-columns: var(--table-columns);
        align-items: center;
    }

    .case-group-header {
        gap: 3px;
    }

    .group-title {
        padding: 10px 8px;
        border-radius: 8px 8px 4px 4px;
        background: linear-gradient(135deg, #075bd0, var(--hotai-blue));
        color: white;
        font-size: 1rem;
        font-weight: 700;
        text-align: center;
        letter-spacing: .08em;
    }

    .group-info {
        grid-column: span 5;
    }

    .group-progress {
        grid-column: span 3;
    }

    .group-state {
        grid-column: span 2;
    }

    .case-column-header {
        margin-top: 8px;
        border-radius: 8px;
        background: linear-gradient(90deg, #edf4fc, #e6effa);
        color: var(--hotai-blue-dark);
        font-weight: 700;
    }

    .case-column-header > span,
    .case-summary > span {
        min-width: 0;
        padding: 12px 4px;
        text-align: center;
        overflow-wrap: anywhere;
    }

    details.case-row {
        border-bottom: 1px solid var(--line);
    }

    details.case-row:last-child {
        border-bottom: none;
    }

    .case-summary {
        min-height: 72px;
        cursor: pointer;
        color: #173a70;
        list-style: none;
        transition: background .15s ease;
    }

    .case-summary::-webkit-details-marker {
        display: none;
    }

    .case-summary:hover {
        background: #f8fbff;
    }

    details[open] .case-summary {
        background: #f4f8fe;
    }

    .case-no {
        font-weight: 800;
    }

    .abnormal-badge,
    .instruction-badge,
    .waiting-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 30px;
        padding: 4px 12px;
        border-radius: 999px;
        font-weight: 700;
    }

    .abnormal-badge {
        background: #eef3f9;
        color: #304f78;
    }

    .instruction-badge {
        border-radius: 8px;
        background: #f3f5f8;
        color: #475a74;
    }

    .waiting-badge.normal {
        background: #eef3f9;
        color: #173a70;
    }

    .waiting-badge.warning {
        background: #fff2cb;
        color: #b45c00;
    }

    .waiting-badge.overdue,
    .waiting-badge.error {
        background: #ffe2e2;
        color: #d51019;
    }

    .waiting-badge.completed {
        background: #edf1f5;
        color: #607087;
    }

    .stage-flow {
        display: flex;
        align-items: flex-start;
        justify-content: center;
        width: 100%;
    }

    .stage-node {
        position: relative;
        flex: 1 1 0;
        min-width: 58px;
        color: #8c9aae;
        font-size: .73rem;
        text-align: center;
    }

    .stage-node:not(:last-child)::after {
        content: "";
        position: absolute;
        top: 6px;
        left: calc(50% + 8px);
        right: calc(-50% + 8px);
        height: 2px;
        background: #cbd3df;
    }

    .stage-dot {
        position: relative;
        z-index: 2;
        display: block;
        width: 13px;
        height: 13px;
        margin: 0 auto 7px;
        border-radius: 50%;
        background: #cbd3df;
    }

    .stage-node.completed,
    .stage-node.completed::after {
        color: #0963c8;
    }

    .stage-node.completed .stage-dot,
    .stage-node.completed::after {
        background: #0963c8;
    }

    .stage-node.current {
        color: var(--hotai-red);
        font-weight: 800;
    }

    .stage-node.current .stage-dot {
        background: var(--hotai-red);
        box-shadow: 0 0 0 4px rgba(238, 28, 37, .1);
    }

    .stage-node.followup {
        color: #d77900;
        font-weight: 800;
    }

    .stage-node.followup .stage-dot {
        background: #f2a23a;
        box-shadow: 0 0 0 4px rgba(242, 162, 58, .12);
    }

    .case-details-layout {
        display: grid;
        grid-template-columns: minmax(0, 1.65fr) minmax(300px, 1fr);
        gap: 16px;
        padding: 18px;
        background: #f5f9ff;
        align-items: start;
    }

    .detail-panel {
        min-width: 0;
        border: 1px solid #dce8f7;
        border-radius: 14px;
        background: #ffffff;
        box-shadow: 0 8px 24px rgba(24, 57, 96, .05);
    }

    .detail-panel-title {
        margin: 0;
        padding: 15px 18px;
        border-bottom: 1px solid #e5edf8;
        color: var(--hotai-blue-dark);
        font-size: 1.02rem;
        font-weight: 800;
        letter-spacing: .04em;
    }

    .sop-scroll {
        max-height: 620px;
        padding: 14px 16px 18px;
        overflow-y: auto;
        scrollbar-color: #b8c9e0 transparent;
        scrollbar-width: thin;
    }

    .sop-module + .sop-module {
        margin-top: 16px;
    }

    .sop-module-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        border-radius: 10px;
        background: #edf5ff;
        color: #123f7a;
    }

    .sop-module-heading strong,
    .sop-module-heading small {
        display: block;
    }

    .sop-module-heading small {
        margin-top: 2px;
        color: #7185a0;
        font-size: .7rem;
        font-weight: 600;
    }

    .sop-module-index {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 28px;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: var(--hotai-blue);
        color: white;
        font-weight: 800;
    }

    .sop-steps {
        margin-left: 14px;
        padding-left: 22px;
        border-left: 2px solid #d4e3f6;
    }

    .sop-step {
        position: relative;
        padding: 13px 0 14px;
        border-bottom: 1px dashed #dfe8f3;
    }

    .sop-step:last-child {
        border-bottom: none;
    }

    .sop-step::before {
        content: "";
        position: absolute;
        top: 21px;
        left: -29px;
        width: 10px;
        height: 10px;
        border: 3px solid #ffffff;
        border-radius: 50%;
        background: var(--hotai-blue);
        box-shadow: 0 0 0 1px #a9c4e8;
    }

    .sop-step-head {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 10px;
        align-items: start;
    }

    .sop-step-number {
        padding: 3px 8px;
        border-radius: 6px;
        background: #e8f2ff;
        color: #0c59b5;
        font-size: .72rem;
        font-weight: 800;
        white-space: nowrap;
    }

    .sop-instruction {
        color: #183960;
        font-weight: 700;
        line-height: 1.55;
    }

    .sop-required {
        margin: 8px 0 0 72px;
        color: #657892;
        font-size: .78rem;
        line-height: 1.5;
    }

    .sop-required > span {
        margin-right: 6px;
        color: #3d5d84;
        font-weight: 800;
    }

    .sop-branches {
        display: grid;
        gap: 7px;
        margin: 10px 0 0 72px;
    }

    .sop-branch {
        display: grid;
        grid-template-columns: minmax(110px, auto) 18px 1fr;
        gap: 7px;
        padding: 9px 10px;
        border-left: 3px solid #f2a23a;
        border-radius: 6px;
        background: #fff8e9;
        color: #5a4a2d;
        font-size: .8rem;
        line-height: 1.45;
    }

    .branch-arrow {
        color: #c96a00;
        font-weight: 800;
    }

    .sop-result,
    .sop-notice {
        margin: 9px 0 0 72px;
        padding: 8px 10px;
        border-radius: 7px;
        font-size: .78rem;
        font-weight: 700;
        line-height: 1.5;
    }

    .sop-result {
        background: #eaf8f1;
        color: #08764b;
    }

    .sop-notice {
        background: #fff1f1;
        color: #c71921;
    }

    .sop-message,
    .sop-empty {
        margin: 14px 16px 16px;
        padding: 11px 12px;
        border-radius: 8px;
        background: #fff7e6;
        color: #945400;
        font-size: .82rem;
        font-weight: 700;
        line-height: 1.5;
    }

    .sop-empty {
        margin: 0;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        padding: 14px;
    }

    .summary-item {
        min-width: 0;
        padding: 11px 12px;
        border: 1px solid #e3eaf4;
        border-radius: 9px;
        background: #f8fafe;
    }

    .summary-wide {
        grid-column: 1 / -1;
    }

    .summary-label,
    .summary-value {
        display: block;
    }

    .summary-label {
        margin-bottom: 4px;
        color: #6a7f9b;
        font-size: .72rem;
        font-weight: 800;
    }

    .summary-value {
        color: #183960;
        font-size: .86rem;
        font-weight: 650;
        line-height: 1.55;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
    }

    .data-errors {
        margin: 0 18px 18px;
        padding: 10px 14px;
        border-radius: 8px;
        background: #fff0f0;
        color: #c71921;
        font-weight: 700;
    }

    .empty-state {
        padding: 52px 24px;
        color: #70829a;
        text-align: center;
    }

    @media (max-width: 900px) {
        .case-details-layout {
            grid-template-columns: 1fr;
        }

        .sop-scroll {
            max-height: none;
        }

        .sop-step-head {
            grid-template-columns: 1fr;
        }

        .sop-required,
        .sop-branches,
        .sop-result,
        .sop-notice {
            margin-left: 0;
        }

        .sop-branch {
            grid-template-columns: 1fr;
        }

        .branch-arrow {
            transform: rotate(90deg);
        }
    }
</style>
"""
