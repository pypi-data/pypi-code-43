import logging
import csv

class Column(object):

    # constructor
    def __init__(self, file, encoding):
        self.log = logging.getLogger(__name__)
        self.file = file
        self.encoding = encoding

    def getRows(self, columns, option=None, param=None):

        headers = self.hasColumns(columns)
        unique = []
        rows = []
        with open(self.file, encoding=self.encoding) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                if (option == 'key' and param != None):
                    if (param == '*'):
                        for header in headers:
                            for column in row:
                                if (header == column and row[column] not in unique and row[column] != ''):
                                    rows.append(row[column])
                                    unique.append(row[column])
                    elif (row[str(param)] not in unique):
                        rows.append(self.getRow(headers, row))
                        unique.append(row[str(param)])
                elif (option != 'key'):
                    rows.append(self.getRow(headers, row))
        return rows
    
    def getRow(self, headers, row):
        obj = {}
        for header in headers:
            obj[str(header)] = row[str(header)]

        return obj

    def hasColumns(self, columns):
        headers = []

        # require the first line of the file for validation
        with open(self.file, encoding=self.encoding) as f:
            reader = csv.DictReader(f, delimiter=',')
            row = next(reader)

            for column in columns:
                header = self.hasColumn(column, row)
                if (header != ''):
                    headers.append(header)

        return headers

    def hasColumn(self, column, row):
        has = column
        try:
            # an exception will throw if this column header doesn't exist
            row[str(column)]
        except:
            # when exception is thrown we'll set this to an empty string
            has = ''
        return has


            # columns is an array
            # Created options for unique:
            # option: search for unique on the key
            #  all | combined allows for
            # currently only supports: unique|keyword where keyword is the value that will be used for deduplication
            # def getRows(self, columns, option=None, param=None):
            #
            #     headers = self.hasColumns(columns)
            #     unique = []
            #     rows = []
            #     with open(self.file, encoding=self.encoding) as f:
            #         reader = csv.DictReader(f, delimiter=',')
            #         for row in reader:
            #             if (option == 'key' and row[str(param)] not in unique):
            #                 rows.append(self.getRow(headers, row))
            #                 unique.append(row[str(param)])
            #             elif (option != 'key'):
            #                 rows.append(self.getRow(headers, row))
            #     return rows
