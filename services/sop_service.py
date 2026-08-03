"""SOP 分類比對、跨模組路徑追蹤與唯讀畫面資料整理。"""

from collections import deque
from collections.abc import Iterable
from typing import Any, Mapping, Sequence

from data.sop_repository import SopDataSourceError, SopRepository
from services.models import DashboardCase
from services.sop_models import (
    CaseSopDetail,
    SopBranch,
    SopCatalog,
    SopModule,
    SopStep,
)


class SopLoadError(RuntimeError):
    """SOP 服務層無法建立資料目錄。"""


class SopService:
    """將 SOP 程式表轉成案件明細可直接顯示的內容。"""

    MATCH_COLUMNS: tuple[str, ...] = (
        "report_scenario",
        "display_type",
        "sub_type",
        "main_type",
    )

    def __init__(self, repository: SopRepository) -> None:
        self._repository = repository

    def load_catalog(self) -> SopCatalog:
        """讀取一次 SOP 資料，供同一頁所有案件共用。"""
        try:
            dataset = self._repository.load_sop_data()
        except SopDataSourceError as exc:
            raise SopLoadError(str(exc)) from exc
        return SopCatalog(
            rules=dataset.rules,
            nodes=dataset.nodes,
            warnings=dataset.warnings,
        )

    def build_case_detail(
        self,
        case: DashboardCase,
        catalog: SopCatalog,
    ) -> CaseSopDetail:
        """比對案件分類並建立左側 SOP 與右側判定資訊。"""
        candidates, match_message = self._resolve_candidates(
            case=case,
            rules=catalog.rules,
        )
        if not candidates:
            return CaseSopDetail(
                case_judgement=case.case_judgement or case.abnormal_type,
                actual_scenario=case.actual_scenario or case.abnormal_type,
                mapping_message=match_message,
            )

        resolved_entry_node_ids = self._unique_values(
            candidates,
            "resolved_entry_node_id",
        )
        entry_node_ids = (
            resolved_entry_node_ids
            if len(candidates) == 1 and len(resolved_entry_node_ids) == 1
            else self._unique_values(candidates, "entry_node_id")
        )
        if len(entry_node_ids) != 1:
            message = (
                match_message
                or "案件對應到不同 SOP，請在 CASE 補入 classification_id。"
            )
            return self._summary_only_detail(
                case=case,
                candidates=candidates,
                mapping_message=message,
            )

        mapping_message = match_message
        if len(candidates) > 1 and not mapping_message:
            mapping_message = (
                "已找到共用 SOP；右側僅顯示候選規則中一致的資訊。"
                "如需顯示完整判定條件，請在 CASE 補入 classification_id。"
            )

        modules = self._build_modules(
            nodes=catalog.nodes,
            entry_node_id=entry_node_ids[0],
        )
        if not modules:
            mapping_message = (
                f"找不到起始節點 {entry_node_ids[0]}，請檢查 SOP_NODES。"
            )

        summary = self._summary_values(case=case, candidates=candidates)
        return CaseSopDetail(
            modules=modules,
            case_judgement=summary["case_judgement"],
            main_type=summary["main_type"],
            actual_scenario=summary["actual_scenario"],
            condition_text=summary["condition_text"],
            mapping_message=mapping_message,
        )

    def _resolve_candidates(
        self,
        case: DashboardCase,
        rules: Sequence[Mapping[str, Any]],
    ) -> tuple[tuple[Mapping[str, Any], ...], str]:
        classification_id = self._text(case.classification_id)
        if classification_id:
            matched = tuple(
                rule
                for rule in rules
                if self._equals(rule.get("classification_id"), classification_id)
            )
            if len(matched) == 1:
                return matched, ""
            if len(matched) > 1:
                return matched, "分類編號重複，請檢查 CLASSIFICATION_RULES。"

        search_values = self._deduplicate_text(
            (
                case.actual_scenario,
                case.case_judgement,
                case.abnormal_type,
            )
        )
        for value in search_values:
            matched = tuple(
                rule
                for rule in rules
                if any(
                    self._equals(rule.get(column), value)
                    for column in self.MATCH_COLUMNS
                )
            )
            if matched:
                message = ""
                if classification_id:
                    message = (
                        f"找不到分類編號 {classification_id}，已改用案件情境比對。"
                    )
                return matched, message

        return (), "找不到對應的 SOP，請確認案件異常情境或分類編號。"

    def _summary_only_detail(
        self,
        case: DashboardCase,
        candidates: Sequence[Mapping[str, Any]],
        mapping_message: str,
    ) -> CaseSopDetail:
        summary = self._summary_values(case=case, candidates=candidates)
        return CaseSopDetail(
            case_judgement=summary["case_judgement"],
            main_type=summary["main_type"],
            actual_scenario=summary["actual_scenario"],
            condition_text=summary["condition_text"],
            mapping_message=mapping_message,
        )

    def _summary_values(
        self,
        case: DashboardCase,
        candidates: Sequence[Mapping[str, Any]],
    ) -> dict[str, str]:
        display_type = self._common_value(candidates, "display_type")
        sub_type = self._common_value(candidates, "sub_type")
        report_scenario = self._common_value(candidates, "report_scenario")
        return {
            "case_judgement": (
                case.case_judgement
                or display_type
                or sub_type
                or case.abnormal_type
            ),
            "main_type": self._common_value(candidates, "main_type"),
            "actual_scenario": (
                case.actual_scenario
                or report_scenario
                or display_type
                or sub_type
                or case.abnormal_type
            ),
            "condition_text": self._common_value(candidates, "condition_text"),
        }

    def _build_modules(
        self,
        nodes: Sequence[Mapping[str, Any]],
        entry_node_id: str,
    ) -> tuple[SopModule, ...]:
        rows_by_node: dict[str, list[Mapping[str, Any]]] = {}
        for row in nodes:
            node_id = self._text(row.get("node_id"))
            if node_id:
                rows_by_node.setdefault(node_id, []).append(row)

        visit_order: dict[str, int] = {}
        queue: deque[str] = deque([entry_node_id])
        while queue:
            node_id = queue.popleft()
            if node_id in visit_order or node_id not in rows_by_node:
                continue
            visit_order[node_id] = len(visit_order)
            for row in sorted(
                rows_by_node[node_id],
                key=lambda item: self._number(item.get("option_order")),
            ):
                next_node_id = self._text(row.get("next_node_id"))
                if next_node_id and next_node_id not in visit_order:
                    queue.append(next_node_id)

        module_nodes: dict[str, list[str]] = {}
        module_order: dict[str, int] = {}
        for node_id, order in visit_order.items():
            first = rows_by_node[node_id][0]
            sop_id = self._text(first.get("sop_id"))
            module_nodes.setdefault(sop_id, []).append(node_id)
            module_order[sop_id] = min(module_order.get(sop_id, order), order)

        modules: list[SopModule] = []
        for sop_id in sorted(module_nodes, key=module_order.get):
            node_ids = sorted(
                module_nodes[sop_id],
                key=lambda node_id: (
                    self._number(rows_by_node[node_id][0].get("step_no")),
                    visit_order[node_id],
                ),
            )
            first_module_row = rows_by_node[node_ids[0]][0]
            steps = tuple(
                self._build_step(
                    rows=rows_by_node[node_id],
                    rows_by_node=rows_by_node,
                )
                for node_id in node_ids
            )
            modules.append(
                SopModule(
                    sop_id=sop_id,
                    flow_name=self._text(first_module_row.get("flow_name")),
                    steps=steps,
                )
            )
        return tuple(modules)

    def _build_step(
        self,
        rows: Sequence[Mapping[str, Any]],
        rows_by_node: Mapping[str, Sequence[Mapping[str, Any]]],
    ) -> SopStep:
        ordered = sorted(
            rows,
            key=lambda item: self._number(item.get("option_order")),
        )
        first = ordered[0]
        node_type = self._text(first.get("node_type"))
        branches: tuple[SopBranch, ...] = ()
        if node_type == "DECISION":
            branches = tuple(
                SopBranch(
                    label=self._text(row.get("option_label")) or "此結果",
                    destination=self._describe_destination(
                        row=row,
                        rows_by_node=rows_by_node,
                    ),
                )
                for row in ordered
            )

        has_pending_branch = any(
            self._text(row.get("next_type")) == "PENDING_CONFIRMATION"
            for row in ordered
        )
        return SopStep(
            step_no=self._text(first.get("step_no")),
            instruction=self._text(first.get("instruction")),
            required_data=self._text(first.get("required_data")),
            node_type=node_type,
            branches=branches,
            result=(
                self._text(first.get("end_result"))
                if node_type == "TERMINAL"
                else ""
            ),
            notice=(
                self._common_value(ordered, "pending_confirmation")
                if has_pending_branch
                else ""
            ),
        )

    def _describe_destination(
        self,
        row: Mapping[str, Any],
        rows_by_node: Mapping[str, Sequence[Mapping[str, Any]]],
    ) -> str:
        next_node_id = self._text(row.get("next_node_id"))
        if next_node_id and next_node_id in rows_by_node:
            target = rows_by_node[next_node_id][0]
            if self._text(target.get("sop_id")) != self._text(row.get("sop_id")):
                return f"進入「{self._text(target.get('flow_name'))}」"
            return (
                f"步驟 {self._text(target.get('step_no'))}："
                f"{self._text(target.get('instruction'))}"
            )

        end_result = self._text(row.get("end_result"))
        if end_result:
            return end_result
        next_type = self._text(row.get("next_type"))
        if next_type == "PENDING_CONFIRMATION":
            return "後續處理方式待確認"
        if next_type == "SCOPE_END":
            return "本專案範圍終點"
        if next_type == "END":
            return "本流程完成"
        return "本路徑完成"

    @classmethod
    def _common_value(
        cls,
        rows: Sequence[Mapping[str, Any]],
        column: str,
    ) -> str:
        values = cls._unique_values(rows, column)
        return values[0] if len(values) == 1 else ""

    @classmethod
    def _unique_values(
        cls,
        rows: Sequence[Mapping[str, Any]],
        column: str,
    ) -> tuple[str, ...]:
        return cls._deduplicate_text(cls._text(row.get(column)) for row in rows)

    @classmethod
    def _deduplicate_text(cls, values: Iterable[Any]) -> tuple[str, ...]:
        result: list[str] = []
        for value in values:
            text = cls._text(value)
            if text and text not in result:
                result.append(text)
        return tuple(result)

    @classmethod
    def _equals(cls, left: Any, right: Any) -> bool:
        return cls._text(left).casefold() == cls._text(right).casefold()

    @staticmethod
    def _number(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 999999.0

    @staticmethod
    def _text(value: Any) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        return "" if text.casefold() == "nan" else text
