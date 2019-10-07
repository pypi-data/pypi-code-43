'''
    这是“nester.py”模块，提供了一个名为print_lol()的函数，这个函数的作用是
打印列表，其中有可能包含（也可能不包含）嵌套列表。
'''
def print_lol(the_list):
    '''
        这个函数取一个位置参数，名为“the_list”，这可以是任何Python列表（
    也可以是包含嵌套列表的列表）。所指定的列表中的每个数据项会（递归地）输出
    到屏幕上，各数据项各占一行。
    '''
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
#print_lol(movies)#我就是不认真，在模块里就调用了函数而且函数里还给了参数
#结果在调用该模块时一直出错，我折腾了好一阵才找到原因