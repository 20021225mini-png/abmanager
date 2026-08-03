/**
 * V11 CASE 判定寫回介面。
 *
 * 使用前請在 Apps Script「專案設定 → 指令碼屬性」新增：
 * CASE_API_TOKEN = 與 Streamlit secrets 相同的長字串
 */

const CASE_API_CONFIG = Object.freeze({
  caseSpreadsheetId: '1MTPfTw0i-DWZbNzfXtKUOS56UI_xaedKIAzM9E7ecD4',
  caseSheetName: 'CASE',
  sopSpreadsheetId: '1sWFKUs2yDYKAyOTxPQeVqN6H9Ta00gq8VGOfzuoM_AM',
  classificationSheetName: 'CLASSIFICATION_RULES',
  timezone: 'Asia/Taipei',
});


/**
 * 若原專案已有 doPost(e)，請保留原函式，並在其中呼叫
 * handleCaseJudgementPost_(e)，不要同時保留兩個 doPost。
 */
function doPost(e) {
  return handleCaseJudgementPost_(e);
}


function handleCaseJudgementPost_(e) {
  const lock = LockService.getScriptLock();
  try {
    const body = parseCaseApiBody_(e);
    verifyCaseApiRequest_(body);

    lock.waitLock(10000);
    const result = updateCaseJudgement_(body);
    return caseApiJson_(Object.assign({ ok: true }, result));
  } catch (error) {
    return caseApiJson_({
      ok: false,
      message: error && error.message ? error.message : String(error),
    });
  } finally {
    if (lock.hasLock()) {
      lock.releaseLock();
    }
  }
}


function parseCaseApiBody_(e) {
  if (!e || !e.postData || !e.postData.contents) {
    throw new Error('請以 JSON POST 呼叫案件寫回介面。');
  }
  try {
    return JSON.parse(e.postData.contents);
  } catch (error) {
    throw new Error('寫回資料不是有效的 JSON。');
  }
}


function verifyCaseApiRequest_(body) {
  const expectedToken = PropertiesService.getScriptProperties()
    .getProperty('CASE_API_TOKEN');

  if (!expectedToken) {
    throw new Error('Apps Script 尚未設定 CASE_API_TOKEN。');
  }
  if (!body || String(body.token || '') !== expectedToken) {
    throw new Error('案件寫回驗證失敗。');
  }
  if (String(body.action || '') !== 'update_case_judgement') {
    throw new Error('不支援的案件寫回動作。');
  }

  const caseNo = String(body.case_no || '').trim();
  const classificationId = String(body.classification_id || '').trim();
  const judgementResult = String(body.judgement_result || '').trim();
  if (!caseNo || !classificationId || !judgementResult) {
    throw new Error('案件編號、分類判定與實際判斷結果皆須填寫。');
  }
  if (!classificationExists_(classificationId)) {
    throw new Error('分類編號不存在於 CLASSIFICATION_RULES。');
  }
}


function classificationExists_(classificationId) {
  const spreadsheet = SpreadsheetApp.openById(
    CASE_API_CONFIG.sopSpreadsheetId
  );
  const sheet = spreadsheet.getSheetByName(
    CASE_API_CONFIG.classificationSheetName
  );
  if (!sheet) {
    throw new Error('找不到 CLASSIFICATION_RULES 工作表。');
  }

  const values = sheet.getDataRange().getDisplayValues();
  if (values.length < 2) {
    return false;
  }
  const headers = values[0].map(value => String(value).trim());
  const idIndex = headers.indexOf('classification_id');
  if (idIndex < 0) {
    throw new Error('CLASSIFICATION_RULES 缺少 classification_id 欄位。');
  }
  return values.slice(1).some(
    row => String(row[idIndex] || '').trim() === classificationId
  );
}


function updateCaseJudgement_(body) {
  const spreadsheet = SpreadsheetApp.openById(
    CASE_API_CONFIG.caseSpreadsheetId
  );
  const sheet = spreadsheet.getSheetByName(CASE_API_CONFIG.caseSheetName);
  if (!sheet) {
    throw new Error('找不到 CASE 工作表。');
  }

  const range = sheet.getDataRange();
  const values = range.getDisplayValues();
  if (values.length < 2) {
    throw new Error('CASE 工作表目前沒有可更新的案件。');
  }

  const headers = values[0].map(value => String(value).trim());
  const requiredHeaders = [
    'CASE_NO',
    'UPDATED_AT',
    'STAGE',
    'CLASSIFICATION_ID',
    'JUDGEMENT_RESULT',
  ];
  const columnIndex = {};
  requiredHeaders.forEach(header => {
    const index = headers.indexOf(header);
    if (index < 0) {
      throw new Error(`CASE 工作表缺少欄位：${header}`);
    }
    columnIndex[header] = index;
  });

  const caseNo = String(body.case_no).trim();
  const matchedRows = [];
  for (let index = 1; index < values.length; index += 1) {
    if (String(values[index][columnIndex.CASE_NO] || '').trim() === caseNo) {
      matchedRows.push(index + 1);
    }
  }
  if (matchedRows.length === 0) {
    throw new Error(`找不到案件：${caseNo}`);
  }
  if (matchedRows.length > 1) {
    throw new Error(`案件編號重複，請先確認 CASE：${caseNo}`);
  }

  const rowNumber = matchedRows[0];
  const currentStage = String(
    values[rowNumber - 1][columnIndex.STAGE] || ''
  ).trim();
  const nextStage = (!currentStage || currentStage === '待處理')
    ? '處理中'
    : currentStage;
  const updatedAt = new Date();

  sheet.getRange(rowNumber, columnIndex.CLASSIFICATION_ID + 1)
    .setValue(String(body.classification_id).trim());
  sheet.getRange(rowNumber, columnIndex.JUDGEMENT_RESULT + 1)
    .setValue(String(body.judgement_result).trim());
  sheet.getRange(rowNumber, columnIndex.UPDATED_AT + 1)
    .setValue(updatedAt)
    .setNumberFormat('yyyy-mm-dd hh:mm:ss');
  sheet.getRange(rowNumber, columnIndex.STAGE + 1).setValue(nextStage);
  SpreadsheetApp.flush();

  return {
    case_no: caseNo,
    classification_id: String(body.classification_id).trim(),
    judgement_result: String(body.judgement_result).trim(),
    updated_at: Utilities.formatDate(
      updatedAt,
      CASE_API_CONFIG.timezone,
      'yyyy-MM-dd HH:mm:ss'
    ),
    stage: nextStage,
  };
}


function caseApiJson_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
