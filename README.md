# 進出異常案件 Follow 看板

使用 Python 與 Streamlit 建立的異常案件看板。

## V11.4 現場查閱模式

- 案件主表、篩選、等待時間、逾期提示與原有配色維持不變。
- 展開案件後顯示案件編號、件號、異常類型、備註及對應處理 SOP。
- SOP 依案件既有異常資訊自動比對；第一個模組預設展開，其餘模組可逐段查看。
- 畫面不顯示「案件判定與寫回」、分類選單、判斷結果輸入框及儲存按鈕。
- `judgement_service` 與 `case_writer` 參數仍由 `render_dashboard()` 接收，讓既有 V11.3 `app.py` 可直接使用。
- 原判定與寫回程式保留在專案中，現行畫面不呼叫，方便日後依作業需求重新評估。

## 資料來源

- CASE：原 CASE Google Sheet，程式維持唯讀載入案件資料。
- SOP：原 SOP Google Sheet，依下列工作表名稱讀取：
  - `CLASSIFICATION_RULES`
  - `SOP_NODES`

兩份試算表的網址與 ID 維持原設定。`CLASSIFICATION_ID`、
`JUDGEMENT_RESULT` 等既有 CASE 欄位可繼續保留，現行 UI 不要求填寫。

`data/google_sheet_sop_repository.py` 仍保留 `SOP_RULES_CSV_URL` 與
`SOP_NODES_CSV_URL` 的預設網址相容處理；這項設定與 CASE 新增欄位無關。

## 執行方式

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## 更新方式

完整部署時，可將本壓縮檔內容放到 GitHub 專案根目錄後提交。
若目前線上版本已是 V11.3，相同結果也可只更新：

- `ui/dashboard.py`
- `ui/components.py`

提交後確認 `VERSION.txt` 第一行為 `V11.4-UI-READONLY`，再重新啟動 Streamlit App。

## 專案分層

- `app.py`：組合相依元件並啟動
- `ui/`：Streamlit 畫面與外觀
- `services/`：等待時間、逾期、案件篩選、排序及 SOP 比對
- `data/`：Google Sheet 資料讀取
- `config/`：資料來源、文字、欄位與規則

## 等待與逾期規則

- 等待時間顯示實際經過時間，包含週末與假日。
- D+1 工作日截止後進入警示；D+3 工作日截止後判定逾期。
- 預設每日截止時間為 17:00。
- 台灣國定假日由 `holidays` 套件提供。
