# translate.py

import os, sys, json, time, trio, asks, sqlite3, pprint
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from pinyin_utils import getVersion

db = None   # keep a cache of previous translations
APIKEY = os.environ['GOOGLE_APIKEY']

__VERSION__ = getVersion()

# ---------------------------------------------------------------------------

def setApiKey(apiKey):
	global APIKEY
	APIKEY = apiKey

# ---------------------------------------------------------------------------

async def translate(hWords, src='en', dest='zh', *, debug=False):
	# --- word can be an array of words,
	#     in which case, the return value will be an array
	global db

	if debug:
		print(f"CALL translate()")

	nWordsToTranslate = 0
	for word in hWords.keys():
		if not hWords[word]:
			nWordsToTranslate += 1

	if nWordsToTranslate == 0:
		if debug:
			print(f"translate(): No words to translate")
		return

	if not db:
		initDB()

	if debug:
		print(f"{nWordsToTranslate} words to translate")

	if dbTranslate(hWords, src, dest):
		# --- True return value means they were all found in the database
		if debug:
			print(f"...all translations found in DB")
	else:
		await webTranslate(hWords, src, dest, debug=debug)

	if debug:
		print(f"DEBUG: after webTranslate")
		pprint.PrettyPrinter(indent=3).pprint(hWords)

# ---------------------------------------------------------------------------

async def webTranslate(hWords, src='en', dest='zh', *, debug=False):
	global APIKEY

	if not APIKEY:
		raise Exception("Cannot translate without an API Key")
	ipname = 'translation.googleapis.com'
	url = mkurl(f"https://{ipname}", 'language', 'translate', 'v2',
	            key    = APIKEY,
	            source = src,
	            target = dest,
	            format = 'text',
	            )

	lWordsToTranslate = []
	lUrlParts = []
	for word in hWords.keys():
		if not hWords[word]:
			lWordsToTranslate.append(word)
			url += f"&q={word}"

	if len(lWordsToTranslate) == 0:
		raise Exception("webTranslate(): No words to translate!")

	resp = await asks.get(url)
	hJson = resp.json()
	lTranslations = hJson['data']['translations']

	pos = 0
	for word in lWordsToTranslate:
		chinese = lTranslations[pos]['translatedText']
		if chinese:
			if debug:
				print(f"...web translated: {word} => {chinese}")
			setTranslation(word, chinese, src, dest)
		else:
			if debug:
				print(f"...{word} not translated")
		hWords[word] = chinese
		pos += 1

# ---------------------------------------------------------------------------

def dbTranslate(hWords, src='en', dest='zh'):
	# --- returns True if all words were found in the database

	allInDB = True
	for word in hWords.keys():
		assert hWords[word] == None
		chinese = _dbTrans(word, src, dest)
		if chinese:
			hWords[word] = chinese
		else:
			allInDB = False
	return allInDB

# ---------------------------------------------------------------------------

def _dbTrans(word, src='en', dest='zh'):
	global db

	cursor = db.cursor()
	cursor.execute('''
			select translation
			from Translations
			where word = ?
			  and source = ?
			  and target = ?
			''', (word, src, dest))
	lData = cursor.fetchone()
	if lData:
		return lData[0]
	else:
		return None

# ---------------------------------------------------------------------------

def setTranslation(word, translation, src='en', dest='zh'):
	global db

	cursor = db.cursor()
	cursor.execute('''
			insert into Translations
			(word, translation, source, target)
			values(?,?,?,?)
			''',
			(word, translation, src, dest))
	db.commit()

# ---------------------------------------------------------------------------

def initDB(doClear=False, dbPath='./Translations.db'):
	global db

	cursor = None
	if not db:
		db = sqlite3.connect(dbPath)
		cursor = db.cursor()
		cursor.execute('''
			create table if not exists
			Translations (
				word text primary key,
				translation text,
				source text,
				target text
				)
			''')
	if doClear:
		if not cursor:
			cursor = db.cursor()
		cursor.execute('''
			delete from Translations
			''')
	db.commit()

# ---------------------------------------------------------------------------

def mkurl(base , *path, **params):

	if base[-1] == '/':
		url = base[:-1]
	else:
		url = base

	for item in path:
		url += f"/{item}"
	if params:
		qstr = urlencode(params)
		url += f"?{qstr}"
	return url
