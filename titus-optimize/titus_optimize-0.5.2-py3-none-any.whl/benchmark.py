import math
from random import random

import numpy as np


def visualize(alloc, num_sockets = 2):
    d = len(alloc[0])
    n = num_sockets
    b = d // n

    rows = []
    for t in range(n):
        S1 = [' '] * (b // 2)
        S2 = [' '] * (b // 2)
        for job_id, job in enumerate(alloc):
            for i in range(t * b, (t + 1) * b):
                if job[i] == 1:
                    if (i - b) % 2 == 0:
                        if S1[(i - b) // 2] == ' ':
                            S1[(i - b) // 2] = str(job_id + 1)
                        else:
                            S1[(i - b) // 2] += '/' + str(job_id + 1)
                    else:
                        if S2[(i - b) // 2] == ' ':
                            S2[(i - b) // 2] = str(job_id + 1)
                        else:
                            S2[(i - b) // 2] += '/' + str(job_id + 1)
        rows.append(S1)
        rows.append(S2)
    max_cell_size = np.max([len(e) for c in rows for e in c])
    formatted_rows = []
    for row in rows:
        formatted_rows.append('| ' + ' | '.join([e.ljust(max_cell_size) for e in row]) + ' |')
    row_len = len(formatted_rows[0])
    print('-' * row_len)
    for i, row in enumerate(formatted_rows):
        if i == 2:
            print('| ' + '-' * (row_len - 4) + ' |')
        print(row)
    print('-' * row_len)