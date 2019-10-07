



#
# http://tldp.org/HOWTO/Bash-Prompt-HOWTO/x329.html
#



import os
import sys
import signal

from .readchar import readchar as _readchar




def __buildTree(items):
	ret = {}
	for item in items:
		if len(item) > 1:
			____addToTree(ret, item, 0)
	return ret
#

def ____addToTree(tree, item, n):
	if n == len(item) - 1:
		c = item[n]
		if c not in tree:
			tree[c] = item
		else:
			raise Exception("Duplicate: " + item)
	else:
		c = item[n]
		if c not in tree:
			tree[c] = {}
		____addToTree(tree[c], item, n + 1)
#





class Console(object):

	class ForeGround:
		BLACK = None
		DARK_GREY = None
		GREY = None
		LIGHT_GREY = None
		WHITE = None

		RED = None
		ORANGE = None
		YELLOW = None
		YELLOWGREEN = None
		GREEN = None
		GREENCYAN = None
		CYAN = None
		CYANBLUE = None
		BLUE = None
		BLUEVIOLET = None
		VIOLET = None
		VIOLETRED = None

		DARK_RED = None
		DARK_ORANGE = None
		DARK_YELLOW = None
		DARK_YELLOWGREEN = None
		DARK_GREEN = None
		DARK_GREENCYAN = None
		DARK_CYAN = None
		DARK_CYANBLUE = None
		DARK_BLUE = None
		DARK_BLUEVIOLET = None
		DARK_VIOLET = None
		DARK_VIOLETRED = None

		LIGHT_RED = None
		LIGHT_ORANGE = None
		LIGHT_YELLOW = None
		LIGHT_YELLOWGREEN = None
		LIGHT_GREEN = None
		LIGHT_GREENCYAN = None
		LIGHT_CYAN = None
		LIGHT_CYANBLUE = None
		LIGHT_BLUE = None
		LIGHT_BLUEVIOLET = None
		LIGHT_VIOLET = None
		LIGHT_VIOLETRED = None

		"""
		BLACK = '\033[30m'
		DARK_RED = '\033[31m'
		DARK_GREEN = '\033[32m'
		DARK_YELLOW = '\033[33m'
		DARK_BLUE = '\033[34m'
		DARK_PURPLE = '\033[35m'
		DARK_CYAN = '\033[36m'
		#WHITE = '\033[37m'
		WHITE = "\033[38;2;255;255;255m"
		DARK_GREY = '\033[90m'
		RED = '\033[91m'
		GREEN = '\033[92m'
		YELLOW = '\033[93m'
		BLUE = '\033[94m'
		PURPLE = '\033[95m'
		CYAN = '\033[96m'
		LIGHT_GREY = '\033[97m'
		#BLACK = '\033[98m'
		"""

		STD_BLACK = '\033[0;30m'
		STD_BLUE = '\033[0;34m'
		STD_GREEN = '\033[0;32m'
		STD_CYAN = '\033[0;36m'
		STD_RED = '\033[0;31m'
		STD_PURPLE = '\033[0;35m'
		STD_DARKYELLOW = '\033[0;33m'
		STD_LIGHTGRAY = '\033[0;37m'
		STD_DARKGRAY = '\033[1;30m'
		STD_LIGHTBLUE = '\033[1;34m'
		STD_LIGHTGREEN = '\033[1;32m'
		STD_LIGHTCYAN = '\033[1;36m'
		STD_LIGHTRED = '\033[1;31m'
		STD_LIGHTPURPLE = '\033[1;35m'
		STD_YELLOW = '\033[1;33m'
		STD_WHITE = '\033[1;37m'

		ALL_STD_COLORS = (
			(STD_BLACK, "STD_BLACK"),
			(STD_BLUE, "STD_BLUE"),
			(STD_GREEN, "STD_GREEN"),
			(STD_CYAN, "STD_CYAN"),
			(STD_RED, "STD_RED"),
			(STD_PURPLE, "STD_PURPLE"),
			(STD_DARKYELLOW, "STD_DARKYELLOW"),
			(STD_LIGHTGRAY, "STD_LIGHTGRAY"),
			(STD_DARKGRAY, "STD_DARKGRAY"),
			(STD_LIGHTBLUE, "STD_LIGHTBLUE"),
			(STD_LIGHTGREEN, "STD_LIGHTGREEN"),
			(STD_LIGHTCYAN, "STD_LIGHTCYAN"),
			(STD_LIGHTRED, "STD_LIGHTRED"),
			(STD_LIGHTPURPLE, "STD_LIGHTPURPLE"),
			(STD_YELLOW, "STD_YELLOW"),
			(STD_WHITE, "STD_WHITE"),
		)

		@staticmethod
		def getByName(name:str):
			for col, colID in Console.ForeGround.ALL_STD_COLORS:
				if colID == name:
					return col
			return None
		#

		@staticmethod
		def rgb256(r:int, g:int, b:int):
			if (r < 0) or (r > 255):
				raise Exception("Red value must be a valid integer value! (Value specified: " + str(r) + ")")
			if not isinstance(g, int) or (g < 0) or (g > 255):
				raise Exception("Green value must be a valid integer value! (Value specified: " + str(g) + ")")
			if not isinstance(b, int) or (b < 0) or (b > 255):
				raise Exception("Blue value must be a valid integer value! (Value specified: " + str(b) + ")")
			return "\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"
		#

		@staticmethod
		def rgb1(r:float, g:float, b:float):
			if not isinstance(g, (int, float)) or (r < 0) or (r > 1):
				raise Exception("Red value must be a valid float value in the range [0..1]! (Value specified: " + str(r) + ")")
			if not isinstance(g, (int, float)) or (g < 0) or (g > 1):
				raise Exception("Red value must be a valid float value in the range [0..1]! (Value specified: " + str(g) + ")")
			if not isinstance(b, (int, float)) or (b < 0) or (b > 1):
				raise Exception("Red value must be a valid float value in the range [0..1]! (Value specified: " + str(b) + ")")
			return "\033[38;2;" + str(int(r * 255)) + ";" + str(int(g * 255)) + ";" + str(int(b * 255)) + "m"
		#

		@staticmethod
		def hsl1(h:float, s:float, l:float):
			if (h < 0) or (h > 1):
				raise Exception("Hue value must be a valid float value in the range [0..1]!")
			if (s < 0) or (s > 1):
				raise Exception("Saturation value must be a valid float value in the range [0..1]!")
			if (l < 0) or (l > 1):
				raise Exception("Luminance value must be a valid float value in the range [0..1]!")
			if s == 0:
				s = 0.0001
			q = l * (1 + s) if l < 0.5 else l + s - l * s
			p = 2 * l - q
			r = Console._hue2rgb(p, q, h + 1/3)
			g = Console._hue2rgb(p, q, h)
			b = Console._hue2rgb(p, q, h - 1/3)
			return "\033[38;2;" + str(int(r * 255)) + ";" + str(int(g * 255)) + ";" + str(int(b * 255)) + "m"
		#

	#

	class BackGround:
		BLACK = None
		DARK_GREY = None
		GREY = None
		LIGHT_GREY = None
		WHITE = None

		RED = None
		ORANGE = None
		YELLOW = None
		YELLOWGREEN = None
		GREEN = None
		GREENCYAN = None
		CYAN = None
		CYANBLUE = None
		BLUE = None
		BLUEVIOLET = None
		VIOLET = None
		VIOLETRED = None

		DARK_RED = None
		DARK_ORANGE = None
		DARK_YELLOW = None
		DARK_YELLOWGREEN = None
		DARK_GREEN = None
		DARK_GREENCYAN = None
		DARK_CYAN = None
		DARK_CYANBLUE = None
		DARK_BLUE = None
		DARK_BLUEVIOLET = None
		DARK_VIOLET = None
		DARK_VIOLETRED = None

		LIGHT_RED = None
		LIGHT_ORANGE = None
		LIGHT_YELLOW = None
		LIGHT_YELLOWGREEN = None
		LIGHT_GREEN = None
		LIGHT_GREENCYAN = None
		LIGHT_CYAN = None
		LIGHT_CYANBLUE = None
		LIGHT_BLUE = None
		LIGHT_BLUEVIOLET = None
		LIGHT_VIOLET = None
		LIGHT_VIOLETRED = None

		STD_BLACK = '\033[40m'
		STD_BLUE = '\033[44m'
		STD_GREEN = '\033[42m'
		STD_CYAN = '\033[46m'
		STD_RED = '\033[41m'
		STD_PURPLE = '\033[45m'
		STD_DARKYELLOW = '\033[43m'
		STD_LIGHTGRAY = '\033[47m'

		ALL_STD_COLORS = (
			(STD_BLACK, "STD_BLACK"),
			(STD_BLUE, "STD_BLUE"),
			(STD_GREEN, "STD_GREEN"),
			(STD_CYAN, "STD_CYAN"),
			(STD_RED, "STD_RED"),
			(STD_PURPLE, "STD_PURPLE"),
			(STD_DARKYELLOW, "STD_DARKYELLOW"),
			(STD_LIGHTGRAY, "STD_LIGHTGRAY"),
		)

		@staticmethod
		def getByName(name:str):
			for col, colID in Console.BackGround.ALL_STD_COLORS:
				if colID == name:
					return col
			return None
		#

		"""
		BLACK = '\033[40m'
		DARK_RED = '\033[41m'
		DARK_GREEN = '\033[42m'
		DARK_YELLOW = '\033[43m'
		DARK_BLUE = '\033[44m'
		DARK_PURPLE = '\033[45m'
		DARK_CYAN = '\033[46m'
		WHITE = '\033[47m'
		DARK_GREY = '\033[100m'
		RED = '\033[101m'
		GREEN = '\033[102m'
		YELLOW = '\033[103m'
		BLUE = '\033[104m'
		PURPLE = '\033[105m'
		CYAN = '\033[106m'
		LIGHT_GREY = '\033[107m'
		"""

		@staticmethod
		def rgb256(r:int, g:int, b:int):
			if (r < 0) or (r > 255):
				raise Exception("Red value must be a valid integer value! (Value specified: " + str(r) + ")")
			if (g < 0) or (g > 255):
				raise Exception("Red value must be a valid integer value! (Value specified: " + str(g) + ")")
			if (b < 0) or (b > 255):
				raise Exception("Red value must be a valid integer value! (Value specified: " + str(b) + ")")
			return "\033[48;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"
		#

		@staticmethod
		def rgb1(r:float, g:float, b:float):
			if not isinstance(g, (int, float)) or (r < 0) or (r > 1):
				raise Exception("Red value must be a valid float value in the range [0..1]! (Value specified: " + str(r) + ")")
			if not isinstance(g, (int, float)) or (g < 0) or (g > 1):
				raise Exception("Green value must be a valid float value in the range [0..1]! (Value specified: " + str(g) + ")")
			if not isinstance(g, (int, float)) or (b < 0) or (b > 1):
				raise Exception("Blue value must be a valid float value in the range [0..1]! (Value specified: " + str(b) + ")")
			return "\033[48;2;" + str(int(r * 255)) + ";" + str(int(g * 255)) + ";" + str(int(b * 255)) + "m"
		#

		@staticmethod
		def hsl1(h:float, s:float, l:float):
			if (h < 0) or (h > 1):
				raise Exception("Hue value must be a valid float value in the range [0..1]! (h is " + str(h) + ")")
			if (s < 0) or (s > 1):
				raise Exception("Saturation value must be a valid float value in the range [0..1]! (s is " + str(s) + ")")
			if (l < 0) or (l > 1):
				raise Exception("Luminance value must be a valid float value in the range [0..1]! (l is " + str(l) + ")")
			if s == 0:
				s = 0.0001
			q = l * (1 + s) if l < 0.5 else l + s - l * s
			p = 2 * l - q
			r = Console._hue2rgb(p, q, h + 1/3)
			g = Console._hue2rgb(p, q, h)
			b = Console._hue2rgb(p, q, h - 1/3)
			return "\033[48;2;" + str(int(r * 255)) + ";" + str(int(g * 255)) + ";" + str(int(b * 255)) + "m"
		#

	#

	"""
	@staticmethod
	def parseColor(sCol:str):
		for s in sCol.split(sep=[" ", "\t", ]):
			
	#
	"""

	MOUSE_ENABLE = "\033[?1000;1006;1015h"
	MOUSE_DISABLE = "\033[?1000;1006;1015l"

	RESET = "\033[0m"
	RESET_TOPLEFT = "\033[0m\033[1;1H"

	BOLD = "\033[01m"
	UNDERLINE = "\033[04m"
	STRIKETHROUGH = "\033[09m"

	class Input:
		KEY_CTRL_Y				= "\x19"
		KEY_CTRL_X				= "\x18"
		KEY_CTRL_C				= "\x03"
		KEY_CTRL_V				= "\x16"
		KEY_CTRL_B				= "\x02"
		KEY_CTRL_N				= "\x0e"
		KEY_CTRL_A				= "\x01"
		KEY_CTRL_S				= "\x13"
		KEY_CTRL_D				= "\x04"
		KEY_CTRL_F				= "\x06"
		KEY_CTRL_G				= "\x07"
		KEY_CTRL_H				= "\x08"
		KEY_CTRL_K				= "\x0b"
		KEY_CTRL_L				= "\x0c"
		KEY_CTRL_Q				= "\x11"
		KEY_CTRL_W				= "\x17"
		KEY_CTRL_E				= "\x05"
		KEY_CTRL_R				= "\x12"
		KEY_CTRL_T				= "\x14"
		KEY_CTRL_Z				= "\x1a"
		KEY_CTRL_U				= "\x15"
		KEY_CTRL_O				= "\x0f"
		KEY_CTRL_P				= "\x10"
		KEY_CTRL_J				= "\n"
		KEY_CTRL_I				= "\t"		# same as KEY_TAB
		KEY_CTRL_M				= "\r"		# same as KEY_ENTER
		KEY_SHIFT_TAB			= "\x1b\x5b\x5A"
		KEY_TAB					= "\x09"
		KEY_BACKSPACE			= "\x7f"
		KEY_ENTER				= "\x0d"
		KEY_CTRL_BREAK			= "\x03"		# same as KEY_CTRL_C
		KEY_ESCAPE_ESCAPE		= "\x1b\x1b"
		KEY_CURSOR_LEFT			= "\x1b\x5b\x44"
		KEY_CURSOR_RIGHT		= "\x1b\x5b\x43"
		KEY_CURSOR_UP			= "\x1b\x5b\x41"
		KEY_CURSOR_DOWN			= "\x1b\x5b\x42"
		KEY_PAGE_UP				= "\x1b\x5b\x35\x7e"
		KEY_PAGE_DOWN			= "\x1b\x5b\x36\x7e"
		KEY_HOME				= "\x1b\x4f\x48"
		KEY_END					= "\x1b\x4f\x46"
		KEY_HOME_NUMPAD			= "\x1b\x5b\x31\x7e"		#(numpad)
		KEY_END_NUMPAD			= "\x1b\x5b\x34\x7e"		#(numpad)
		#KEY_SHIFT_CURSOR_LEFT	= "\x1b\x5b\x44\x32\x44"
		#KEY_SHIFT_CURSOR_RIGHT	= "\x1b\x5b\x43\x32\x43"
		#KEY_SHIFT_CURSOR_UP	= "\x1b\x5b\x41\x32\x41"
		#KEY_SHIFT_CURSOR_DOWN	= "\x1b\x5b\x42\x32\x42"
		KEY_CTRL_PAGE_DOWN		= "\x1b\x5b\x35\x3B\x35\x7e"
		KEY_CTRL_PAGE_UP		= "\x1b\x5b\x36\x3B\x35\x7e"
		KEY_CTRL_CURSOR_LEFT	= "\x1b\x5b\x31\x3B\x35\x44"
		KEY_CTRL_CURSOR_RIGHT	= "\x1b\x5b\x31\x3B\x35\x43"
		KEY_CTRL_CURSOR_UP		= "\x1b\x5b\x31\x3B\x35\x41"
		KEY_CTRL_CURSOR_DOWN	= "\x1b\x5b\x31\x3B\x35\x42"
		KEY_ALT_CURSOR_PAGE_DOWN	= "\x1b\x5b\x36\x3b\x33\x7e"
		KEY_ALT_CURSOR_PAGE_UP		= "\x1b\x5b\x35\x3b\x33\x7e"
		KEY_ALT_CURSOR_LEFT		= "\x1b\x5b\x31\x3b\x33\x44"
		KEY_ALT_CURSOR_RIGHT	= "\x1b\x5b\x31\x3b\x33\x43"
		KEY_ALT_CURSOR_UP		= "\x1b\x5b\x31\x3b\x33\x41"
		KEY_ALT_CURSOR_DOWN		= "\x1b\x5b\x31\x3b\x33\x42"
		KEY_ALT_HOME			= "\x1b\x5b\x31\x3b\x33\x48"
		KEY_ALT_END				= "\x1b\x5b\x31\x3b\x33\x46"
		KEY_CTRL_ALT_HOME		= "\x1b\x5b\x31\x3b\x37\x48"
		KEY_CTRL_ALT_END		= "\x1b\x5b\x31\x3b\x37\x46"
		KEY_CTRL_ALT_LEFT		= "\x1b\x5b\x31\x3b\x37\x44"
		KEY_CTRL_ALT_RIGHT		= "\x1b\x5b\x31\x3b\x37\x43"
		KEY_CTRL_ALT_UP			= "\x1b\x5b\x31\x3b\x37\x41"
		KEY_CTRL_ALT_DOWN		= "\x1b\x5b\x31\x3b\x37\x42"
		KEY_HOME				= "\x1b\x5b\x48"
		KEY_END					= "\x1b\x5b\x46"
		KEY_CTRL_HOME			= "\x1b\x5b\x31\x3b\x35\x48"
		KEY_CTRL_END			= "\x1b\x5b\x31\x3b\x35\x46"
		KEY_DELETE				= "\x1b\x5b\x33\x7e"
		KEY_INSERT				= "\x1b\x5b\x32\x7e"
		KEY_F2					= "\x1b\x4f\x51"
		KEY_F3					= "\x1b\x4f\x52"
		KEY_F4					= "\x1b\x4f\x53"
		KEY_F5					= "\x1b\x5b\x31\x35\x7e"
		KEY_F6					= "\x1b\x5b\x31\x37\x7e"
		KEY_F7					= "\x1b\x5b\x31\x38\x7e"
		KEY_F8					= "\x1b\x5b\x31\x39\x7e"
		KEY_F9					= "\x1b\x5b\x32\x30\x7e"
		KEY_F12					= "\x1b\x5b\x32\x34\x7e"
		KEY_CTRL_F1				= "\x1b\x5b\x31\x3b\x35\x50"
		KEY_CTRL_F2				= "\x1b\x5b\x31\x3b\x35\x51"
		KEY_CTRL_F3				= "\x1b\x5b\x31\x3b\x35\x52"
		KEY_CTRL_F4				= "\x1b\x5b\x31\x3b\x35\x53"
		KEY_CTRL_F5				= "\x1b\x5b\x31\x35\x3b\x35\x7e"
		KEY_CTRL_F6				= "\x1b\x5b\x31\x37\x3b\x35\x7e"
		KEY_CTRL_F7				= "\x1b\x5b\x31\x38\x3b\x35\x7e"
		KEY_CTRL_F8				= "\x1b\x5b\x31\x39\x3b\x35\x7e"
		KEY_CTRL_F9				= "\x1b\x5b\x32\x30\x3b\x35\x7e"
		KEY_CTRL_F10			= "\x1b\x5b\x32\x31\x3b\x35\x7e"
		KEY_CTRL_F11			= "\x1b\x5b\x32\x33\x3b\x35\x7e"
		KEY_CTRL_F12			= "\x1b\x5b\x32\x34\x3b\x35\x7e"
		KEY_SHIFT_F1			= "\x1b\x5b\x31\x3b\x32\x50"
		KEY_SHIFT_F2			= "\x1b\x5b\x31\x3b\x32\x51"
		KEY_SHIFT_F3			= "\x1b\x5b\x31\x3b\x32\x52"
		KEY_SHIFT_F4			= "\x1b\x5b\x31\x3b\x32\x53"
		KEY_SHIFT_F5			= "\x1b\x5b\x31\x35\x3b\x32\x7e"
		KEY_SHIFT_F6			= "\x1b\x5b\x31\x37\x3b\x32\x7e"
		KEY_SHIFT_F7			= "\x1b\x5b\x31\x38\x3b\x32\x7e"
		KEY_SHIFT_F8			= "\x1b\x5b\x31\x39\x3b\x32\x7e"
		KEY_SHIFT_F9			= "\x1b\x5b\x32\x30\x3b\x32\x7e"
		KEY_SHIFT_F11			= "\x1b\x5b\x32\x33\x3b\x32\x7e"
		KEY_SHIFT_F12			= "\x1b\x5b\x32\x34\x3b\x32\x7e"
		MOUSE_EVENT				= "\x1b\x5b\x3c"
		MOUSE_EVENT_2			= "\x1b\x5b\x5b\x3c"

		ALL_KEYS_TO_KEY_NAME = {
			KEY_SHIFT_F1: "Shift+F1",
			KEY_SHIFT_F2: "Shift+F2",
			KEY_SHIFT_F3: "Shift+F3",
			KEY_SHIFT_F4: "Shift+F4",
			KEY_SHIFT_F5: "Shift+F5",
			KEY_SHIFT_F6: "Shift+F6",
			KEY_SHIFT_F7: "Shift+F7",
			KEY_SHIFT_F8: "Shift+F8",
			KEY_SHIFT_F9: "Shift+F9",
			KEY_SHIFT_F11: "Shift+F11",
			KEY_SHIFT_F12: "Shift+F12",
			KEY_CTRL_F1: "Ctrl+F1",
			KEY_CTRL_F2: "Ctrl+F2",
			KEY_CTRL_F3: "Ctrl+F3",
			KEY_CTRL_F4: "Ctrl+F4",
			KEY_CTRL_F5: "Ctrl+F5",
			KEY_CTRL_F6: "Ctrl+F6",
			KEY_CTRL_F7: "Ctrl+F7",
			KEY_CTRL_F8: "Ctrl+F8",
			KEY_CTRL_F9: "Ctrl+F9",
			KEY_CTRL_F10: "Ctrl+F10",
			KEY_CTRL_F11: "Ctrl+F11",
			KEY_CTRL_F12: "Ctrl+F12",
			KEY_CTRL_Y: "Ctrl+Y",
			KEY_CTRL_X: "Ctrl+X",
			KEY_CTRL_C: "Ctrl+C",
			KEY_CTRL_V: "Ctrl+V",
			KEY_CTRL_B: "Ctrl+B",
			KEY_CTRL_N: "Ctrl+N",
			KEY_CTRL_A: "Ctrl+A",
			KEY_CTRL_S: "Ctrl+S",
			KEY_CTRL_D: "Ctrl+D",
			KEY_CTRL_F: "Ctrl+F",
			KEY_CTRL_G: "Ctrl+G",
			KEY_CTRL_H: "Ctrl+H",
			KEY_CTRL_K: "Ctrl+K",
			KEY_CTRL_L: "Ctrl+L",
			KEY_CTRL_Q: "Ctrl+Q",
			KEY_CTRL_W: "Ctrl+W",
			KEY_CTRL_E: "Ctrl+E",
			KEY_CTRL_R: "Ctrl+R",
			KEY_CTRL_T: "Ctrl+T",
			KEY_CTRL_Z: "Ctrl+Z",
			KEY_CTRL_U: "Ctrl+U",
			KEY_CTRL_O: "Ctrl+O",
			KEY_CTRL_P: "Ctrl+P",
			KEY_CTRL_J: "Ctrl+J",
			KEY_SHIFT_TAB: "Shift+Tab",
			KEY_TAB: "Tab",
			KEY_BACKSPACE: "Backspace",
			KEY_ENTER: "Enter",
			KEY_ESCAPE_ESCAPE: "ESC,ESC",
			KEY_CURSOR_LEFT: "CursorLeft",
			KEY_CURSOR_RIGHT: "CursorRight",
			KEY_CURSOR_UP: "CursorUp",
			KEY_CURSOR_DOWN: "CursorDown",
			KEY_PAGE_UP: "PageUp",
			KEY_PAGE_DOWN: "PageDown",
			KEY_HOME: "Home",
			KEY_END: "End",
			KEY_HOME_NUMPAD: "Home(Numpad)",
			KEY_END_NUMPAD: "End(Numpad)",
			KEY_CTRL_PAGE_UP: "Ctrl+PageUp",
			KEY_CTRL_PAGE_DOWN: "Ctrl+PageDown",
			KEY_CTRL_CURSOR_LEFT: "Ctrl+CursorLeft",
			KEY_CTRL_CURSOR_RIGHT: "Ctrl+CursorRight",
			KEY_CTRL_CURSOR_UP: "Ctrl+CursorUp",
			KEY_CTRL_CURSOR_DOWN: "Ctrl+CursorDown",
			KEY_ALT_CURSOR_LEFT: "Alt+CursorLeft",
			KEY_ALT_CURSOR_RIGHT: "Alt+CursorRight",
			KEY_ALT_CURSOR_UP: "Alt+CursorUp",
			KEY_ALT_CURSOR_DOWN: "Alt+CursorDown",
			KEY_ALT_CURSOR_PAGE_UP: "Alt+PageUp",
			KEY_ALT_CURSOR_PAGE_DOWN: "Alt-PageDown",
			KEY_ALT_HOME: "Alt+Home",
			KEY_ALT_END: "Alt+End",
			KEY_CTRL_HOME: "Ctrl+Home",
			KEY_CTRL_END: "Ctrl+End",
			KEY_HOME: "Home",
			KEY_END: "End",
			KEY_DELETE: "Delete",
			KEY_INSERT: "Insert",
			KEY_F2: "F2",
			KEY_F3: "F3",
			KEY_F4: "F4",
			KEY_F5: "F5",
			KEY_F6: "F6",
			KEY_F7: "F7",
			KEY_F8: "F8",
			KEY_F9: "F9",
			KEY_F12: "F12",
			KEY_CTRL_ALT_HOME: "Ctrl+Alt+Home",
			KEY_CTRL_ALT_END: "Ctrl+Alt+End",
			KEY_CTRL_ALT_LEFT: "Ctrl+Alt+Left",
			KEY_CTRL_ALT_RIGHT: "Ctrl+Alt+Right",
			KEY_CTRL_ALT_UP: "Ctrl+Alt+Up",
			KEY_CTRL_ALT_DOWN: "Ctrl+Alt+Down",
			MOUSE_EVENT: "MOUSE_EVENT",
		}

		ALL_KEY_NAMES_TO_KEY = {}

		ALL_SPECIAL_KEYS = set([
			KEY_CTRL_Y, KEY_CTRL_X, KEY_CTRL_C, KEY_CTRL_V, KEY_CTRL_B, KEY_CTRL_A, KEY_CTRL_S, KEY_CTRL_D, KEY_CTRL_F, KEY_CTRL_G,
			KEY_CTRL_H, KEY_CTRL_K, KEY_CTRL_L, KEY_CTRL_Q, KEY_CTRL_W, KEY_CTRL_E, KEY_CTRL_R, KEY_CTRL_T, KEY_CTRL_Z, KEY_CTRL_U,
			KEY_CTRL_O, KEY_CTRL_P, KEY_CTRL_J,
			KEY_SHIFT_TAB, KEY_TAB, KEY_BACKSPACE, KEY_ENTER, KEY_ESCAPE_ESCAPE,
			KEY_CURSOR_LEFT, KEY_CURSOR_RIGHT, KEY_CURSOR_UP, KEY_CURSOR_DOWN, KEY_PAGE_DOWN, KEY_PAGE_UP,
			KEY_HOME, KEY_END, KEY_HOME_NUMPAD, KEY_END_NUMPAD, KEY_CTRL_PAGE_DOWN, KEY_CTRL_PAGE_UP,
			KEY_CTRL_CURSOR_DOWN, KEY_CTRL_CURSOR_LEFT, KEY_CTRL_CURSOR_RIGHT, KEY_CTRL_CURSOR_UP,
			KEY_DELETE, KEY_INSERT, KEY_F2, KEY_F3, KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8, KEY_F9, KEY_F12,
			KEY_CTRL_F1, KEY_CTRL_F2, KEY_CTRL_F3, KEY_CTRL_F4, KEY_CTRL_F5, KEY_CTRL_F6,
			KEY_CTRL_F7, KEY_CTRL_F8, KEY_CTRL_F9, KEY_CTRL_F10, KEY_CTRL_F11, KEY_CTRL_F12,
			KEY_SHIFT_F1, KEY_SHIFT_F2, KEY_SHIFT_F3, KEY_SHIFT_F4, KEY_SHIFT_F5, KEY_SHIFT_F6,
			KEY_SHIFT_F7, KEY_SHIFT_F8, KEY_SHIFT_F9, KEY_SHIFT_F11, KEY_SHIFT_F12,
			KEY_ALT_CURSOR_DOWN, KEY_ALT_CURSOR_LEFT, KEY_ALT_CURSOR_RIGHT, KEY_ALT_CURSOR_UP,
			KEY_ALT_CURSOR_PAGE_UP, KEY_ALT_CURSOR_PAGE_DOWN, KEY_ALT_HOME, KEY_ALT_END,
			KEY_CTRL_HOME, KEY_CTRL_END, KEY_HOME, KEY_END,
			KEY_CTRL_ALT_HOME, KEY_CTRL_ALT_END, KEY_CTRL_ALT_LEFT, KEY_CTRL_ALT_RIGHT, KEY_CTRL_ALT_UP, KEY_CTRL_ALT_DOWN,
			MOUSE_EVENT, MOUSE_EVENT_2,
		])

		@staticmethod
		def isSpecialKey(key:str):
			return key in Console.Input.ALL_SPECIAL_KEYS
		#

		#
		# Read a single character from STDIN. (This keyboard character can be expressed by multiple characters.)
		#
		# @return	str		Returns a string. If the string contains a single character this will be an ordinary character. Otherwise
		#					the key pressed was a special character. Use the constants defined in this class for checking what key has
		#					been pressed.
		#
		@staticmethod
		def readKey():
			tree = Console.Input._TREE

			dataRead = ""
			while True:
				c = _readchar()
				dataRead += c
				if c in tree:
					x = tree[c]
					if isinstance(x, str):
						if x == Console.Input.MOUSE_EVENT_2:
							x = Console.Input.MOUSE_EVENT
						if x == Console.Input.MOUSE_EVENT:
							s = []
							while True:
								c = _readchar()
								s.append(c)
								if (c == "M") or (c == 'm'):
									break
							x += "".join(s)
						return x
					else:
						tree = x
				else:
					return dataRead
		#

		@staticmethod
		def readKeyWithTimeout(timeoutSeconds:int = 1):
			signal.signal(signal.SIGALRM, Console.Input.__interrupt)
			signal.alarm(timeoutSeconds) # sets timeout
			try:
				key = Console.Input.readKey()
				signal.alarm(0)
				timeout = False
			except KeyboardInterrupt:
				#print("Keyboard interrupt")
				timeout = True # Do this so you don't mistakenly get input when there is none
				key = None
			except Exception as e:
				#print(e)
				timeout = True
				#print("Timeout")
				signal.alarm(0)
				key = None
			return key

		@staticmethod
		def __interrupt(signum, frame):
			raise Exception("")

	#

	@staticmethod
	def _hue2rgb(p, q, t):
		if t < 0:
			t += 1
		if t > 1:
			t -= 1
		if t < 1/6:
			return p + (q - p) * 6 * t
		if t < 1/2:
			return q
		if t < 2/3:
			return p + (q - p) * (2/3 - t) * 6
		return p
	#

	@staticmethod
	def getSize():
		return os.get_terminal_size()
	#

	@staticmethod
	def width():
		return os.get_terminal_size()[0]
	#

	@staticmethod
	def height():
		return os.get_terminal_size()[1]
	#

	#
	# Returns the current cursor position.
	#
	# @return	int x		The column position (starting at zero).
	# @return	int y		The row position (starting at zero).
	#
	@staticmethod
	def getCursorPosition():
		print("\u001B[6n", end="", flush=True)
		buf = ""
		c = None
		while c != "R":
			c = Console.Input.readKey()
			buf += c
		sYX = buf[2:-1].split(";")
		y = int(sYX[0]) - 1
		x = int(sYX[1]) - 1
		return (x, y)
	#

	#
	# Print a string at the specified position. The cursor is moved during printing and will be positioned after the last character after printing is completed.
	#
	@staticmethod
	def printAt(x:int, y:int, text:str, bFlush:bool=True):
		assert isinstance(x, int)
		assert isinstance(y, int)

		print("\033[" + str(y + 1) + ";" + str(x + 1) + "H" + text, end='', flush=bFlush)
	#

	#
	# Measure the text length. Escape codes are identified and not included into the length.
	#
	@staticmethod
	def getTextWidth(text:str):
		n = 0
		i = 0
		while i < len(text):
			if text[i:].startswith('\033['):
				# escape code found
				i += 3
				while text[i] != 'm':
					i += 1
			else:
				# regular character found
				n += 1
			i += 1
		return n
	#

	#
	# Remove any formatting and color codes.
	#
	@staticmethod
	def stripESCSequences(text:str):
		ret = ""
		i = 0
		while i < len(text):
			if text[i:].startswith('\033['):
				# escape code found
				i += 3
				while text[i] != 'm':
					i += 1
			else:
				# regular character found
				ret += text[i]
			i += 1
		return ret
	#

	#
	# Move the cursor to the specified position.
	#
	@staticmethod
	def moveCursorTo(x:int, y:int, bFlush:bool=True):
		assert isinstance(x, int)
		assert isinstance(y, int)

		print("\033[" + str(y + 1) + ";" + str(x + 1) + "H", end='', flush=bFlush)
	#

	#
	# Clear the screen.
	#
	@staticmethod
	def clear():
		#os.system('cls' if os.name == 'nt' else 'clear')
		print("\u001Bc")
	#

	@staticmethod
	def flush():
		sys.stdout.flush()
	#

