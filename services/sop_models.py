"""SOP 服務層輸出的唯讀畫面模型。"""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class SopCatalog:
    """一次讀取後可供所有案件共用的 SOP 資料。"""

    rules: tuple[Mapping[str, Any], ...]
    nodes: tuple[Mapping[str, Any], ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class SopBranch:
    """判斷節點的單一結果與下一步。"""

    label: str
    destination: str


@dataclass(frozen=True)
class SopStep:
    """畫面上顯示的一個 SOP 步驟。"""

    step_no: str
    instruction: str
    required_data: str
    node_type: str
    branches: tuple[SopBranch, ...] = ()
    result: str = ""
    notice: str = ""


@dataclass(frozen=True)
class SopModule:
    """一組共用流程模組。"""

    sop_id: str
    flow_name: str
    steps: tuple[SopStep, ...]


@dataclass(frozen=True)
class CaseSopDetail:
    """單一案件的 SOP 與分類摘要。"""

    modules: tuple[SopModule, ...] = ()
    case_judgement: str = ""
    main_type: str = ""
    actual_scenario: str = ""
    condition_text: str = ""
    mapping_message: str = ""
