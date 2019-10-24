from shield34_reporter.model.csv_rows.basic_csv_row import BasicCsvRow


class ReportCsvRow(BasicCsvRow):
    rowType = None
    rowSubType = None

    def __init__(self, row_sub_type):
        self.rowSubType = row_sub_type
        super(ReportCsvRow, self).__init__([{"timestamp", "row_sub_type", "row_type",  "row_value"}], "report.csv")



