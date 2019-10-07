


import sys
import threading

from .Console import Console





#bPynputLoaded = False
#try:
#	import pynput
#	from pynput.mouse import Listener as MouseListener
#	bPynputLoaded = True
#except:
#	pass





#
# This class implements an active component that actively retrieves keyboard or mouse events. Whenever an event is fired an event handler
# method will be invoked (if such a method was specified).
#
class EventCollector(object):

	def __getCallable(self, attrName:str, obj, function):
		if obj:
			try:
				f = getattr(obj, attrName)
			except:
				f = None
			if f:
				assert callable(f)
		else:
			if function:
				assert callable(function)
			f = function
		return f
	#

	#def __xx_on_mouse_move(self, x, y):
	#	self.__on_mouse_move(self, x, y)
	##

	def __init__(self, listener = None, on_key_pressed = None, on_ctrl_c = None, on_screen_resized = None,
		on_mouse_move = None, on_mouse_wheel = None, on_mouse_button = None, on_mouse_drag = None):

		self.__on_screen_resized = self.__getCallable("on_screen_resized", listener, on_screen_resized)
		self.__on_key_pressed = self.__getCallable("on_key_pressed", listener, on_key_pressed)
		self.__on_ctrl_c = self.__getCallable("on_ctrl_c", listener, on_ctrl_c)
		self.__on_mouse_move = self.__getCallable("on_mouse_move", listener, on_mouse_move)
		self.__on_mouse_wheel = self.__getCallable("on_mouse_wheel", listener, on_mouse_wheel)
		self.__on_mouse_button = self.__getCallable("on_mouse_button", listener, on_mouse_button)
		self.__on_mouse_drag = self.__getCallable("on_mouse_drag", listener, on_mouse_drag)

		#if bPynputLoaded:
		#	self.__mouseListener = MouseListener(
		#		on_move = self.__xx_on_mouse_move if self.__on_mouse_move else None,
		#		)
		#	self.__mouseListener.start()
		#else:
		#	self.__mouseListener = None

		self.__bRun = True
	#

	def terminate(self):
		self.__bRun = False
		#if self.__mouseListener:
		#	self.__mouseListener.stop()
	#

	def run(self):
		print(Console.MOUSE_ENABLE)
		mouseButtonStates = [ False ] * 3
		try:

			lastSize = Console.getSize()
			while self.__bRun:
				key = Console.Input.readKeyWithTimeout(1)

				currentSize = Console.getSize()
				if lastSize != currentSize:
					if self.__on_screen_resized:
						self.__on_screen_resized(self, lastSize[0], lastSize[1], currentSize[0], currentSize[1])
					lastSize = currentSize

				if key is None:
					pass
				elif key.startswith(Console.Input.MOUSE_EVENT):
					bMouseDown = key[-1] == "M"
					nMouseButton, mouseX, mouseY = [ int(x) for x in key[3:-1].split(";") ]
					if nMouseButton == 64:
						if self.__on_mouse_wheel:
							self.__on_mouse_wheel(self, False)
					elif nMouseButton == 65:
						if self.__on_mouse_wheel:
							self.__on_mouse_wheel(self, True)
					else:
						if 0 <= nMouseButton <= 2:
							bDragging = bMouseDown and (mouseButtonStates[nMouseButton] == bMouseDown)
							mouseButtonStates[nMouseButton] = bMouseDown
							if bDragging:
								if self.__on_mouse_drag:
									self.__on_mouse_drag(self, nMouseButton, mouseX, mouseY, tuple(mouseButtonStates))
							else:
								if self.__on_mouse_button:
									self.__on_mouse_button(self, nMouseButton, bMouseDown, mouseX, mouseY, tuple(mouseButtonStates))
					# print(bMouseDown, nMouseButton, mouseX, mouseY)
				elif key is Console.Input.KEY_CTRL_C:
					if self.__on_ctrl_c:
						self.__on_ctrl_c(self, key)
					else:
						self.__bRun = False
				else:
					if self.__on_key_pressed:
						self.__on_key_pressed(self, key)

		finally:
			print(Console.MOUSE_DISABLE)
	#

#














