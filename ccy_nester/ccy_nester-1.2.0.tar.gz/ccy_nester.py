"""
这是nester.py 模块，提供了一个名为print_lol()的函数，
这个函数的作用是打印列表，其中有可能包含（也可能不包含）嵌套列表。
"""


def print_lol(this_list, level=0):
    
    levelParam = level
    if level > 0:
        levelParam = level + 1

    """
    这个函数取一个位置参数，名为the_list,这可以是任何Python
    列表（也可以是包含嵌套列表的列表）。所指定的列表中的每个数据项
    会（递归地）输出到屏幕上，各数据项各占一行。
    """
    for each_item in this_list:
        if isinstance(each_item, list):
            print_lol(each_item, levelParam)
        else:
            for num in range(levelParam - 1):
                if num > 0:
                    print('\t', end='')
            print(each_item)


print_lol(
    ['Palin', 'Cleese', 'Idle', [1, 2, True]],
    -1
)