#



Console.Input._TREE = __buildTree(Console.Input.ALL_SPECIAL_KEYS)

for key, value in Console.Input.ALL_KEYS_TO_KEY_NAME.items():
	Console.Input.ALL_KEY_NAMES_TO_KEY[value] = key


# https://www.rapidtables.com/web/color/RGB_Color.html


Console.ForeGround.BLACK = Console.ForeGround.rgb256(0, 0, 0)
Console.ForeGround.DARK_GREY = Console.ForeGround.rgb256(96, 96, 96)
Console.ForeGround.GREY = Console.ForeGround.rgb256(128, 128, 128)
Console.ForeGround.LIGHT_GREY = Console.ForeGround.rgb256(192, 192, 192)
Console.ForeGround.WHITE = Console.ForeGround.rgb256(255, 255, 255)

Console.ForeGround.RED = Console.ForeGround.rgb256(255, 0, 0)
Console.ForeGround.ORANGE = Console.ForeGround.rgb256(255, 128, 0)
Console.ForeGround.YELLOW = Console.ForeGround.rgb256(255, 255, 0)
Console.ForeGround.YELLOWGREEN = Console.ForeGround.rgb256(128, 255, 0)
Console.ForeGround.GREEN = Console.ForeGround.rgb256(0, 255, 0)
Console.ForeGround.GREENCYAN = Console.ForeGround.rgb256(0, 255, 128)
Console.ForeGround.CYAN = Console.ForeGround.rgb256(0, 255, 255)
Console.ForeGround.CYANBLUE = Console.ForeGround.rgb256(0, 128, 255)
Console.ForeGround.BLUE = Console.ForeGround.rgb256(0, 0, 255)
Console.ForeGround.BLUEVIOLET = Console.ForeGround.rgb256(128, 0, 255)
Console.ForeGround.VIOLET = Console.ForeGround.rgb256(255, 0, 255)
Console.ForeGround.VIOLETRED = Console.ForeGround.rgb256(255, 0, 128)

