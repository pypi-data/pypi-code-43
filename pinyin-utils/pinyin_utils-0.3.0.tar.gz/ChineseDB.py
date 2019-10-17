# ChineseDB.py

import sys, os, re, sqlite3
from collections import namedtuple
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from more_itertools import ilen

from pinyin_utils import getVersion, convertPinyin
from tabdb import tabdb
from englishWords import fixWord

reInt = re.compile(r'^\s*(\d+)')
__VERSION__ = getVersion()

# ===========================================================================

class ChineseDB:

	def __init__(self, filename='./Chinese.db'):

		db = self.db = sqlite3.connect(filename)
		self.createMissingTables()
		self.setChars = set(())

	# ------------------------------------------------------------------------

	def createMissingTables(self):

		# --- NOTE: sqlite adds a column named rowid to each table
		self.do('''
			create table if not exists
			chars (
				Char text primary key,
				CharOrder integer unique,
				FirstWordNum integer null,
				Pinyin text,
				Meaning text
				);
			create table if not exists
			words (
				Word text primary key,
				WordFreq integer,
				Pinyin text,
				PartOfSpeech char(1),
				Meaning text
				);
			create table if not exists
			english (
				Word text primary key,
				WordFreq integer,
				Chinese text,
				Pinyin text
				);
			create table if not exists
			abbrev (
				Word text primary key,
				WordFreq integer,
				Meaning text
				);
			''')

	# ------------------------------------------------------------------------

	def rebuildTables(self, *args):

		for table in args:
			if table in ['chars','words','english','abbrev']:
				self.do(f"drop table {table}")
			else:
				raise Exception(f"No such table: {table}")
		self.createMissingTables()

	# ------------------------------------------------------------------------
	# ------------------------------------------------------------------------

	def numChars(self):

		return self.fetch('select count(*) from chars')

	# ------------------------------------------------------------------------

	def chars(self, min=0, max=999999, *, debug=False):

		if debug:
			print(f"CALL chars({min}, {max})")
		assert type(min) == int
		assert type(max) == int
		sql = f'''
			select Char, CharOrder, Pinyin, Meaning
			from chars
			order by FirstWordNum, CharOrder
			limit {max-min} offset {min}
			'''
		if debug:
			print(f"SQL:\n{sql}")
		cursor = self.db.cursor()
		for row in cursor.execute(sql):
			yield {
				'Char':    row[0],
				'CharOrder':   row[1],
				'Pinyin':  row[2],
				'Meaning': row[3],
				}

	# ------------------------------------------------------------------------

	def setChar(self, h):

		(ch, n, pinyin, meaning) = (h[key] for key in
				('Char','CharOrder','Pinyin','Meaning')
				)
		assert len(ch) == 1
		self.do('''
			insert or replace into chars
			(Char, CharOrder, Pinyin, Meaning)
			values(?,?,?,?)
			''',
			(ch, n, pinyin, meaning)
			)
		self.setChars.add(ch)

	# ------------------------------------------------------------------------

	def setCharMeaning(self, ch, meaning):

		self.do('''
			update chars
			set Meaning = ?
			where Char = ?
			''',
			(meaning, ch)
		)

	# ------------------------------------------------------------------------

	def setFirstWordNum(self, ch, num):

		self.do('''
			update chars
			set FirstWordNum = ?
			where Char = ?
			  and FirstWordNum is null
			''',
			(num, ch)
		)

	# ------------------------------------------------------------------------

	def buildSetOfChars(self):

		nChars = 0
		for h in self.chars():
			nChars += 1
			self.setChars.add(h['Char'])
		print(f"buildSetOfChars(): {nChars} chars found")

	# ------------------------------------------------------------------------
	# ------------------------------------------------------------------------

	def setWord(self, h):
		# --- NOTE: We only want to add a word if all of its characters
		#           exist in the chars table
		(word, freq, pinyin, part, meaning) = (
				h[key] for key in (
						'Word','WordFreq','Pinyin','PartOfSpeech','Meaning')
				)
		assert type(word) == str

		for ch in word:
			if ch not in self.setChars:
				return False

		if (len(part) == 0):
			part = ' '
		else:
			part = part[0]

		if len(word) == 1:
			# --- Get pinyin and meaning from chars table
			(pinyin, meaning) = self.fetchrow('''
					select Pinyin, Meaning
					from chars
					where Char = ?
					''', (word))
		self.do('''
			insert or replace into words
			(Word, WordFreq, Pinyin, PartOfSpeech, Meaning)
			values(?,?,?,?,?)
			''',
			(word, freq, pinyin, part, meaning)
			)
		return True

	# ------------------------------------------------------------------------

	def numWords(self):

		return self.fetch('select count(*) from words')

	# ------------------------------------------------------------------------

	def words(self, min=0, max=999999, *, debug=False):

		if debug:
			print(f"CALL words({min}, {max})")
		assert type(min) == int
		assert type(max) == int
		sql = f'''
			select Word, WordFreq, Pinyin, PartOfSpeech, Meaning
			from words
			order by WordFreq desc
			limit {max-min} offset {min}
			'''
		if debug:
			print(f"SQL:\n{sql}")
		cursor = self.db.cursor()
		for row in cursor.execute(sql):
			yield {
				'Word':         row[0],
				'WordFreq':     row[1],
				'Pinyin':       row[2],
				'PartOfSpeech': row[3],
				'Meaning':      row[4],
				}

	# ------------------------------------------------------------------------
	# ------------------------------------------------------------------------

	def setEnglishWord(self, h):

		(word, freq, chinese, pinyin) = (
				h[key] for key in (
						'Word','WordFreq','Chinese','Pinyin')
				)

		assert word and type(word) == str
		assert not freq or type(freq) == int
		assert not chinese or type(chinese) == str
		assert not pinyin or type(pinyin) == str

		self.do('''
			insert or replace into english
			(Word, WordFreq, Chinese, Pinyin)
			values(?,?,?,?)
			''',
			(word, freq, chinese, pinyin)
			)

	# ------------------------------------------------------------------------

	def setAbbrev(self, h, expanded):

		word = h['Word']
		freq = h['WordFreq']

		assert word and type(word) == str
		assert not freq or type(freq) == int

		self.do('''
			insert or replace into abbrev
			(Word, WordFreq, Meaning)
			values(?,?,?)
			''',
			(word, freq, expanded)
			)
		return True

	# ------------------------------------------------------------------------

	def numEnglishWords(self):

		return self.fetch('select count(*) from english')

	# ------------------------------------------------------------------------

	def englishWords(self, min=0, max=999999, *, debug=False):

		if debug:
			print(f"CALL englishWords({min}, {max})")
		assert type(min) == int
		assert type(max) == int
		sql = f'''
			select Word, WordFreq, Chinese, Pinyin
			from english
			order by WordFreq desc
			limit {max-min} offset {min}
			'''
		if debug:
			print(f"SQL:\n{sql}")
		cursor = self.db.cursor()
		for row in cursor.execute(sql):
			yield {
				'Word':      row[0],
				'WordFreq':  row[1],
				'Chinese':   row[2],
				'Pinyin':    row[3],
				}

	# ------------------------------------------------------------------------
	# ------------------------------------------------------------------------

	def do(self, sql, lData=None):

		assert type(sql) == str
		sql = sql.strip()
		cursor = self.db.cursor()
		pos = sql.find(';')
		length = len(sql)
		if (pos > -1) and (pos != length-1):
			if lData:
				raise Exception("You cannot provide lData if SQL contains ';'")
			cursor.executescript(sql)
		else:
			try:
				if lData:
					cursor.execute(sql, lData)
				else:
					cursor.execute(sql)
			except Exception as ex:
				self.dumpSQL(sql)
				print(f"ERROR: {ex}")
				sys.exit(-1)
		self.db.commit()

	# ------------------------------------------------------------------------

	def dumpSQL(self, sql):

		print('-' * 65)
		print(sql.replace('\t','   '))
		print('-' * 65)

	# ------------------------------------------------------------------------

	def fetchrow(self, sql, lData=None):   # fetch a single row

		assert type(sql) == str
		cursor = self.db.cursor()
		if lData:
			cursor.execute(sql, lData)
		else:
			cursor.execute(sql)
		lRow = cursor.fetchone()
		if lRow:
			return lRow
		else:
			return None

	# ------------------------------------------------------------------------

	def fetch(self, sql, lData=None):   # fetch a single field

		assert type(sql) == str
		cursor = self.db.cursor()
		if lData:
			cursor.execute(sql, lData)
		else:
			cursor.execute(sql)
		lRow = cursor.fetchone()
		if lRow:
			return lRow[0]
		else:
			return None

