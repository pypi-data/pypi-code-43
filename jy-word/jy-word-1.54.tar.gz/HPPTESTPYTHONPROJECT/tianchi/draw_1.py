# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/8/20 0020
__author__ = 'huohuo'
import json
from jy_word.File import File

import matplotlib.pyplot as plt

linjian = 'L0002_lingjian'
my_file = File()
data = my_file.read('%s.csv' % linjian)
for k in data[0].keys():
    print k
n = 0
plt.figure(figsize=(50, 500))
color = ['r', 'g', 'y', 'b']
for index, item in enumerate(data):
    dots = json.loads(item['外轮廓'])
    c_index = index % len(color)
    c = color[c_index]
    dotx, doty = [], []
    for dot in dots:
        dotx.append(dot[0])
        doty.append(dot[1])
    plt.plot(dotx, doty, '-', color=c)
    print item['零件号'], len(dots)

    plt.text(float(dot[0]), float(dot[1]), str(index))
    n += len(dots)
plt.xlabel('x')
plt.ylabel('y')
plt.title(linjian)
# plt.show()
plt.savefig('%s.png' % linjian, dpi=100)
print len(data), n
plt.show()

if __name__ == "__main__":
    pass
    

