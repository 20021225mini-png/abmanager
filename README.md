# 進出異常案件 Follow 看板

使用 Python 與 Streamlit 建立的異常案件看板。

## V11.11 本機測試版：單層精簡控制列

- 未滿 24 小時顯示 `HH時 MM分`；滿 24 小時顯示 `X天 HH時`。
- 等待時間仍以完整秒數計算；CASE、CLOSED_AT 與原始資料不變。
- D+1／D+3 工作日警示規則維持不變。
- 第二列左側維持「全部／待處理／處理中／已結案」，右側以與案件等待時間相同的膠囊色框顯示「逾期／警示／正常」。
- 圖例門檻文字依序為「達 3 個工作日／達 1 個工作日／未滿 1 個工作日」，並採一般字重。
- 已結案案件的等待時間改為無底色粗體文字，避免與「1 個工作日內」的灰色色碼混淆。
- 移除「案件篩選」與「等待時間」兩個輔助標題，篩選選項與三組色碼說明直接併成同一個橫列。
- 控制列高度收至 34px，同時縮小上下留白，其他畫面與判斷邏輯維持不變。
- 等待時間文字是實際經過時間，色碼則依工作日截止時間判斷；例如 D+1 當日 17:00 前即使已超過 24 小時，仍維持正常色。
- 一般結案方式依最終處理結果判定完成，固定排在未結案件後方；完成時間優先讀取 `CLOSED_AT`，缺少時讀取 `UPDATED_AT`。
- 重新丈量與資訊修正案件仍以 `SHELVING_COMPLETED_AT` 判定完成，不會因一般更新時間而提早結案。
- 若一般結案案件同時缺少 `CLOSED_AT` 與 `UPDATED_AT`，仍歸入已結案，等待時間顯示「時間待補」。
- 展開案件後，左側顯示處理 SOP（約 60%），右側顯示案件編號、件號、異常類型與備註（約 40%）。
- SOP 依案件既有異常資訊自動比對；第一個模組預設展開，其餘模組可逐段查看。
- 畫面不顯示「案件判定與寫回」、分類選單、判斷結果輸入框及儲存按鈕。
- `judgement_service` 與 `case_writer` 參數仍由 `render_dashboard()` 接收，讓既有 V11.3 `app.py` 可直接使用；畫面程式不匯入或呼叫判定元件。
- `ui/judgement.py` 為不產生畫面的相容層；即使舊版 `dashboard.py` 意外呼叫，也不會顯示判定與寫回區塊。
- Streamlit 啟動紀錄會顯示 `ABMANAGER_DEPLOY_VERSION=V11.11-COMPACT-CONTROL-ROW-LOCAL`，用於確認實際啟動版本。
- 頁面更新時間旁同步顯示 `V11.11-COMPACT-CONTROL-ROW-LOCAL`。

## 資料來源

- CASE：原 CASE Google Sheet，程式維持唯讀載入案件資料。
- SOP：原 SOP Google Sheet，依下列工作表名稱讀取：
  - `CLASSIFICATION_RULES`
  - `SOP_NODES`

兩份試算表的網址與 ID 維持原設定。`CLASSIFICATION_ID`、
`JUDGEMENT_RESULT` 等既有 CASE 欄位可繼續保留，現行 UI 不要求填寫。

`data/google_sheet_sop_repository.py` 仍保留 `SOP_RULES_CSV_URL` 與
`SOP_NODES_CSV_URL` 的預設網址相容處理；這項設定與 CASE 新增欄位無關。

## 本機預覽方式

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Windows 若平常使用 `py` 啟動 Python，請改為：

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

瀏覽器會開啟 `http://localhost:8501`。預覽結束後在終端機按 `Ctrl+C`。
本機預覽不會更新 GitHub 或線上 Streamlit。

## 更新方式

若原 `abmanager` 已是 V11.10，本機確認畫面正確後，只需再放入：

- `ui/dashboard.py`
- `ui/styles.py`
- `tests/test_dashboard_layout.py`
- `tests/test_overdue_service.py`
- `VERSION.txt`

確認後才執行 `git add .`、`git commit` 與 `git push origin streamlit-app`。

## 專案分層

- `app.py`：組合相依元件並啟動
- `ui/`：Streamlit 畫面與外觀
- `services/`：等待時間、逾期、案件篩選、排序及 SOP 比對
- `data/`：Google Sheet 資料讀取
- `config/`：資料來源、文字、欄位與規則

## 等待與逾期規則

- 等待時間顯示實際經過時間，包含週末與假日。
- 顯示格式不含秒數，但程式內仍保留完整秒數供排序及計算使用。
- D+1 工作日截止後進入警示；D+3 工作日截止後判定逾期。
- 預設每日截止時間為 17:00。
- 台灣國定假日由 `holidays` 套件提供。
