# -*- coding:utf-8 -*- 
# Date: 2018-03-13 17:42:14
# Author: dekiven

import os

from DKVTools.Funcs import *

if isPython3() :
	import tkinter as tk
	import tkinter.ttk as ttk
else :
	import Tkinter as tk
	import ttk
	# import Tkinter.ttk as ttk
	
#import sys 
#reload(sys)
#sys.setdefaultencoding('utf-8')

class DataTableView(ttk.Treeview) :
	'''DataTableView
ttk.Treeview show 属性可以取值：'tree', 'headings', None。说明如下：
'tree' :	不显示左边和顶端的表头
'headings':	不显示左边的表头
None:		左边和顶端的表头均显示（这种情况空表会多一列用于显示左边表头，显示顶端表头后第一列的位置是空，第二列显示设置的第一个表头内容）
	'''
	def __init__(self, *args, **dArgs) :
		ttk.Treeview.__init__(self, *args, **dArgs)
		self.heads = None
		self.data = None
		self.rowHeads = None

		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		scrollV = ttk.Scrollbar(self)
		scrollV.grid(column=1, sticky=(tk.N, tk.S))
		scrollV.config(command=self.yview)
		self.scrollbarV = scrollV

		self.config(yscrollcommand=scrollV.set)

		self.__registEvents()

		# scrollH = tk.Scrollbar(self, orient=tk.HORIZONTAL)
		# scrollH.grid(row=1, sticky=(tk.W, tk.E))
		# scrollH.config(command=self.xview)
		# self.scrollbarH = scrollH

		# self.config(yscrollcommand=scrollV.set, xscrollcommand=scrollH.set)

	def setHeads(self, heads) :
		self.heads = heads
		l = len(heads)
		if l > 0 :
			c = [str(i) for i in range(1, l+1)]
			self.configure(columns=c)
			i = 0
			for h in heads :
				i += 1
				self.column(str(i), width=20, anchor='center')
				self.heading(str(i), text=str(h))

	def setData(self, data, heads=None, rowHeads=None) :
		if isinstance(heads, list) or isinstance(heads, tuple) :
			self.setHeads(heads)
		self.data = data
		self.rowHeads = rowHeads
		self.clearItems()
		self.__updateData()

	def clearItems(self) :
		[self.delete(i) for i in self.get_children('')]

	def __updateData(self, *args, **dArgs) :
		data = self.data
		rowHeads = self.rowHeads or ()
		lenRH = len(rowHeads)
		if data :
			for i in range(0,len(data)) :
				d = data[i]
				text = None
				if i < lenRH :
					text = rowHeads[i]
				# print(d)
				# print(type(d))
				if text :
					self.insert('', 'end', text=text, values=list(d), tags=['T_ALL',])
				else :					
					self.insert('', 'end', values=list(d), tags=['T_ALL',])


	def movetoPercentV(self, percent) :
		self.yview('moveto', str(percent/100.0))

	def moveToTop(self) :
		self.movetoPercentV(0)

	def moveToBottom(self) :
		self.movetoPercentV(100)

	def moveUpOneStep(self) :
		self.yview(tk.SCROLL, -1, tk.UNITS)

	def moveDownOneStep(self) :
		self.yview(tk.SCROLL, 1, tk.UNITS)

	def __registEvents(self) :
		# TODO:注册鼠标中键滑动监听
		self.bind('<MouseWheel>', self.__on_mouseWheel)
		self.bind('<<TreeviewSelect>>', self.__on_select)

		# self.event_add('<<new_test_event>>', '<Motion>', '<Key>', '<Button>')
		self.event_add('<<new_test_event>>', '<Motion>')

		self.tag_bind('T_ALL', '<<new_test_event>>', self.__on_test)

	def __on_mouseWheel(self, event) :
		# print(event.delta)
		if self.focus :
			if event.delta > 0 :
				self.moveUpOneStep()
			else :
				self.moveDownOneStep()

	def __on_select(self, *args) :
		print(args[0].type, args)

	def __on_test(self, *args, **dArgs) :
		# print(args[0].type, dArgs)
		x = args[0].x
		y = args[0].y
		print(x, y, self.identify_element(x, y), self.identify_column(x), self.identify_row(y))

def __main() :
	_tk = tk.Tk()
	_tk.columnconfigure(0, weight=1)
	_tk.rowconfigure(0, weight=1)
	tv = DataTableView(_tk, show="headings")
	# tv = DataTableView(_tk, show="tree")
	# tv = DataTableView(_tk, show=None)
	tv.pack(expand=tk.YES, fill=tk.BOTH)
	tv.setHeads(['a', 'b', 'c'])
	d = [('1', '2', '3'),('2', '2', '3'),('3', '2', '3')]
	# tv.clearItems()
	tv.setData(d)
	# tv.__updateData()
	tv.mainloop()

if __name__ == '__main__':
	__main()
