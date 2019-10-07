
#
# This example uses a console buffer implementation to perform fast rendering of text.
# Performance measurements are displayed.
# Performance might vary greatly from system to system.
#



import sys
import time
import datetime

from jk_console import *





class Effect1(object):

	def __init__(self, width:int = None, height:int = None):
		self.chars = ".,;/;,. "
		self.colors = [ Console.ForeGround.STD_LIGHTGRAY, Console.ForeGround.STD_BLUE, Console.ForeGround.STD_LIGHTBLUE, Console.ForeGround.STD_LIGHTCYAN,
			Console.ForeGround.STD_LIGHTBLUE, Console.ForeGround.STD_BLUE, Console.ForeGround.STD_LIGHTGRAY, Console.RESET ]
		self.mods = [ 0, -1, -1, -2, -2, -1, -1, 0 ]

		self.expectedWidth = width
		self.expectedHeight = height
		self.w = None
		self.h = None
		self.cb = None
		self.i = None
		self.lastConsoleWidth = -1
		self.lastConsoleHeight = -1

		self.init()
	#

	def init(self):
		self.lastConsoleWidth, self.lastConsoleHeight = Console.getSize()

		self.w = Console.width() - 1 if self.expectedWidth is None else min(self.expectedWidth, Console.width() - 1)
		self.h = Console.height() - 1 if self.expectedHeight is None else min(self.expectedHeight, Console.height() - 1)
		self.cb = ConsoleBuffer(self.w, self.h)

		rect = Rect(0, 0, self.w, self.h)
		rect = rect.shrink(right = 1, bottom = 1)
		self.cb.drawFrame(rect = rect)

		self.i = 1
	#

	def drawPattern(self, ofs:int):
		for iy in range(1, self.h - 2):
			for ix in range(2, self.w - 2):
				j = (iy + ofs) % 8
				i = (ix + iy + ofs + self.mods[j]) % 8
				self.cb.set(ix, iy, self.colors[i], self.chars[i])
	#

	def runOneLoop(self):
		t0 = datetime.datetime.now()
		self.drawPattern(self.i)
		t1 = datetime.datetime.now()
		self.cb.bufferToConsole(bForceFullRepaint=True)
		t2 = datetime.datetime.now()

		#time.sleep(0.001)

		td1 = t1 - t0
		td2 = t2 - t1
		tdS = t2 - t0
		pdata = [
			"~~ screen-size: ", str(self.w), "x", str(self.h), " pixels"
			" ~~ rendering: %d.%03ds" % (td1.seconds, (td1.microseconds + 499) // 1000),
			" ~~ buffer-to-screen: %d.%03ds" % (td2.seconds, (td2.microseconds + 499) // 1000),
			" ~~ total: %d.%03ds (fps %d)" % (tdS.seconds, (tdS.microseconds + 499) // 1000, int(1.0 / (t2 - t0).total_seconds())),
		]
		pdata.append(" ~~")
		self.cb.printText(2, self.h - 2, Console.ForeGround.STD_WHITE, "".join(pdata))
		self.i += 1

		ww, hh = Console.getSize()
		if (ww != self.lastConsoleWidth) or (hh != self.lastConsoleHeight):
			self.init()
	#

	def runForever(self):
		while True:
			self.runOneLoop()
	#

#


