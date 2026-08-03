"""Google Sheet CASE 工作表欄位設定。"""

CASE_NO = "CASE_NO"
CREATED_AT = "CREATED_AT"
UPDATED_AT = "UPDATED_AT"
CLOSED_AT = "CLOSED_AT"
PRODUCT_TYPE = "PRODUCT_TYPE"
PART_NO = "PART_NO"
QTY = "QTY"
SITUATION = "SITUATION"
ORIGINAL_CART = "ORIGINAL_CART"
NOTE = "NOTE"
STAGE = "STAGE"
FINAL_RESOLUTION = "FINAL_RESOLUTION"
LAYER = "LAYER"
FLOOR = "FLOOR"
HANDLER = "HANDLER_NAME"
SHELVING_STATUS = "SHELVING_STATUS"
SHELVING_COMPLETED_AT = "SHELVING_COMPLETED_AT"
CLASSIFICATION_ID = "CLASSIFICATION_ID"
CASE_JUDGEMENT = "CASE_JUDGEMENT"
JUDGEMENT_RESULT = "JUDGEMENT_RESULT"
ACTUAL_SCENARIO = "ACTUAL_SCENARIO"

REQUIRED_SOURCE_COLUMNS: tuple[str, ...] = (
    CASE_NO,
    CREATED_AT,
    PART_NO,
    QTY,
    SITUATION,
    ORIGINAL_CART,
    STAGE,
    LAYER,
    FLOOR,
)

OPTIONAL_SOURCE_COLUMNS: tuple[str, ...] = (
    UPDATED_AT,
    CLOSED_AT,
    PRODUCT_TYPE,
    NOTE,
    HANDLER,
    FINAL_RESOLUTION,
    SHELVING_STATUS,
    SHELVING_COMPLETED_AT,
    CLASSIFICATION_ID,
    CASE_JUDGEMENT,
    JUDGEMENT_RESULT,
    ACTUAL_SCENARIO,
)

ALL_SOURCE_COLUMNS: tuple[str, ...] = (
    *REQUIRED_SOURCE_COLUMNS,
    *OPTIONAL_SOURCE_COLUMNS,
)

# CLOSED_AT 直接取自 CASE 工作表；未結案案件維持空白。
# HANDLER 取自 CASE 工作表的 HANDLER_NAME。

# 下列欄位允許 Google Sheet 使用程式欄名、中文欄名或常見拼法。
# 讀取後統一轉為上方的大寫欄名，避免 UI 與資料來源耦合。
SOURCE_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    CLASSIFICATION_ID: ("classification_id", "分類編號"),
    CASE_JUDGEMENT: (
        "case_judgement",
        "case_judgment",
        "本案判定",
    ),
    JUDGEMENT_RESULT: (
        "judgement_result",
        "judgment_result",
        "判斷結果",
    ),
    ACTUAL_SCENARIO: (
        "actual_scenario",
        "實際情境",
        "異常情境",
    ),
}
