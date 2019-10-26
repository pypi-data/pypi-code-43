from .DataGenerator import DataGen

from .common.Common import stringify, write_to_text, get_default_file_name, \
    is_file, join_path_to_filename


class SQLTableGen(DataGen):
    def generate_create_table_query(self):
        """ generates the create table query """
        create_statement = "create table {table_name} (".format(table_name=self.table_name)
        for column_name in self.column_defs:
            column_metadata = self.column_defs[column_name]
            col_type = column_metadata["col_type"]

            varchar_length = column_metadata.get("varchar_length")
            if varchar_length:
                create_statement += "\n{column_name} {col_type}({varchar_length}),".format(
                    column_name=column_name,
                    col_type=col_type,
                    varchar_length = varchar_length
                    )
            else:
                create_statement += "\n{column_name} {col_type},".format(
                    column_name=column_name,
                    col_type=col_type
                    )

        create_statement = create_statement[: -1]
        create_statement += "\n);"
        return create_statement

    def generate_row(self, collection):
        """ returns a string of randomized data and collection which stores all
            previous values generated for each field """
        row = "("
        row_values, collection = self.generate_data(collection)
        for column_name in row_values:
            col_type = self.column_defs[column_name]["col_type"]
            if col_type == "varchar":
                val = stringify(row_values[column_name])
                row += val + ","
            else:
                val = row_values[column_name]
                row += str(val) + ","

        row = row[: -1]
        row += "),"
        return row, collection

    def generate_insert_query(self):
        """ generates the insert statement """
        insert_statement = "insert into {table_name} values".format(table_name=self.table_name)
        collection = {} # {col_name: [values]}

        for i in range(self.num_rows):
            row, collection = self.generate_row(collection)
            insert_statement += "\n{row}".format(row=row)

        insert_statement = insert_statement[: -1]
        insert_statement += "\n;"

        return insert_statement

    def generate_table_queries(self):
        """ generate create and insert queries, then save them to a .sql file
            located at self.path """
        create_table_query = self.generate_create_table_query()
        insert_query = self.generate_insert_query()
        query = create_table_query + "\n\n" + insert_query
        return query

    def build_sql_doc(self):
        """ generate SQL queries and write to file """
        table_queries = self.generate_table_queries()
        if is_file(self.path):
            outfile = self.path
        else:
            filename = get_default_file_name(self.table_name, "sql")
            outfile = join_path_to_filename(self.path, filename)
        write_to_text(outfile, table_queries)
