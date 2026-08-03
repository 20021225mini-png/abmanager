"""Google Sheet CSV 欄位與別名讀取測試。"""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from data.google_sheet_repository import GoogleSheetCaseRepository
from data.google_sheet_sop_repository import GoogleSheetSopRepository


class GoogleSheetRepositoryTest(TestCase):
    def test_case_optional_columns_accept_lowercase_aliases(self) -> None:
        with TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "case.csv"
            csv_path.write_text(
                "CASE_NO,CREATED_AT,PART_NO,QTY,SITUATION,ORIGINAL_CART,"
                "STAGE,LAYER,FLOOR,classification_id,case_judgement,"
                "actual_scenario,judgement_result\n"
                "A001,2026-08-03 10:00,P001,1,地上撿到,C01,待處理,中,2F,"
                "IN-10,可正常使用,異常台車區,進異常流程\n",
                encoding="utf-8",
            )

            row = GoogleSheetCaseRepository(str(csv_path)).load_cases().rows[0]

        self.assertEqual(row["CLASSIFICATION_ID"], "IN-10")
        self.assertEqual(row["CASE_JUDGEMENT"], "可正常使用")
        self.assertEqual(row["ACTUAL_SCENARIO"], "異常台車區")
        self.assertEqual(row["JUDGEMENT_RESULT"], "進異常流程")

    def test_sop_repository_accepts_program_sheet_columns(self) -> None:
        with TemporaryDirectory() as temp_dir:
            rules_path = Path(temp_dir) / "rules.csv"
            nodes_path = Path(temp_dir) / "nodes.csv"
            rules_path.write_text(
                "classification_id,report_scenario,main_type,sub_type,"
                "display_type,condition_text,entry_node_id\n"
                "IN-10,地上撿到,其他,地上撿到,地上撿到,確認可用性,SOP-01-S01\n",
                encoding="utf-8",
            )
            nodes_path.write_text(
                "node_id,sop_id,step_no,flow_name,node_type,instruction,"
                "required_data,option_order,option_label,next_type,"
                "next_node_id,end_result,pending_confirmation\n"
                "SOP-01-S01,SOP-01,1,可用性確認,TERMINAL,確認可用性,"
                "零件號,1,完成,END,,結案,\n",
                encoding="utf-8",
            )

            dataset = GoogleSheetSopRepository(
                rules_csv_url=str(rules_path),
                nodes_csv_url=str(nodes_path),
            ).load_sop_data()

        self.assertEqual(dataset.rules[0]["classification_id"], "IN-10")
        self.assertEqual(dataset.nodes[0]["node_id"], "SOP-01-S01")