Console.ForeGround.DARK_RED = Console.ForeGround.rgb256(204, 0, 0)
Console.ForeGround.DARK_ORANGE = Console.ForeGround.rgb256(204, 102, 0)
Console.ForeGround.DARK_YELLOW = Console.ForeGround.rgb256(204, 204, 0)
Console.ForeGround.DARK_YELLOWGREEN = Console.ForeGround.rgb256(102, 204, 0)
Console.ForeGround.DARK_GREEN = Console.ForeGround.rgb256(0, 204, 0)
Console.ForeGround.DARK_GREENCYAN = Console.ForeGround.rgb256(0, 204, 102)
Console.ForeGround.DARK_CYAN = Console.ForeGround.rgb256(0, 204, 204)
Console.ForeGround.DARK_CYANBLUE = Console.ForeGround.rgb256(0, 102, 204)
Console.ForeGround.DARK_BLUE = Console.ForeGround.rgb256(0, 0, 204)
Console.ForeGround.DARK_BLUEVIOLET = Console.ForeGround.rgb256(102, 0, 204)
Console.ForeGround.DARK_VIOLET = Console.ForeGround.rgb256(204, 0, 204)
Console.ForeGround.DARK_VIOLETRED = Console.ForeGround.rgb256(204, 0, 102)

