from .DataGenerator import DataGen

from .common.Common import get_default_file_name, write_to_json, is_file, \
    join_path_to_filename


class JSONGen(DataGen):
    def add_row_to_prejson(self, row_data, pre_json):
        """ extract values from row_data and add them to pre_json """
        for column_name in row_data:
            val = row_data[column_name]
            if column_name not in pre_json:
                pre_json[column_name] = [val]
            else:
                pre_json[column_name].append(val)
        return pre_json

    def generate_document(self):
        """ build dict obj with column_name as key and values stored in list """
        collection = {}
        pre_json = {}
        for i in range(self.num_rows):
            row_values, collection = self.generate_data(collection)
            pre_json = self.add_row_to_prejson(row_values, pre_json)
        return pre_json

    def build_json_doc(self):
        pre_json = self.generate_document()
        if is_file(self.path):
            outfile = self.path
        else:
            filename = get_default_file_name(self.table_name, "json")
            outfile = join_path_to_filename(self.path, filename)
        write_to_json(outfile, pre_json)
