# 進出異常案件 Follow 看板

使用 Python 與 Streamlit 建立的異常案件 MVP 看板。

## V10 部署修正

若錯誤停在：

```text
from config.settings import SOP_NODES_CSV_URL, SOP_RULES_CSV_URL
```

代表 GitHub 內的 V9／V10 模組版本不一致。請將本壓縮檔的
`app.py`、`requirements.txt`、`config/`、`data/`、`services/`、`ui/`
完整覆蓋到 GitHub 根目錄。`CLASSIFICATION_ID` 與 `JUDGEMENT_RESULT`
可以保留，這兩欄不會造成匯入錯誤。

## V10 更新

- 保留 V9 的案件列表、階段篩選、等待時間與台灣工作日判斷。
- 新增第二份 Google Sheet 作為 SOP 資料來源，不與 CASE 主表合併。
- 展開案件後採「左側處理 SOP、右側案件摘要」配置。
- SOP 會從 `entry_node_id` 追蹤跨模組的後續節點，完整顯示步驟與分支。
- SOP 每 5 分鐘重新讀取；按下「重新整理」會同步更新案件與 SOP。
- 多筆分類共用同一 SOP 時仍可顯示流程，判定摘要只顯示共同資訊。

## 執行方式

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## 分層

- `app.py`：組合相依元件並啟動
- `ui/`：Streamlit 畫面與外觀
- `services/`：等待時間、逾期、案件篩選與排序
- `data/`：Google Sheet CASE 工作表讀取與整理
- `config/`：資料來源、文字、欄位與規則

## Google Sheet 資料來源

- CASE：原本的案件工作表。
- SOP：`異常案件處理SOP`，程式依工作表名稱讀取：
  - `CLASSIFICATION_RULES`
  - `SOP_NODES`

兩張 SOP 工作表需保留現有程式欄名，並設定為部署環境可檢視。

## CASE 可選欄位

V10 可直接沿用目前 CASE 欄位。若要讓右側摘要完整且唯一對應，建議
逐步增加下列欄位：

- `classification_id`：分類編號，例如 `IN-10`；只供程式比對。
- `case_judgement`：本案判定。
- `actual_scenario`：實際情境。
- `judgement_result`：判斷結果。

程式也接受對應的大寫欄名與中文欄名。欄位尚未加入時，會先用
`SITUATION` 比對分類規則；無法唯一判定的摘要維持「尚未填寫」，不會
任意抓取第一筆規則。

## D+3 工作日規則

- 等待時間數字顯示實際經過時間，包含週末與假日。
- 案件於 D+1 工作日截止後進入警示。
- 案件於 D+3 工作日截止後判定逾期。
- 預設每日截止時間為 17:00。
- 工作日依週六、週日與台灣國定假日判斷，國定假日由
  `holidays` 套件提供，不需手動維護公司行事曆。
- 「重新丈量」與「請資訊部修正異常系統資料」以
  `SHELVING_COMPLETED_AT` 作為整案完成時間。
- 查詢條件顯示於第一列；案件狀態按鈕顯示於第二列。
- 案件狀態依序為「全部、待處理、處理中、已結案」。
- 「已結案」包含一般結案與完成上架案件；歷史資料仍保留，
  可搭配搜尋欄查詢。

## 目前資料注意事項

- `classification_id` 尚未填寫且同一情境對應不同 SOP 時，案件明細會
  提示補入分類編號。
- HOPES 開箱紀錄查詢後的結果分流仍依 SOP 資料標示為待確認。
- 缺少來源資料的列表欄位維持空白；案件摘要以「尚未填寫」提示。