Console.ForeGround.LIGHT_RED = Console.ForeGround.rgb256(255, 102, 102)
Console.ForeGround.LIGHT_ORANGE = Console.ForeGround.rgb256(255, 178, 102)
Console.ForeGround.LIGHT_YELLOW = Console.ForeGround.rgb256(255, 255, 102)
Console.ForeGround.LIGHT_YELLOWGREEN = Console.ForeGround.rgb256(178, 255, 102)
Console.ForeGround.LIGHT_GREEN = Console.ForeGround.rgb256(102, 255, 102)
Console.ForeGround.LIGHT_GREENCYAN = Console.ForeGround.rgb256(102, 255, 178)
Console.ForeGround.LIGHT_CYAN = Console.ForeGround.rgb256(102, 255, 255)
Console.ForeGround.LIGHT_CYANBLUE = Console.ForeGround.rgb256(102, 178, 255)
Console.ForeGround.LIGHT_BLUE = Console.ForeGround.rgb256(102, 102, 255)
Console.ForeGround.LIGHT_BLUEVIOLET = Console.ForeGround.rgb256(178, 102, 255)
Console.ForeGround.LIGHT_VIOLET = Console.ForeGround.rgb256(255, 102, 255)
Console.ForeGround.LIGHT_VIOLETRED = Console.ForeGround.rgb256(255, 102, 178)


