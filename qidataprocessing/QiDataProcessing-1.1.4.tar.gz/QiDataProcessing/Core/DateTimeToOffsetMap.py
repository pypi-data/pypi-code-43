import datetime
from QiDataProcessing.Core.CSharpUtils import QiCore


class OffsetCount:
    def __init__(self, offset, count):
        self._offset = offset
        self._count = count

    @property
    def offset(self):
        return self._offset

    @property
    def count(self):
        return self._count

    def to_string(self):
        msg = 'offset:' + str(self._offset)
        msg += 'count:' + str(self._count)
        return msg


class DateTimeToOffsetMap:
    def __init__(self, file_header):
        self._bucketSize = 32
        self._mask = self._bucketSize - 1
        self._fileHeader = None
        self._defaultKey = datetime.date
        self._keys = []
        self._values = []
        self._fileHeader = file_header

    def add(self, date_time, offset):
        pass

    def get_trading_day_offsets(self, begin_trading_day, end_trading_day, start_offset, end_offset, start_count, end_count):
        start = begin_trading_day
        end = end_trading_day
        while True:
            data = self.try_get(start, start_offset, start_count)
            if data[0]:
                start_offset = data[1]
                start_count = data[2]
                break
            start = start + datetime.timedelta(days=1)
            if start > end_trading_day:
                start_offset = -1
                end_offset = -1
                end_count = 0
                return False, start_offset, end_offset, start_count, end_count

        while True:
            data = self.try_get(end, end_offset, end_count)
            if data[0]:
                end_offset = data[1]
                end_count = data[2]
                break
            start = start + datetime.timedelta(days=1)
            if start > end_trading_day:
                start_offset = -1
                end_offset = -1
                return False, start_offset, end_offset, start_count, end_count

        return start_offset <= end_offset, start_offset, end_offset, start_count, end_count

    def get_start_offset(self, key, offset, count):
        if key == self._defaultKey:
            raise Exception("invalid date time")

        key = datetime.datetime(key.year, key.month, key.day)
        temp_key = self._defaultKey
        index = -1

        key_hash = self.hash_key(key)
        idx = key_hash & self._mask
        for i in range(0, self._bucketSize):
            if self._keys[idx] != self._defaultKey:
                if key == self._keys[idx]:
                    index = idx
                    break

                if key < self._keys[idx]:
                    if (temp_key == self._defaultKey) | (temp_key > self._keys[idx]):
                        temp_key = self._keys[idx]
                        index = idx

            idx += 1
            if idx == len(self._keys):
                idx = 0

        if index == -1:
            raise Exception("invalid date time")

        value = self._values[index]
        offset = value.Offset
        count = value.Count
        return offset, count

    def get_end_offset(self, key, offset, count):
        if key == self._defaultKey:
            raise Exception("invalid date time")

        key = datetime.datetime(key.year, key.month, key.day)
        temp_key = self._defaultKey
        index = -1

        key_hash = self.hash_key(key)
        idx = key_hash & self._mask
        for i in range(0, self._bucketSize):
            if self._keys[idx] != self._defaultKey:
                if key == self._keys[idx]:
                    index = idx
                    break

                if key > self._keys[idx]:
                    if (temp_key == self._defaultKey) | (temp_key < self._keys[idx]):
                        temp_key = self._keys[idx]
                        index = idx

            ++idx
            if idx == len(self._keys):
                idx = 0

        if index == -1:
            raise Exception("invalid date time")

        value = self._values[index]
        offset = value.Offset
        count = value.Count
        return offset, count

    def try_get(self, key, offset, count):
        if key == self._defaultKey:
            raise Exception("invalid date time")

        key = datetime.datetime(key.year, key.month, key.day)
        key_hash = self.hash_key(key)
        index = key_hash & self._mask
        found = False
        old_index = index
        while self._keys[index] != self._defaultKey:
            if self._keys[index] == key:
                found = True
                break

            key_hash += 1
            index = key_hash & self._mask
            if old_index == index:
                raise Exception("Unexpected collision is detected in DateTimeToOffsetMap")

        if found:
            value = self._values[index]
            offset = value.offset
            count = value.count
        else:
            offset = -1
            count = 0

        return found, offset, count

    def write(self, writer):
        for i in range(0, self._bucketSize):
            writer.write(self._keys[i].Ticks)
        for i in range(0, self._bucketSize):
            value = self._values[i]
            writer.write(value.offset)
            writer.write(value.count)

    def read(self, reader):
        for i in range(0, self._bucketSize):
            self._keys.append(QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64()))

        for i in range(0, self._bucketSize):
            self._values.append(OffsetCount(reader.read_int64(), reader.read_int32()))

    @staticmethod
    def hash_key(time):
        return time.day
