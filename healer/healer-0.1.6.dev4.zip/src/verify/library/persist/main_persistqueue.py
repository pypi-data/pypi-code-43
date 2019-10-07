
import os
import persistqueue

this_dir = os.path.abspath(os.path.dirname(__file__))

path = f"{this_dir}/data.test"

perque = persistqueue.SQLiteAckQueue(path=path)

perque.put('str1')
perque.put('str1')
perque.put('str2')
perque.put('str2')

print(perque)
print(perque.size)

while perque.size:
    item = perque.get()
    print(perque.size)
    print(item)
#     perque.ack(item)