# ===========================================================================

def getHanziURL(page):

	assert (page >= 0) and (page <= 99)
	baseURL = 'http://hanzidb.org/character-list/by-frequency?page='
	return baseURL + str(page+1)

# ---------------------------------------------------------------------------

def hanziChars(debug=True):

	h = {}     # always yield this dictionary
	for page in range(100):
		if debug:
			print(f"Fetching HanZI page {page}")
		url = getHanziURL(page)
		html = urlopen(url).read()
		bs = BeautifulSoup(html, 'lxml')

		lTables = bs.find_all('table')
		if len(lTables) != 1:
			raise Exception(f"There are {len(lTables)} tables on the page")
		table = lTables[0]

		# --- Cycle through all table rows
		nRows = 0
		for tr in table.find_all('tr'):
			if nRows == 0:
				# --- Skip the header row
				nRows = 1
				continue
			lCells = tr.find_all('td')
			yield {
				'Char':    lCells[0].get_text(),
				'CharOrder': int(lCells[7].get_text()),
				'Pinyin':  lCells[1].get_text(),
				'Meaning': lCells[2].get_text(),
				}

# ===========================================================================

def getEnglishURL(page):
	# OLD URL: http://www.naturalenglish.club/esl/{page * 1000}.php

	min = 1 + page * 1000
	max = min + 999
	return (
		f'https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists'
		f'/TV/2006/{min}-{max}')


