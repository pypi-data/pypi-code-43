from collections import deque
import pickle
from . import Pyraminx, PYRAMINX_CASE_PATH
from multiprocessing import Process, Manager, Queue

move_table = [[-1, -1, -1, -1, -1, -1, -1, -1, -1] for _ in range(933120)]
inverse_moves = [0, 2, 1, 4, 3, 6, 5, 8, 7]
move_table[0][0] = 0
NUMBER_OF_PROCESSES = 4


def setup():
    create_move_table()

    with open(PYRAMINX_CASE_PATH, 'wb') as f:
        for row in move_table[0:100]:
            print(row)
        pickle.dump(move_table, f, pickle.HIGHEST_PROTOCOL)


class MoveTableClass:
    def __init__(self):
        self.memory = deque()
        self.memory.append(0)


def add_entry(queue):
    while queue:
        node = queue.popleft()
        explore_node(queue)


def explore_node(queue):
    node = queue.get()
    state = Pyraminx.id_to_state(node)
    for i in range(1, 9):
        if move_table[node][i] > -1:
            continue
        transformation = Pyraminx.move_transformations[i - 1]
        new_state = Pyraminx.apply_move(state, transformation)
        new_id = Pyraminx.state_to_id(new_state)
        if move_table[new_id][0] == -1:
            move_table[new_id][0] = move_table[node][0] + 1
            queue.put(new_id)
        move_table[node][i] = new_id
        move_table[new_id][inverse_moves[i]] = node


def create_move_table():
    queue = Queue()
    queue.put(0)
    explore_node(queue)
    ps = []
    i = 0

    while not queue.empty():
        p = Process(target=explore_node, args=(queue,))
        print('Starting a process')
        p.start()
        ps.append(p)
        i += 1
    for p in ps:
        print('Joining a process')
        p.join()
    for row in move_table[:10]:
        print(i)
        #print(row[0])

    if False:
        p = Process(target=add_entry, args=(queue,))
        print('Starting a process')
        p.start()
        print('Joining a process')
        p.join()

    if False:

        processes = [Process(target=add_entry, args=(queue,)) for _ in range(NUMBER_OF_PROCESSES)]
        for p in processes:
            print('Starting a process')
            p.start()
        for p in processes:
            print('Joining a process')
            p.join()


if __name__ == '__main__':
    setup()
