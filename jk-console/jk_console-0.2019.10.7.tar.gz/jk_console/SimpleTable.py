


from .Console import Console




class SimpleTableConstants(object):

	HALIGN_LEFT = 0
	HALIGN_CENTER = 1
	HALIGN_RIGHT = 2

	CASE_NORMAL = 0
	CASE_LOWER = 1
	CASE_UPPER = 2

#



class SimpleTableCell(SimpleTableConstants):

	def __init__(self, table):
		self.__table = table
		self.halign = None
		self.value = None
		self.color = None
		self.textTransform = None
	#

	def __str__(self):
		if self.value is None:
			return ""
		else:
			return str(self.value)
	#

	def __len__(self):
		s = self.__str__()
		return len(s)
	#

#



class SimpleTableColumn(SimpleTableConstants):

	def __init__(self, table, columnIndex:int, rows:list):
		self.columnIndex = columnIndex
		self.__table = table
		#self.__columnData = columnData
		self.halign = None
		self.textTransform = None
		self.__rows = rows
		self.color = None
		self.vlineAfterColumn = False
		self.marginLeft = 1
		self.marginRight = 1
	#

	def getMaxWidth(self):
		return max([ (len(row) if row else 0) for row in self.__rows ])
	#

	"""
	@property
	def halign(self) -> int:
		return self.__columnData.get("halign", SimpleTableConstants.HALIGN_DEFAULT)
	#

	@halign.setter
	def halign(self, v:int):
		self.__columnData["halign"] = v
	#
	"""

	def __getitem__(self, index:int):
		assert isinstance(index, int)
		if index >= len(self.__rows):
			return None
		return self.__rows[index]
	#

	def __setitem__(self, index:int, v):
		raise NotImplementedError()
	#

	def __len__(self):
		return len(self.__rows)
	#

	def __enter__(self):
		return self
	#

	def __exit__(self, type, value, traceback):
		pass
	#

#



class SimpleTableRow(SimpleTableConstants):

	def __init__(self, table):
		self.__table = table
		self.__cells = []
		table._getColumnsList(0).append(self)
		self.halign = None
		self.color = None
		self.textTransform = None
		self.hlineAfterRow = False
	#

	def addCell(self) -> SimpleTableCell:
		c = SimpleTableCell(self.__table)
		self.__table._getColumnsList(len(self.__cells)).remove(self)
		self.__cells.append(c)
		self.__table._getColumnsList(len(self.__cells)).append(self)
		return c
	#

	def addCells(self, *args):
		self.__table._getColumnsList(len(self.__cells)).remove(self)
		for a in args:
			c = SimpleTableCell(self.__table)
			self.__cells.append(c)
			c.value = a
		self.__table._getColumnsList(len(self.__cells)).append(self)
	#

	def __getitem__(self, index:int):
		assert isinstance(index, int)
		if index >= len(self.__cells):
			return None
		return self.__cells[index]
	#

	def __setitem__(self, index:int, v):
		raise NotImplementedError()
	#

	def __len__(self):
		return len(self.__cells)
	#

	def __enter__(self):
		return self
	#

	def __exit__(self, type, value, traceback):
		pass
	#

#



