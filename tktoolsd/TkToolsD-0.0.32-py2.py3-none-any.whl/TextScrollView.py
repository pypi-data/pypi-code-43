# -*- coding:utf-8 -*- 
# Date: 2018-03-13 11:11:19
# Author: dekiven

import os
from DKVTools.Funcs import *

if isPython3() :
	import tkinter as tk
	import tkinter.ttk as ttk
else :
	import Tkinter as tk
	import ttk


#import sys 
#reload(sys)
#sys.setdefaultencoding('utf-8')

class TextScrollView(tk.Text) :
	'''TextScrollView has a scrollbar that gird(1,0)
	'''

	def __init__(self, *args, **dArgs) :
		tk.Text.__init__(self, *args, **dArgs)

		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		scrollV = ttk.Scrollbar(self)
		scrollV.grid(column=1, sticky=(tk.N, tk.S))
		scrollV.config(command=self.yview)
		self.scrollbar = scrollV
		self.config(yscrollcommand=scrollV.set)

	def insertAtEnd(self, textStr) :
		self.insert('end', textStr)

	def clearAll(self) :
		self.delete('1.0', 'end')

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

	def __on_mouseWheel(self, event) :
		# print(event.delta)
		if self.focus :
			if event.delta > 0 :
				self.moveUpOneStep()
			else :
				self.moveDownOneStep()

def __main() :
	_tk = tk.Tk()
	_tk.columnconfigure(0, weight=1)
	_tk.rowconfigure(0, weight=1)
	tv = TextScrollView(_tk)
	tv.pack(expand=tk.YES, fill=tk.BOTH)
	tv.mainloop()

if __name__ == '__main__':
	__main()

