"""这是个方法名为print_lol 参数为任何的列表"""
def print_lol(the_list):
	"""对有内嵌列表的递归输出到屏幕"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
