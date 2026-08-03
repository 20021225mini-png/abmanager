"""案件互動判定所需的畫面資料模型。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationOption:
    """使用者看到中文說明、程式保存分類代碼的一個選項。"""

    classification_id: str
    label: str
    case_judgement: str
    main_type: str
    actual_scenario: str
    condition_text: str
    entry_node_id: str


@dataclass(frozen=True)
class JudgementChoices:
    """單一案件的建議分類與完整分類目錄。"""

    recommended: tuple[ClassificationOption, ...]
    all_options: tuple[ClassificationOption, ...]
    current_classification_id: str = ""
    message: str = ""
