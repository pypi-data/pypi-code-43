"""这是个方法名为print_lol 参数为任何的列表"""
def print_lol(the_list, indent=False, level=0):
	"""第一个参数是列表，对有内嵌列表的递归输出到屏幕,各占一行，
	   第二个参数表示是否需要缩进，
	   第三个参数进行Tab缩进处理"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item,indent,level+1)
		else:
			if indent:
				print("\t"*level,end='')
				#for index in range(level):
				#print("\t",end='')
			print(each_item)
