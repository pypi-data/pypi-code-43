import copy
import emoji
import datetime
import dbstream
import pyodbc
import os

import requests

from pyzure.core.Column import create_columns, extend_column
from pyzure.core.Table import create_table
from pyzure.core.tools.print_colors import C
from pyzure.core.tools.progress_bar import print_progress_bar


def extract_emojis(str_):
    return ''.join(c for c in str_ if c in emoji.UNICODE_EMOJI or c in ('🏻', '🇺', '🇸', '🇬', '🇧'))


def replace_all_emoji(str_):
    for i in extract_emojis(str_):
        str_ = str_.replace(i, '???')
    return str_


class AzureDBStream(dbstream.DBStream):
    def __init__(self, instance_name):
        super().__init__(instance_name)
        self.instance_type_prefix = "AZURE"
        self.ssh_init_port = 6544

    def credentials(self):
        creds = super().credentials()
        alias = self.instance_type_prefix + "_" + self.instance_name
        if os.environ.get(alias + "_DRIVER_PATH"):
            driver = os.environ.get(alias + "_DRIVER_PATH")
        else:
            driver = os.environ.get(alias + "_DRIVER")
        creds.update({
            "uid": creds["user"],
            "server": creds["host"],
            "driver": driver,
            "TDS_Version": "7.2"
        })
        return creds

    def execute_query(self, query, data=None):
        connection_kwargs = self.credentials()
        con = pyodbc.connect(**connection_kwargs)

        cursor = con.cursor()

        try:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
        except Exception as e:
            cursor.close()
            con.close()
            raise e

        result = []
        try:
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                dict_ = dict()
                for i in range(len(columns)):
                    dict_[columns[i]] = row[i]
                result.append(dict_)
        except (pyodbc.ProgrammingError, TypeError):
            pass
        con.commit()
        cursor.close()
        con.close()
        return result

    def _send(
            self,
            data,
            replace,
            batch_size=1000,
            sub_commit=True):
        # Time initialization
        start = datetime.datetime.now()

        # Extract info
        rows = data["rows"]
        if not rows:
            return 0
        table_name = data["table_name"]
        columns_name = data["columns_name"]
        total_len_data = len(rows)

        # Clean table if needed
        if replace:
            cleaning_query = '''DELETE FROM ''' + table_name + ''';'''
            self.execute_query(cleaning_query)
            print(C.OKBLUE + "Cleaning Done" + C.ENDC)

        connection_kwargs = self.credentials()
        con = pyodbc.connect(**connection_kwargs)
        cursor = con.cursor()

        small_batch_size = int(2099 / len(columns_name))

        print("Initiate send_to_azure...")

        # Initialize counters
        boolean = True
        question_mark_pattern = "(%s)" % ",".join(["?" for i in range(len(rows[0]))])
        counter = 0
        while boolean:
            temp_row = []
            question_mark_list = []
            for i in range(small_batch_size):
                if rows:
                    value_list = rows.pop()
                    for i in range(len(value_list)):
                        if isinstance(value_list[i], str):
                            value_list[i] = replace_all_emoji(value_list[i])
                    temp_row.append(value_list)
                    question_mark_list.append(question_mark_pattern)
                else:
                    boolean = False
                    continue
            counter = counter + len(temp_row)
            # percent = round(float(counter * 100) / total_len_data)
            if sub_commit:
                suffix = "%% rows sent"
                print_progress_bar(counter, total_len_data, suffix=suffix)
            else:
                suffix = "% rows prepared to be sent"
                print_progress_bar(counter, total_len_data, suffix=suffix)
            data_values_str = ','.join(question_mark_list)
            columns_name_str = "\",\"".join(columns_name)
            inserting_request = '''INSERT INTO %s ("%s") VALUES %s ;''' % (
                table_name, columns_name_str, data_values_str)

            final_data = [y for x in temp_row for y in x]
            if final_data:
                try:
                    cursor.execute(inserting_request, final_data)
                except Exception as e:
                    cursor.close()
                    con.close()
                    raise e

            if sub_commit:
                con.commit()
        if not sub_commit:
            con.commit()
        cursor.close()
        con.close()

        print("data sent to azure")
        print("Total rows: %s" % str(total_len_data))
        print(C.BOLD + "Total time in seconds : %s" % str((datetime.datetime.now() - start).seconds) + C.ENDC)
        return 0

    def send_data(self,
                  data,
                  replace=True,
                  batch_size=1000,
                  other_table_to_update=None,
                  sub_commit=True
                  ):
        data_copy = copy.deepcopy(data)
        try:
            self._send(data, replace, sub_commit)
            if os.environ.get("SERVER_MONITORING_URL"):
                info = {
                    "instance_type": self.instance_type_prefix,
                    "instance_name": self.instance_name,
                    "schema_name": data["table_name"].split('.')[0],
                    "table_name": data["table_name"].split('.')[1],
                    "sent_rows": len(data["rows"]),
                    "sent_time": datetime.datetime.now()
                }

                requests.post(os.environ.get("SERVER_MONITORING_URL"), params=info)
        except Exception as e:
            print(e)
            if "invalid object name" in str(e).lower():
                create_table(
                    self,
                    data_copy
                )
            elif "invalid column name" in str(e).lower():
                create_columns(self, data_copy, other_table_to_update)
            elif "string or binary data would be truncated" in str(e).lower():
                extend_column(self, data_copy, other_table_to_update)
            else:
                raise e
            self.send_data(data=data_copy, replace=replace, batch_size=batch_size,
                           other_table_to_update=other_table_to_update, sub_commit=sub_commit)