Console.BackGround.BLACK = Console.BackGround.rgb256(0, 0, 0)
Console.BackGround.DARK_GREY = Console.BackGround.rgb256(96, 96, 96)
Console.BackGround.GREY = Console.BackGround.rgb256(128, 128, 128)
Console.BackGround.LIGHT_GREY = Console.BackGround.rgb256(192, 192, 192)
Console.BackGround.WHITE = Console.BackGround.rgb256(255, 255, 255)

Console.BackGround.RED = Console.BackGround.rgb256(255, 0, 0)
Console.BackGround.ORANGE = Console.BackGround.rgb256(255, 128, 0)
Console.BackGround.YELLOW = Console.BackGround.rgb256(255, 255, 0)
Console.BackGround.YELLOWGREEN = Console.BackGround.rgb256(128, 255, 0)
Console.BackGround.GREEN = Console.BackGround.rgb256(0, 255, 0)
Console.BackGround.GREENCYAN = Console.BackGround.rgb256(0, 255, 128)
Console.BackGround.CYAN = Console.BackGround.rgb256(0, 255, 255)
Console.BackGround.CYANBLUE = Console.BackGround.rgb256(0, 128, 255)
Console.BackGround.BLUE = Console.BackGround.rgb256(0, 0, 255)
Console.BackGround.BLUEVIOLET = Console.BackGround.rgb256(128, 0, 255)
Console.BackGround.VIOLET = Console.BackGround.rgb256(255, 0, 255)
Console.BackGround.VIOLETRED = Console.BackGround.rgb256(255, 0, 128)

