


from .Rectangle import Rectangle
from ..Console import Console
from .ViewPortCell import ViewPortCell
from .ViewPortRenderer import ViewPortRenderer
from .ViewPortRGB import ViewPortRGB
from .ViewPortBuffer2 import ViewPortBuffer2









class ConsoleCell(object):

	def __init__(self, viewPortCells:list):
		# contains instances of ViewPortCell
		self.cells = viewPortCells
		# contains the current console string to display
		self.s = None
		# contains the last console string displayed
		self.oldS = None
	#

	def buildConsoleStr(self):
		c = None
		colFG = None
		colFGBrightness = None
		colBG = None
		colBGBrightness = None

		#print(len(self.cells), end="", flush=True)
		for cell in reversed(self.cells):
			if cell.c is not None:
				c = cell.c
				colFG = cell.colFG
				colFGBrightness = cell._brightness
				break

		for cell in reversed(self.cells):
			if cell.colBG is not None:
				colBG = cell.colBG
				colBGBrightness = cell._brightness
				break

		if c is None:
			c = " "
		if colBG is None:
			colBG = 0
			colBGBrightness = 0
		if colFG is None:
			colFG = 0
			colFGBrightness = 0

		self.s = ViewPortRenderer.bgTables[colBGBrightness][colBG] + ViewPortRenderer.fgTables[colFGBrightness][colFG] + c
	#

#




class ViewPort(object):

	__EMPTY_CELL = ViewPortCell()

	def __init__(self):
		ViewPort.__EMPTY_CELL.c = " "
		ViewPort.__EMPTY_CELL.colBG = int(ViewPortRGB.rgb256(0, 0, 0))
		ViewPort.__EMPTY_CELL.colFG = int(ViewPortRGB.rgb256(0, 0, 0))
		ViewPort.__EMPTY_CELL._brightness = ViewPortRenderer.MAX_BRIGHTNESS

		self.__width, self.__height = Console.getSize()
		#self.__height -= 1
		self.__screenMatrix = None
		self.__buffers = []
	#

	def createBuffer(self, *args, bErrorIfOutOfBounds:bool = False):
		if len(args) == 1:
			assert isinstance(args[0], Rectangle)
			ofsX = args[0].x
			ofsY = args[0].y
			width = args[0].width
			height = args[0].height
		elif len(args) == 4:
			assert isinstance(args[0], int)
			assert isinstance(args[1], int)
			assert isinstance(args[2], int)
			assert isinstance(args[3], int)
			ofsX = args[0]
			ofsY = args[1]
			width = args[2]
			height = args[3]
		else:
			raise Exception("args ???")

		assert ofsX >= 0
		assert ofsY >= 0
		assert width >= 0
		assert height >= 0

		buffer = ViewPortBuffer2(self, ofsX, ofsY, width, height)
		buffer.bErrorIfOutOfBounds = bErrorIfOutOfBounds
		self.__buffers.append(buffer)
		self.__screenMatrix = self.__buildScreenMatrix()
		self.__screenStrings = [ None ] * len(self.__screenMatrix)
		self.__oldScreenStrings = [ None ] * len(self.__screenMatrix)
		return buffer
	#

	def __buildScreenMatrix(self):
		rows = []
		for y in range(0, self.__height):
			row = []
			rows.append(row)
			for x in range(0, self.__width):
				row.append(ConsoleCell([ self.__EMPTY_CELL ]))

		for buffer in self.__buffers:
			for y in range(0, buffer.height):
				row = rows[buffer.ofsY + y]
				for x in range(0, buffer.width):
					row[buffer.ofsX + x].cells.append(buffer.rows[y][x])

		return rows
	#

	def render(self, bRenderAll:bool = False):
		bHasData = False
		y = None
		x = None
		output = []

		n = 0
		for nRow, row in enumerate(self.__screenMatrix):
			for nCol, cell in enumerate(row):
				cell.buildConsoleStr()
				if bRenderAll or (cell.s != cell.oldS):
					if not bHasData:
						bHasData = True
						x = nCol
						y = nRow
					output.append(cell.s)
					cell.oldS = cell.s
					n += 1
				else:
					if bHasData:
						Console.printAt(x, y, "".join(output), False)
						bHasData = False
						output.clear()

		if bHasData:
			Console.printAt(x, y, "".join(output), False)
			bHasData = False
		Console.moveCursorTo(0, 0, True)
		#Console.flush()

		return n
	#

#








