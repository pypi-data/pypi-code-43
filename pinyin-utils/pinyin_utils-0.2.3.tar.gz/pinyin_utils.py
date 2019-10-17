# pinyin_utils.py

import re, pytest, pprint

hConv = {}    # cached conversions

__version__ = "0.2.3"

# ---------------------------------------------------------------------------

def getVersion():

	return __version__

# ---------------------------------------------------------------------------

def convertPinyin(s, *, debug=False):

	assert type(s) == str
	retval = ''
	for match in re.finditer('([^a-z]*)([a-z]+)([0-5])?', s):
		new = None
		(other, base, tone) = match.groups()
		assert tone is None or type(tone) == str
		if (tone is None) or (tone == '') or (tone == '5') or (tone == '0'):
			# --- There is no 'v' in pinyin, so this is safe
			#     By convention, 'v' means 'ü'
			new = base.replace('v','ü')
			if debug:
				print(f"CONV '{base}' => '{new}' - neutral tone")
		else:
			index = int(tone) - 1
			if base in hConv:
				new = hConv[base][index]
				if debug:
					print(f"CONV '{base}' => '{new}' - found in hConv")
			else:
				# --- Set these:
				#        ch is the vowel we want to add accent to
				#        pos is the position in string 'base' where it's found
				(ch, pos) = (None, -1)   # set these

				# --- check for 2 common exceptions
				posIU = base.find('iu')
				posIO = base.find('io')
				if posIU != -1:
					(ch, pos) = ('u', posIU + 1)
					if debug:
						print("...IU exception")
				elif posIO != -1:
					(ch, pos) = ('o', posIO + 1)
					if debug:
						print("...IO exception")
				else:
					# --- Find lowest vowel and position
					for vowel in ('a','e','i','o','u','ü','v'):
						pos = base.find(vowel)
						if pos > -1:
							ch = base[pos]
							if debug:
								print(f"...found vowel '{vowel}' at pos {pos}")
							break     # from this "for vowel" loop

				if not ch or (pos == -1):
					raise Exception(f"No vowel found in string '{base}'")

				# --- fill in hConv so it's quicker to find next time
				new = strWithCharReplaced(base, pos, toned(ch, index))
				hConv[base] = _getPinyinList(base, ch, pos)
				if debug:
					print(f"CONV '{base}' => '{new}' - add to hConv")

		retval += other + new
	return retval

# ---------------------------------------------------------------------------

def toned(ch, index):

	assert (len(ch) == 1) and (ch in ('a','e','i','o','u','ü','v'))
	assert (index >= 0) and (index < 4)
	if ch == 'a':
		return ('ā', 'á', 'ǎ', 'à')[index]

	elif ch == 'e':
		return ('ē', 'é', 'ě', 'è')[index]

	elif ch == 'i':
		return ('ī', 'í', 'ǐ', 'ì')[index]

	elif ch == 'o':
		return ('ō', 'ó', 'ǒ', 'ò')[index]

	elif ch == 'u':
		return ('ū', 'ú', 'ǔ', 'ù')[index]

	else:
		return ('ǖ', 'ǘ', 'ǚ', 'ǜ')[index]

# ---------------------------------------------------------------------------

def strWithCharReplaced(s, pos, newch):

	assert type(s) == str
	assert pos >= 0
	assert pos < len(s)
	return s[:pos] + newch + s[pos+1:]

# ---------------------------------------------------------------------------

def _getPinyinList(untoned, ch, pos):

	lPinyin = []
	for i in (0,1,2,3):
		lPinyin.append(strWithCharReplaced(untoned, pos, toned(ch, i)))
	return lPinyin

# ---------------------------------------------------------------------------
#           Unit Tests
# ---------------------------------------------------------------------------

def test_1():
	assert strWithCharReplaced('abc', 0, 'X') == 'Xbc'
	assert strWithCharReplaced('abc', 1, 'X') == 'aXc'
	assert strWithCharReplaced('abc', 2, 'X') == 'abX'
	with pytest.raises(AssertionError):
		strWithCharReplaced(42, 1, 'X') == 'aXc'
	with pytest.raises(AssertionError):
		strWithCharReplaced('abc', 3, 'X') == 'aXc'
	with pytest.raises(AssertionError):
		strWithCharReplaced('abc', -1, 'X') == 'aXc'

def test_2():
	assert toned('a', 0) == 'ā'
	assert toned('o', 2) == 'ǒ'
	with pytest.raises(AssertionError):
		toned('x', 2)
	with pytest.raises(AssertionError):
		toned('a', 4)
	with pytest.raises(AssertionError):
		toned('a', -1)

def test_3():
	print()
	assert convertPinyin('liu3') == 'liǔ'
	assert convertPinyin('wo3')  == 'wǒ'
	assert convertPinyin('xiong2') == 'xióng'
	assert convertPinyin('san1ming2zhi4') == 'sānmíngzhì'

	# --- Do each one again - it should get them from cache
	assert convertPinyin('liu3') == 'liǔ'
	assert convertPinyin('wo3')  == 'wǒ'
	assert convertPinyin('xiong2') == 'xióng'
	assert convertPinyin('san1ming2zhi4') == 'sānmíngzhì'

def not_test_4():
	global hConv

	# --- This only works if your console support unicode
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(hConv)
