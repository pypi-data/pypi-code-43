# tabdb.py

import os, sys, io, pytest

from pinyin_utils import getVersion

__VERSION__ = getVersion()

class tabdb:

	def __init__(self, *, fh=None,
	                      filepath=None,
	                      lineNumKey='LineNumber',
	                      lRequire=None):
		# --- One of fh and filepath must be defined
		#     fh can be a file handle or a string
		#     filepath must be a string

		if fh:
			if filepath:
				raise Exception("Can't define both fh and filepath")

			# --- Allow passing in a string
			if isinstance(fh, str):
				self.fh = io.StringIO(fh)
			else:
				self.fh = fh
		elif filepath:
			if fh:
				raise Exception("Can't define both fh and filepath")
			assert type(filepath) == str
			self.fh = open(filepath, 'r', encoding='utf8')
		else:
			raise Exception("You must define either fh or filepath")
		self.lineNumKey = lineNumKey
		self.lRequire = lRequire

	# ------------------------------------------------------------------------

	def __iter__(self):

		fh = self.fh
		lnKey = self.lineNumKey
		lineNum = 1
		lKeys = None
		h = {}     # this is yielded
		for line in fh.readlines():
			if lineNum == 1:
				# --- strip utf-8 "byte order mark" if present
				if line.startswith(u'\ufeff'):
					line = line[1:]
				lKeys = line.strip().split('\t')
				if self.lRequire:
					for key in self.lRequire:
						if key not in lKeys:
							raise Exception(f"Missing key '{key}'")
				lineNum = 2
				continue
			assert lKeys
			fieldNum = 0
			for value in line.rstrip().split('\t'):
				if fieldNum < len(lKeys):
					h[lKeys[fieldNum]] = value
				fieldNum += 1
			while (fieldNum < len(lKeys)):
				h[lKeys[fieldNum]] = ''
				fieldNum += 1
			if lnKey:
				h[lnKey] = lineNum
			yield h
			lineNum += 1

# ---------------------------------------------------------------------------
#                  UNIT TESTS
# ---------------------------------------------------------------------------

if sys.argv[0].find('pytest') > -1:

	TAB = '\t'
	NL = '\n'
	dbstring = (
		  TAB.join(('first',  'middle', 'last'))    + NL
		+ TAB.join(('John',   '',       'Deighan')) + NL
		+ TAB.join(('Lewis',  'James',  'Foster'))  + NL
		+ TAB.join(('Arathi', 'Gowda',  'Prasad'))  + NL
		)

	def test_1():
		with pytest.raises(Exception):
			for h in tabdb():
				pass

	def test_2():

		first0 = None
		last0 = None
		nRecords = 0
		for h in tabdb(fh=dbstring):
			first, last = (h.get(s) for s in ('first','last'))
			if nRecords == 0:
				first0, last0 = first, last
			nRecords += 1
		assert nRecords == 3
		assert first0 == 'John'
		assert last0 == 'Deighan'

	def test_3():
		with pytest.raises(Exception):
			for h in tabdb(fh=dbstring, lRequire=('first','last','suffix')):
				pass
