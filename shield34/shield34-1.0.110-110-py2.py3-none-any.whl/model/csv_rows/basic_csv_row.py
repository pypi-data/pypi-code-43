import time


class BasicCsvRow(object):
    timestamp = ""
    header = []
    csv_file_name = ""

    def __init__(self, header, csv_file_name):
        self.timestamp = time.time()
        self.header = header
        self.csv_file_name = csv_file_name


def make_basic_csv_row(header, csv_file_name):
    basic_csv_row = BasicCsvRow(header, csv_file_name)
    return basic_csv_row