class SimpleTable(SimpleTableConstants):

	def __init__(self):
		self.__rows = []
		self.__columns = {}
		self.__nColumns = {
			0: []
		}
	#

	def _getColumnsList(self, n:int):
		cols = self.__nColumns.get(n)
		if cols is None:
			cols = []
			self.__nColumns[n] = cols
		return cols
	#

	def addRow(self, *args) -> SimpleTableRow:
		r = SimpleTableRow(self)
		self.__rows.append(r)
		if args:
			r.addCells(*args)
		return r
	#

	@property
	def numberOfColumns(self) -> int:
		return max(self.__nColumns.keys())
	#

	@property
	def numberOfRows(self) -> int:
		return len(self.__rows)
	#

	def __len__(self):
		return len(self.__rows)
	#

	def __getColumnWidth(self, nColumn:int) -> int:
		cells = self.__getColumnCells(nColumn)
		if cells:
			return max([ (len(c) if c else 0) for c in cells ])
		else:
			return 0
	#

	def __getColumnWidths(self) -> list:
		return [ self.__getColumnWidth(n) for n in range(0, self.numberOfColumns) ]
	#

	def column(self, nColumn:int):
		d = self.__columns.get(nColumn)
		if d is None:
			d = SimpleTableColumn(self, nColumn, self.__rows)
			self.__columns[nColumn] = d
		return d
	#

	def row(self, nRow:int):
		if (nRow >= len(self.__rows)) or (nRow < 0):
			return None
		return self.__rows[nRow]
	#

	def __getColumnCells(self, nColumn:int):
		columnCells = []
		for row in self.__rows:
			columnCells.append(row[nColumn])
		return columnCells
	#

	#
	# Print the table.
	#
	def print(self, prefix:str = "", gapChar = " ", vLineChar = "|", hLineChar = "-", crossChar = "|", printFunction = None, useColors:bool = True):
		if printFunction is None:
			printFunction = print

		outBuffer = []
		self.__printToBuffer(outBuffer, prefix, gapChar, vLineChar, hLineChar, crossChar, useColors)

		for line in outBuffer:
			printFunction(line)
	#

	#
	# Print the table.
	#
	def printToLines(self, prefix:str = "", gapChar = " ", vLineChar = "|", hLineChar = "-", crossChar = "|", useColors:bool = True):
		outBuffer = []
		self.__printToBuffer(outBuffer, prefix, gapChar, vLineChar, hLineChar, crossChar, useColors)
		return outBuffer
	#

	def __printToBuffer(self, outBuffer:list, prefix:str = "", gapChar = " ", vLineChar = "|", hLineChar = "-", crossChar = "|", useColors:bool = True):
		columnWidths = self.__getColumnWidths()

		for row in self.__rows:
			rowCells = [ prefix ]
			data = []
			for nColumn in range(0, len(columnWidths)):
				column = self.column(nColumn)
				halign, color, textTransform, text = self.__getCellData(row, column, row[nColumn])
				if not useColors:
					color = None
				if color:
					rowCells.append(color)
				text = self.__hformatCellText(text, halign, textTransform, columnWidths[nColumn], column.marginLeft, column.marginRight)
				rowCells.append(text)
				if color:
					rowCells.append(Console.RESET)

				if column.vlineAfterColumn:
					rowCells.append(vLineChar)
				else:
					rowCells.append(gapChar)

				data.append((nColumn, column, text))

			outBuffer.append("".join(rowCells))

			if row.hlineAfterRow:
				rowCells.clear()
				rowCells.append(prefix)
				rowGapHLine = hLineChar * len(gapChar)
				for nColumn, column, text in data:
					hline = hLineChar * len(text)
					rowCells.append(hline)

					if column.vlineAfterColumn:
						rowCells.append(crossChar)
					else:
						rowCells.append(rowGapHLine)

				outBuffer.append("".join(rowCells))
	#

	def raw(self):
		ret = []

		for row in self.__rows:
			rowCells = []
			for nColumn in range(0, self.numberOfColumns):
				column = self.column(nColumn)
				halign, color, textTransform, text = self.__getCellData(row, column, row[nColumn])
				rowCells.append(self.__hformatCellText(text, None, textTransform, 0, 0, 0))
			ret.append(rowCells)

		return ret
	#

	def __getCellData(self, row:SimpleTableRow, column:SimpleTableColumn, cell:SimpleTableCell):
		# collect data: cell vs. row vs. column

		if cell:
			s = str(cell)
			halign = cell.halign
			color = cell.color
			textTransform = cell.textTransform
		else:
			s = ""
			halign = None
			color = None
			textTransform = None

		if halign is None:
			halign = row.halign
		if halign is None:
			halign = column.halign

		if color is None:
			color = row.color
		if color is None:
			color = column.color

		if textTransform is None:
			textTransform = row.textTransform
		if textTransform is None:
			textTransform = column.textTransform

		return halign, color, textTransform, s
	#

	def __hformatCellText(self, s:str, halign:int, textTransform:int, width:int, marginLeft:int, marginRight:int):
		if textTransform == SimpleTableConstants.CASE_LOWER:
			s = s.lower()
		elif textTransform == SimpleTableConstants.CASE_UPPER:
			s = s.upper()

		if halign in [ None, SimpleTableConstants.HALIGN_LEFT ]:
			s = s + " " * (width - len(s))
		elif halign == SimpleTableConstants.HALIGN_CENTER:
			spc = " " * ((width - len(s)) // 2 + 1)
			s = spc + s + spc
			s = s[:width]
		elif halign == SimpleTableConstants.HALIGN_RIGHT:
			s = " " * (width - len(s)) + s
		else:
			raise Exception()

		if marginLeft:
			s = " " * marginLeft + s
		if marginRight:
			s += " " * marginRight

		return s
	#

	def addEmptyRow(self):
		if len(self.__rows):
			if (self.__rows[-1]):
				self.addRow()
	#

#




