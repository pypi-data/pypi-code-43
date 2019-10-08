from openpyxl import load_workbook


"""
# Example Function Run
# Function(dataDictionary, FileName)

# DICTIONARY {"SHEET": {"CELL": VALUE, "CELL": VALUE}}
datadict = {'Sheet1': {'D1': 123.4, 'D2': 567.8},
            'Sheet2': {'D1': 123.4, 'D2': 567.8},
            'Sheet3': {'D1': 123.4, 'D2': 567.8},
            }

# FULL PATH TO FILE
loc = os.getcwd()
fnme = 'MMW_BMP_Spreadsheet_Tool(Skippack).xlsx'
file = os.path.join(loc, fnme)

# Function Methods
writer = BMPxlsx.Writer(file)
input1 = {'Sheet1': {'D1': 13.4, 'D2': 47.8},
        'Sheet2': {'D1': 23.4, 'D2': 57.8},
        'Sheet3': {'D1': 33.4, 'D2': 67.8},
    }
writer.write(input1)
writer.close()

"""


class Writer:
    def __init__(self, file):
        self.file = file
        self.wb = load_workbook(self.file)

    def write(self, input):
        for key, value in input.iteritems():
            sheet = self.wb[key]
            for k, v in value.iteritems():
                sheet[k] = v
        self.wb.save(self.file)
        # return Writer(self.file)

    def close(self):
        self.wb.save(self.file)
        self.wb.close()


def main():
    message = "The Excel Writing Function instantiates an Excel file object. This object is opened, written to, then saved/closed."
    print(message)


if __name__ == '__main__':
    main()


