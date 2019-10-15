"""这是“nester.py”模块，提供了一个名为print_lo1()的函数，这个函数的作用是打印列表，其中有肯能
包含(也可能不包含)嵌套列表。"""
def print_lo1(lis):
	"""这个函数取一个位置参数，名为"the_list"，这可以是任何python列表（也可以是包含嵌套列表的
	列表）。所指定的列表中的每个数据项会（递归地）输出到屏幕上，个数据项各站一行"""
	for i in lis:
		if isinstance(i,list):
			print_lo1(i)
		else:
			print(i)