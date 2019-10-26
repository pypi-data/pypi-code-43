from .DataGenerator import DataGen

from .common.Common import write_to_csv, get_default_file_name, is_file, join_path_to_filename


class CSVGen(DataGen):
    def generate_row(self, collection):
        """ returns a tuple of randomized data and collection which stores all
            previous values generated for each field """
        output = []
        row_values, collection = self.generate_data(collection)
        for column_name in row_values:
            val = row_values[column_name]
            output.append(val)
        return tuple(output), collection

    def generate_document(self):
        """ generate a list of tuples """
        collection = {}
        column_names = tuple(self.column_defs.keys())
        pre_csv = [column_names]
        for i in range(self.num_rows):
            row, collection = self.generate_row(collection)
            pre_csv.append(row)
        return pre_csv

    def build_csv_doc(self):
        pre_csv = self.generate_document()
        if is_file(self.path):
            outfile = self.path
        else:
            filename = get_default_file_name(self.table_name, "csv")
            outfile = join_path_to_filename(self.path, filename)
        write_to_csv(outfile, pre_csv)
