
import os
import sys

from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath

from kivy.config import Config
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase

import kivy
from kivy.resources import resource_add_path
resource_add_path(os.path.join(os.path.dirname(__file__),'./ttf'))
Config.set('kivy', 'default_font', [
    'msgothic',
    'DroidSansFallback.ttf'])

from kivy.app import App
# from .baseWidget import baseWidgets
# from .widgetExt import Messager
# from .externalwidgetmanager import ExternalWidgetManager
from .threadcall import HttpClient,Workers
from .derivedWidget import buildWidget, loadUserDefinedWidget
from .utils import *

class BlocksApp(App):
	myFontSizes = {
		"smallest":1.5,
		"small":3,
		"normal":4.5,
		"large":6,
		"huge":7.5,
		"hugest":9,
	}
	separatorsize = 2

	def urlwidget(self,**kw):
		url = kw.get('url')
		if url is None:
			raise ArgumentError('url','urlwidget miss a url argument')
		parenturl = kw.get('parenturl')
		url = absurl(url,parenturl)
		x = None
		dic = App.get_running_app().hc.get(url)
		if dic is not None:
			ancestor = kw.get('ancestor')
			x = buildWidget(dic, ancestor=ancestor,parenturl=url)
		
		return x

	def filewidget(self,**kw):
		filename = kw.get('filename')
		if filename is None:
			raise ArgumentError('filename','filewidget miss a filename argument')
		b = ''
		with codecs.open(filename,'r','utf-8') as f:
			b = f.read()
		if b == '':
			return None
		dic = json.loads(b)
		ancestor = kw.get('ancestor')
		x = buildwidget(dic,ancestor)
		return x

	def build(self):
		config = getConfig()
		self.config = config
		self.workers = Workers(maxworkers=config.maxworkers or 80)
		self.workers.start()
		self.hc = HttpClient()
		WindowBase.softinput_mode='below_target'
			
		if config.font_sizes:
			self.myFontSizes = config.font_sizes

		self.font_size = self.getFontSize(config.font_name)
		x = None
		loadUserDefinedWidget()
		if config.root:
			x = buildWidget(config.root)
			self.rootWidget = x
			return x
		raise Exception('please define root widget')
			
	def getFontSize(self,name=None):
		if name is None:
			name = self.config.font_name
		x = self.myFontSizes.get(name,None)
		if x == None:
			x = self.myFontSizes.get('normal')
		return x

	def namedSize(self,cnt=1,name=None):
		return mm(cnt * self.getFontSize(name=name))

	def textsize(self,x,y=None,name=None):
		"""
		deparent
		"""
		xr = self.namedSize(cnt=x,name=name)
		if y is None:
			return xr
		return (xr,self.namedSize(cnt=y,name=name))
	
	def unitedSize(self,x,y=None,name=None):
		xr = self.namedSize(cnt=x,name=name)
		if y is None:
			return xr
		return (xr,self.namedSize(cnt=y,name=name))

	def buttonsize(self,x):
		m = int(0.6 * self.font_size)
		return (sp(int(self.font_size * x + m),
					sp(self.font_size + m )))
	def __del__(self):
		self.workers.running = False		
