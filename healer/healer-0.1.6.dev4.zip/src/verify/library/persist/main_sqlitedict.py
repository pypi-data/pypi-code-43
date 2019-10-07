
import os
import time
from dataclasses import dataclass

this_dir = os.path.abspath(os.path.dirname(__file__))

data_path = f"{this_dir}/data.db"


@dataclass
class ValueEntry:
    value:int
    entry_list:str


from sqlitedict import SqliteDict

data_dict = SqliteDict(data_path, autocommit=True)

data_dict['key-1'] = "hello-kitty-1"
data_dict['key-2'] = "hello-kitty-2"
data_dict['key-3'] = ValueEntry(10, 'hello-again')

print(data_dict)
print(f"size={len(data_dict)}")

# for key, value in data_dict.items():
#     print(f"{key} = {value}")

data_dict.clear()
print(f"size={len(data_dict)}")

start_time = time.time()

count = 100000

for index in range(count):
    key = f"index-{index}"
    value = ValueEntry(key, f"hello-{key}")
    data_dict[key] = value

delta_time = time.time() - start_time
unit_time = delta_time / count

print(f"unit_time: {int(unit_time * 1000*1000)} us")

print(f"size={len(data_dict)}")
