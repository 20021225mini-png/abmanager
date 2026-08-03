"""應用程式、資料來源與路徑設定。"""

from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]

GOOGLE_SHEET_ID = "1MTPfTw0i-DWZbNzfXtKUOS56UI_xaedKIAzM9E7ecD4"
CASE_SHEET_GID = "1219451878"
CASE_SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}"
    f"/export?format=csv&gid={CASE_SHEET_GID}"
)

SOP_GOOGLE_SHEET_ID = "1sWFKUs2yDYKAyOTxPQeVqN6H9Ta00gq8VGOfzuoM_AM"
SOP_RULES_SHEET_NAME = "CLASSIFICATION_RULES"
SOP_NODES_SHEET_NAME = "SOP_NODES"
SOP_RULES_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SOP_GOOGLE_SHEET_ID}"
    f"/gviz/tq?tqx=out:csv&sheet={SOP_RULES_SHEET_NAME}"
)
SOP_NODES_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SOP_GOOGLE_SHEET_ID}"
    f"/gviz/tq?tqx=out:csv&sheet={SOP_NODES_SHEET_NAME}"
)

LOCAL_TIMEZONE = ZoneInfo("Asia/Taipei")
DATETIME_DISPLAY_FORMAT = "%Y-%m-%d %H:%M"
CACHE_TTL_SECONDS = 60
SOP_CACHE_TTL_SECONDS = 300

PAGE_TITLE = "進出異常案件 Follow 看板"
PAGE_LAYOUT = "wide"
