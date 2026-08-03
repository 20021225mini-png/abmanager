# 進出異常案件 Follow 看板

使用 Python 與 Streamlit 建立的異常案件 MVP 看板。

## V11.2 更新

- 案件展開後先顯示緊湊案件摘要，再顯示處理 SOP；摘要改為四欄格狀排列。
- SOP 依模組收合，第一個判斷模組預設展開，後續流程需要時再展開。
- 新增「上架完仍有剩餘」五種判定結果：`IN-08A～IN-08E`。
- 未完成判定時顯示共用原因判斷；完成判定後依 `resolved_entry_node_id` 只顯示該結果的處理路徑。
- 包裝件少開後續維持待確認，其餘四條路徑依已確認資訊顯示。

## V11 原有功能

- 新增「案件判定與寫回」區塊；處理人員在看板選擇中文判定，程式在後端保存 `CLASSIFICATION_ID`。
- `JUDGEMENT_RESULT` 必填，用於記錄每筆案件實際查詢、盤點或確認到的結果。
- 儲存時同步更新 `UPDATED_AT`；案件仍為「待處理」時，自動推進為「處理中」。
- 寫回透過 Apps Script Web App 執行，Streamlit 不需持有 Google Sheet 帳號憑證。
- 保留 V10 的 SOP 明細、摘要、篩選、等待時間及台灣工作日規則。

## V10 原有功能

- 保留 V9 的案件列表、階段篩選、等待時間與台灣工作日判斷。
- 新增第二份 Google Sheet 作為 SOP 資料來源，不與 CASE 主表合併。
- 展開案件後顯示案件摘要與可收合的 SOP 模組。
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

- CASE：試算表 `1MTP...E7ecD4` 的 `CASE` 工作表（gid `1219451878`）；
  V11 的判定結果只寫回這張表。
- SOP：試算表 `1sW...oM_AM`，程式依工作表名稱唯讀：
  - `CLASSIFICATION_RULES`
  - `SOP_NODES`

兩張 SOP 工作表需保留現有程式欄名，並設定為部署環境可檢視。
`CLASSIFICATION_RULES` 可增加選用欄位 `resolved_entry_node_id`；同一現場情境
對應多個結果時，`entry_node_id` 指向共用判斷流程，完成分類後則從
`resolved_entry_node_id` 顯示該結果的處理路徑。

V11.2 部署前，先將隨附的 SOP 程式資料更新到第二份 Google Sheet：

1. 以同名工作表內容更新 `CLASSIFICATION_RULES`。
2. 以同名工作表內容更新 `SOP_NODES`。
3. 保留工作表名稱與第一列表頭；更新後按看板「重新整理」。

## CASE 寫回欄位

V11 會使用下列欄位；你目前已新增的兩欄請保留：

- `CLASSIFICATION_ID`：程式自動保存分類編號，例如 `IN-08E`。
- `JUDGEMENT_RESULT`：人員填寫的本案實際判斷結果。
- `UPDATED_AT`：儲存判定時更新時間。
- `STAGE`：原為「待處理」時推進為「處理中」。

`CASE_JUDGEMENT` 與 `ACTUAL_SCENARIO` 仍為可選欄位；畫面可透過
`CLASSIFICATION_ID` 從 `CLASSIFICATION_RULES` 取得這些資訊。

## Apps Script 寫回設定

1. 將 `gas/CaseJudgementApi.gs` 加入目前小工具使用的 Apps Script 專案。
2. 若專案原本已有 `doPost(e)`，保留原函式，並依註解將本介面的請求轉給 `handleCaseJudgementPost_(e)`；同一專案只能有一個 `doPost(e)`。
3. 在 Apps Script「專案設定 → 指令碼屬性」新增：

   ```text
   CASE_API_TOKEN = 自行設定的一組長字串
   ```

4. 將專案部署為 Web App：執行身分選擇自己，存取權限需讓 Streamlit 部署環境可以呼叫。
5. 在 Streamlit Cloud 的 App settings → Secrets 加入：

   ```toml
   CASE_WRITE_API_URL = "Apps Script Web App 的 /exec 網址"
   CASE_WRITE_API_TOKEN = "與指令碼屬性完全相同的長字串"
   ```

6. 重新啟動 Streamlit App。設定完成後，「儲存判定」按鈕會開放。

Apps Script 儲存前會確認案件編號唯一、分類代碼存在，以及 CASE 必要欄位完整；更新其他欄位時會保留案件原有資料。

## V10 匯入錯誤檢查

若看到下列匯入錯誤：

```text
from config.settings import SOP_NODES_CSV_URL, SOP_RULES_CSV_URL
```

本版已加入舊設定檔相容處理，不會再因缺少這兩個新常數而停止啟動。
仍請完整覆蓋新版的 `config/`、`data/`、`services/`、`ui/`、`app.py`
與 `requirements.txt`。這項錯誤發生在讀取 Google Sheet 之前，
與 CASE 新增欄位無關。

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
- 包裝件確認少開後的補開方式與結案條件，依 SOP 資料標示為待確認。
- 缺少來源資料的列表欄位維持空白；案件摘要以「尚未填寫」提示。
