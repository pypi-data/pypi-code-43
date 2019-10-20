# -*- coding:utf-8 -*- 
# Date: 2018-03-07 10:40:20
# Author: dekiven

import os

from PIL import Image 
from PIL import ImageTk

from DKVTools.Funcs import *

if isPython3() :
	import tkinter as tk	
else:
	import Tkinter as tk

#import sys 
#reload(sys)
#sys.setdefaultencoding('utf-8')

__imgDict = {}

def __getMaxImgSize(imgSize, viewSize) :
	if viewSize is None :
		return imgSize
	ri = imgSize[0] / float(imgSize[1])
	rv = viewSize[0] / float(viewSize[1])
	maxSize = None
	if rv > ri :
		maxSize = (int(viewSize[1] * ri), viewSize[1])
	else :
		maxSize = (viewSize[0], int(viewSize[0] / ri))
	# print(imgSize, ri, viewSize, rv, maxSize)
	return maxSize


def GetImgTk(file, size=None, folder=None):
	'''获取图片，如果已经存在计数器+1,返回图片(ImageTk.PhotoImage).\n图片新增方法release(),调用ReleaseImgTk'''
	img = None
	if not os.path.isabs(file) :
		file = os.path.join(folder or os.getcwd(), file)
	if not os.path.isfile(file) :
		raise Exception('"%s" do not exists !'%(file))
	if os.path.isfile(file):
		key = '%s%s'%(file, str(size) if size is not None else '')
		img = __imgDict.get(key)
		if img is None :
			img = Image.open(file)
			maxSize = __getMaxImgSize(img.size, size)
			img = img.resize(maxSize, Image.ANTIALIAS)
			img = ImageTk.PhotoImage(img)

			img.params = (file, size, folder)
			def releaseFunc() :
				ReleaseImgTk(*img.params)
			img.release = releaseFunc

			__imgDict[key] = [img, 1]
		else :
			img = (img[0], img[1]+1)
			__imgDict[key] = img
			img = img[0]
	return img


def ReleaseImgTk(file, size=None, folder=None) :
	img = None
	if not os.path.isabs(file) :
		file = os.path.join(folder or os.getcwd(), file)
	if os.path.isfile(file):
		key = '%s%s'%(file, str(size) if size is not None else '')
		img = __imgDict.get(key)
		img[1] -= 1
		__imgDict[key] = img
		if img is not None and img[1] == 0 :
			# print('release %s'%(key))
			del __imgDict[key]

class ImgView(tk.Canvas):
	'''显示完整图片的widget，显示区域改变更新图片大小
	'''
	def __init__(self, *args, **dArgs):
		tk.Canvas.__init__(self, *args, **dArgs)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.size = (int(self.cget('width')), int(self.cget('height')))
		self.imgPath = ''
		self.hasImg = False
		self.bind('<Configure>', self.__onConfigureChanged)

	def grid(self, **dicArgs):
		'''不传sticky属性，默认强制缩放整个Img显示区域
		'''
		if dicArgs is None or len(dicArgs.keys()) == 0:
			dicArgs={'sticky':tk.N+tk.S+tk.W+tk.E}
		# else:
		# 	 dicArgs['sticky']=tk.N+tk.S+tk.W+tk.E
		# print(dicArgs)
		tk.Canvas.grid(self, **dicArgs)

	def setImgTkPhotoPath(self, filePath, size=None):
		self.clearImg()
		size = size and size or self.size
		img = GetImgTk(filePath, size)
		self.size = size
		self.setImgTkPhoto(img)
		self.imgPath = filePath

	def setImgTkPhoto(self, img):
		self.create_image(self.size[0]/2, self.size[1]/2, image=img)
		self.hasImg = True

	def clearImg(self):
		if self.hasImg :
			self.delete('all')
			ReleaseImgTk(self.imgPath, size=self.size)
			self.hasImg = False
			self.imgPath = ''

	def __onConfigureChanged(self, event):
		# print(event.width, event.height)
		size = (event.width, event.height)
		if self.hasImg :
			self.setImgTkPhotoPath(self.imgPath, size)
		self.size = size
		# self.configure(bg='red')


def __main():
	# help(ImgView)
	view = ImgView()
	master = view.master
	master.columnconfigure(0, weight=1)
	master.rowconfigure(0, weight=1)
	view.grid()
	view.setImgTkPhotoPath('res/d_checked.png')

	def exitApp(event) :
		view.quit()
	master.bind('<Escape>', exitApp)
	view.mainloop()

	

if __name__ == '__main__':
	__main()

