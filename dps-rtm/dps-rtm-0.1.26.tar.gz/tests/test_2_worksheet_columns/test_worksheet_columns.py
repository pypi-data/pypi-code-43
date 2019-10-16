# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.containers.worksheet_columns as wc
import rtm.main.excel as excel


def test_ws_cols_init(fix_path):
    path = fix_path
    worksheet_name = "test_worksheet"
    wb = excel.get_workbook(path)
    ws = excel.get_worksheet(wb, worksheet_name)
    worksheet_columns = wc.WorksheetColumns(ws)
    for ws_col in worksheet_columns:
        assert isinstance(ws_col, wc.WorksheetColumn)


if __name__ == "__main__":
    pass
