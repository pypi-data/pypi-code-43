import csv
import io
import sys
import os

class CsvFileHandler:

    @staticmethod
    def write_csv_file(file_path, csv_rows, header):
        if sys.version_info > (3, 0):
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                for csv_row in csv_rows:
                    writer.writerow(csv_row.to_array())
            csvfile.close()
        else:
            try:
                import unicodecsv
            except ImportError:
                print("[+] Install the unicodecsv module to write the CSV report")
                sys.exit(1)

            with open(file_path, "wb") as csvfile:
                writer = unicodecsv.writer(csvfile)
                writer.writerow(header)
                for csv_row in csv_rows:
                    writer.writerow(csv_row.to_array())
            csvfile.close()
