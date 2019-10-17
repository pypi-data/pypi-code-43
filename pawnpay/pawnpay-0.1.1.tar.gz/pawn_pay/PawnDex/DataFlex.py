#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification

import json
import os
import struct
import warnings
from datetime import datetime, timedelta


class Column:
    def __init__(self):
        self.size = 0
        self.type = 0
        self.offset = 0
        self.name = ""
        self.number = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return json.dumps({
            'number': self.number,
            'name': self.name,
            'type': self.type,
            'offset': self.offset,
            'size': self.size,
        }, sort_keys=True, indent=4)


class Dataflex:
    def __init__(
            self,
            file_path,
            block_size=int(),  # SHOULD be 512 bytes but it can be arbitrary
            ignore_columns=[],
            debug=False
    ):
        self.data = None
        self.block_size = block_size
        self.columns = None
        self.column_tags = None
        self.rows = []
        self.debug = debug

        self.ignore_columns = ignore_columns  # indexes or names
        self.file_path = file_path
        self.read_file()

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return self.rows

    def get_record_length(self):
        return self.byte_to_int(self.get_bytes(0x9A, 2))

    def read_file(self):
        if self.data:
            return

        file = open(self.file_path, 'rb')
        self.output("Opened file:\t%s" % self.file_path)
        self.output("Size in bytes:\t%s" % os.path.getsize(self.file_path))
        self.data = file.read()

        self.block_size = self.get_record_length()
        self.output("BLOCK SIZE " + str(self.block_size))

        self.parse_data()
        file.close()

    def parse_data(self):
        if self.rows:
            return

        self.output("Number of columns:\t%d" % self.get_total_columns())
        self.output("Number of rows:\t%d" % self.get_total_records())

        # get the offset where records begin
        start = 0
        offset = self.get_total_columns()
        while start < offset:
            start += self.block_size

        self.output("Reading records starting from:\t{}".format(start))
        # self.get_columns()

        # record_size = 0
        # for col in self.columns:
        #     record_size += col.size

        # self.output("Record size from field defs:\t{}".format(record_size))

        rows = []
        for line in range(self.get_total_records()):
            row = {'RECORD_NUM': line + 1}
            self.output("Working row #%d" % line)
            for col in self.get_columns():
                self.output("NAME:\t%s" % col.name)
                self.output("TYPE:\t%s" % col.type)
                self.output("SIZE:\t%d" % col.size)
                if (col.number in self.ignore_columns or
                        col.name in self.ignore_columns):
                    self.output("Ignoring Column: %s" % col.name)
                    continue
                offset = col.offset - 1
                offset = 0x0C00 + start + offset + (line * self.block_size)
                value = None

                self.output("OFFSET:\t%d" % offset)

                data = self.get_bytes(offset, col.size)

                self.output("BINARY:\t%s" % ','.join(map(bin, data)))

                if col.type == 'string':
                    value = self.byte_to_string(data).strip()
                elif col.type == 'int':
                    value = self.byte_to_int(data)
                elif col.type == 'mixed':
                    # living on the EDGE >:D
                    value = self.byte_to_string(data).strip()
                elif col.type == 'date':
                    try:
                        value = self.bytes_to_date(data)
                    except Exception:
                        value = '09-17-1642'
                        pass
                else:
                    self.output("UNKNOWN TYPE")
                    # try a string I guess ¯\_(ツ)_/¯
                    value = self.byte_to_string(data).strip()

                self.output("VALUE:\t%s" % str(value))
                self.output("====================================")

                # null fields
                if value == -1 or value == '':
                    value = None

                row.update({col.name: value})
            rows.append(row)
        self.rows = rows

    def get_columns(self):
        if self.columns:
            return self.columns

        tags = self.get_tags()

        size_offset = 3
        type_offset = 4

        columns = []

        base_offset = 0x2E0

        for i in range(self.get_total_columns()):
            col = Column()
            col.number = i

            try:
                col.name = tags[i]
            except:
                col.name = "Column %d" % i

            offset = i * 8

            current_offset = base_offset + offset

            col.offset = self.byte_to_int(self.get_bytes(current_offset, 2))
            col.size = self.byte_to_char(
                self.get_bytes(current_offset + size_offset, 1)
            )
            col.type = self.byte_to_char(
                self.get_bytes(current_offset + type_offset, 1)
            )

            # type to string
            if col.type == 0:
                col.type = 'string'
            elif col.type == 1:
                col.type = 'int'
            elif col.type == 2:
                col.type = 'date'
            elif col.type == 3:
                col.type = 'mixed'

            columns.append(col)

        self.columns = columns

        # self.output("COLUMNS:")
        # self.output(columns)

        return self.columns

    def get_tags(self):
        if self.column_tags:
            return self.column_tags

        tag_file = self.file_path[:-3] + 'tag'
        if os.path.isfile(tag_file):
            self.output("Loading tags from %s" % tag_file)
            with open(tag_file, 'r') as tags:
                column_tags = []
                for line in tags:
                    column_tags.append(line.strip())
                self.column_tags = column_tags
        else:
            self.output("No tag file found for %s" % tag_file)
        return self.column_tags

    def get_bytes(self, start, length):
        return self.data[start:(start + length)]

    def bytes_to_date(self, _bytes):
        EPOCH = 700000  # 1642-09-17
        date = datetime.strptime('1642-09-17', '%Y-%m-%d')

        str_buffer = ''
        for byte in _bytes:
            str_buffer += self.get_packed_bcd(byte)

        # 3 day difference comes from where?
        date_offset = int(str_buffer) - EPOCH - 3

        self.output("Date offset:\t{}".format(date_offset))

        if (date_offset < 0):
            # date so far in the past it might have been
            # when this software was released
            # probably just a null field
            return None

        value = date + timedelta(days=date_offset)
        return value.strftime('%m-%d-%Y')

    def get_packed_bcd(self, byte):
        str_buffer = ''
        n1 = str(byte >> 4)
        n2 = str(byte & 0xF)
        # print("NIBBLE 1:\t%s" % n1)
        # print("NIBBLE 2:\t%s" % n2)
        str_buffer += n1
        str_buffer += n2
        return str_buffer

    def get_unpacked_bcd(self, _bytes):
        # get last 4 bytes
        str_buffer = ''
        if type(_bytes) is 'str':
            for byte in _bytes:
                str_buffer += str(byte & 0xF)
        else:
            str_buffer += str(_bytes & 0xF)
        return str_buffer

    def byte_to_int(self, data):
        # print("DECOING INT:\t%s" % ','.join(map(bin, data)))
        val = 0

        if len(data) == 1:
            # PACKED BINARY CODED DECIMAL
            # two 4-bit integers
            val = self.get_packed_bcd(data[0])

        elif len(data) == 2:
            # 16-bit integer
            val = struct.unpack('H', data)[0]
        elif len(data) >= 3:
            # PACKED BINARY CODED DECIMAL
            # first byte is unpacked for some reason
            str_buffer = ''
            str_buffer += str(self.get_unpacked_bcd(data[0]))
            for byte in data[1:]:
                str_buffer += str(self.get_packed_bcd(byte))
            val = int(str_buffer)
        # print("INT:\t%s" % val)
        return val

    def byte_to_char(self, data):
        return struct.unpack('B', data)[0]

    def byte_to_string(self, data):
        # for bit in data:
        #     ord
        return data.decode('utf-8', 'ignore')

    def get_total_columns(self):
        return self.byte_to_int(self.get_bytes(0xA5, 2))

    def get_total_records(self):
        return self.byte_to_int(self.get_bytes(0x0, 2))

    def output(self, string):
        if (self.debug):
            print(string)
