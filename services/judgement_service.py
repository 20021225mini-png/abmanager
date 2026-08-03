"""依案件情境建立可操作的中文分類判定選項。"""

from collections.abc import Iterable
from typing import Any, Mapping, Sequence

from services.judgement_models import ClassificationOption, JudgementChoices
from services.models import DashboardCase
from services.sop_models import SopCatalog


class JudgementService:
    """將 CLASSIFICATION_RULES 轉成看板可選擇的判定項目。"""

    MATCH_COLUMNS: tuple[str, ...] = (
        "report_scenario",
        "display_type",
        "sub_type",
        "main_type",
    )

    def build_choices(
        self,
        case: DashboardCase,
        catalog: SopCatalog,
    ) -> JudgementChoices:
        """先列案件情境相符的建議項目，仍保留查看全部分類。"""
        all_options = tuple(
            option
            for rule in catalog.rules
            if (option := self._to_option(rule)) is not None
        )
        search_values = self._deduplicate_text(
            (
                case.actual_scenario,
                case.case_judgement,
                case.abnormal_type,
            )
        )
        recommended_ids: list[str] = []
        for value in search_values:
            matches = [
                self._text(rule.get("classification_id"))
                for rule in catalog.rules
                if any(
                    self._equals(rule.get(column), value)
                    for column in self.MATCH_COLUMNS
                )
            ]
            matches = [value for value in matches if value]
            if matches:
                recommended_ids = matches
                break

        if case.classification_id and case.classification_id not in recommended_ids:
            recommended_ids.insert(0, case.classification_id)

        recommended_id_set = set(recommended_ids)
        recommended = tuple(
            option
            for option in all_options
            if option.classification_id in recommended_id_set
        )

        if recommended:
            message = "已依案件登記情境優先列出可能的判定項目。"
        else:
            message = "目前情境尚未唯一對應，請展開完整分類後選擇。"

        return JudgementChoices(
            recommended=recommended,
            all_options=all_options,
            current_classification_id=case.classification_id,
            message=message,
        )

    @classmethod
    def _to_option(
        cls,
        rule: Mapping[str, Any],
    ) -> ClassificationOption | None:
        classification_id = cls._text(rule.get("classification_id"))
        if not classification_id:
            return None

        main_type = cls._text(rule.get("main_type"))
        display_type = (
            cls._text(rule.get("display_type"))
            or cls._text(rule.get("sub_type"))
        )
        report_scenario = cls._text(rule.get("report_scenario"))
        actual_scenario = report_scenario or display_type
        condition_text = cls._text(rule.get("condition_text"))

        label_parts = [part for part in (main_type, actual_scenario) if part]
        if condition_text:
            label_parts.append(condition_text)
        return ClassificationOption(
            classification_id=classification_id,
            label="｜".join(label_parts) or classification_id,
            case_judgement=display_type or main_type,
            main_type=main_type,
            actual_scenario=actual_scenario,
            condition_text=condition_text,
            entry_node_id=cls._text(rule.get("entry_node_id")),
        )

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
    def _text(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()
