



from .Console import Console



class ConsoleGraphics(object):

	@staticmethod
	def hline(x1:int, y:int, x2:int, c:str):
		s = ""
		for i in range(0, x2 - x1 + 1):
			s += c
		Console.printAt(x1, y, s, bFlush=False)
	#

	@staticmethod
	def vline(x:int, y1:int, y2:int, c:str):
		for y in range(y1, y2 + 1):
			Console.printAt(x, y, c, bFlush=False)
	#

	@staticmethod
	def box(centerX:int, centerY:int, text:str, frameChar:str):
		w = len(text)
		x1 = centerX - int(w/2) - 2
		x2 = x1 + 4 + w
		y1 = centerY - 2
		y2 = centerY + 2

		ConsoleGraphics.hline(x1, y1, x2, frameChar)
		ConsoleGraphics.hline(x1, y2, x2, frameChar)
		ConsoleGraphics.vline(x1, y1, y2, frameChar)
		ConsoleGraphics.vline(x2, y1, y2, frameChar)
		Console.printAt(x1 + 2, y1 + 2, text, bFlush=False)
	#

#