Console.BackGround.DARK_RED = Console.BackGround.rgb256(204, 0, 0)
Console.BackGround.DARK_ORANGE = Console.BackGround.rgb256(204, 102, 0)
Console.BackGround.DARK_YELLOW = Console.BackGround.rgb256(204, 204, 0)
Console.BackGround.DARK_YELLOWGREEN = Console.BackGround.rgb256(102, 204, 0)
Console.BackGround.DARK_GREEN = Console.BackGround.rgb256(0, 204, 0)
Console.BackGround.DARK_GREENCYAN = Console.BackGround.rgb256(0, 204, 102)
Console.BackGround.DARK_CYAN = Console.BackGround.rgb256(0, 204, 204)
Console.BackGround.DARK_CYANBLUE = Console.BackGround.rgb256(0, 102, 204)
Console.BackGround.DARK_BLUE = Console.BackGround.rgb256(0, 0, 204)
Console.BackGround.DARK_BLUEVIOLET = Console.BackGround.rgb256(102, 0, 204)
Console.BackGround.DARK_VIOLET = Console.BackGround.rgb256(204, 0, 204)
Console.BackGround.DARK_VIOLETRED = Console.BackGround.rgb256(204, 0, 102)

Console.BackGround.LIGHT_RED = Console.BackGround.rgb256(255, 102, 102)
Console.BackGround.LIGHT_ORANGE = Console.BackGround.rgb256(255, 178, 102)
Console.BackGround.LIGHT_YELLOW = Console.BackGround.rgb256(255, 255, 102)
Console.BackGround.LIGHT_YELLOWGREEN = Console.BackGround.rgb256(178, 255, 102)
Console.BackGround.LIGHT_GREEN = Console.BackGround.rgb256(102, 255, 102)
Console.BackGround.LIGHT_GREENCYAN = Console.BackGround.rgb256(102, 255, 178)
Console.BackGround.LIGHT_CYAN = Console.BackGround.rgb256(102, 255, 255)
Console.BackGround.LIGHT_CYANBLUE = Console.BackGround.rgb256(102, 178, 255)
Console.BackGround.LIGHT_BLUE = Console.BackGround.rgb256(102, 102, 255)
Console.BackGround.LIGHT_BLUEVIOLET = Console.BackGround.rgb256(178, 102, 255)
Console.BackGround.LIGHT_VIOLET = Console.BackGround.rgb256(255, 102, 255)
Console.BackGround.LIGHT_VIOLETRED = Console.BackGround.rgb256(255, 102, 178)