# ---------------------------------------------------------------------------

def englishWords(debug=False):
	# --- Get English words from Wiktionary
	global reInt

	h = {}     # always yield this dictionary
	for page in range(10):
		if debug:
			print(f"Fetching Wiktionary page {page}")
		url = getEnglishURL(page)
		html = urlopen(url).read()
		bs = BeautifulSoup(html, 'lxml')

		lTables = bs.find_all('table')
		if len(lTables) != 1:
			raise Exception(f"There are {len(lTables)} tables on the page")
		table = lTables[0]

		# --- Cycle through all table rows
		nRows = 0
		for tr in table.find_all('tr'):
			if nRows == 0:
				# --- Skip the header row
				nRows = 1
				continue
			lCells = tr.find_all('td')
			freq = lCells[2].get_text()
			result = reInt.search(freq)
			if result:
				freq = result.group(1)
			else:
				raise  Exception(f"Invalid frequency: '{freq}'")
			word = lCells[1].get_text()
			word = fixWord(word)
			if word:
				yield {
					'Word':      word,
					'WordFreq':  int(freq),
					'Chinese':   None,
					'Pinyin':    None,
					}

# ===========================================================================

def chineseWords(filepath, debug=False):

	try:
		lReq = ('Word','Pinyin','WCount','Dominant.PoS','Eng.Tran.')
		for h in tabdb(filepath='./ChineseWords.txt', lRequire=lReq):
			pinyin = h['Pinyin']
			try:
				pinyin = convertPinyin(pinyin)
			except:
				pass  # happens if string contains no vowel
			yield {
				'Word':         h['Word'],
				'Pinyin':       pinyin,
				'WordFreq':     h['WCount'],
				'PartOfSpeech': h['Dominant.PoS'],
				'Meaning':      h['Eng.Tran.']
				}
	except Exception as ex:
		print(ex)
		sys.exit(-1)

