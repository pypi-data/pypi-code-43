import csv


class CsvFileHandler:

    @staticmethod
    def write_csv_file(file_path, csv_rows, header):
        with open(file_path, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(header)
            for csv_row in csv_rows:
                writer.writerow(csv_row.to_array())

        csvFile.close()
