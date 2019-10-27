
import xlrd
from pymongo import MongoClient
from os.path import abspath, basename


def xl2mg(file, database, url="mongodb://localhost:27017/"):
    """
    file: input Excel file.
    database: the prefered database name
    url: Local, Server or Atlas cluster url, by default url="mongodb://localhost:27017/"

    """

    # get absolute xl_file path
    abs_xl_file_path = abspath(file)

    # create a new MongoDB collection 
    tmp_client =  MongoClient(url)
    tmp_db = tmp_client[str(basename(database))]

    # open the workbook
    xlf = xlrd.open_workbook(abs_xl_file_path, on_demand=True)

    # get sheet_names list
    sheets_list = xlf.sheet_names()

    for sheet_name in sheets_list:

        # delete if exist and then create a new collection
        tmp_client.drop_database(sheet_name)
        tmp_col = tmp_db[sheet_name]

        # load the sheet
        xl_sheet = xlf.sheet_by_name(sheet_name)

        # get all header row --> will be the MongoDB document fields
        headerCells = xl_sheet.row(0)
        keysList = []
        for e in headerCells:
            keysList.append(e.value.replace('.','~'))
        del(headerCells)
        
        # get col_number and row_number
        col_number = xl_sheet.ncols
        row_number = xl_sheet.nrows

        # for each row
        for rowIndex in range(1,row_number):
            # create new empty dict --> document
            doc = {}
            # for each cell
            for colIndex in range(col_number):
                doc[keysList[colIndex]] = str(xl_sheet.cell(rowIndex,colIndex).value)
            tmp_col.insert_one(doc)
