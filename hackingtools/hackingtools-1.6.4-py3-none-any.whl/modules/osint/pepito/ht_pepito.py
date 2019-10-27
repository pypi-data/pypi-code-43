from hackingtools.core import Logger, Utils, Config
import hackingtools as ht
import os

config = Config.getConfig(parentKey='modules', key='ht_pepito')
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))

class StartModule():

	def __init__(self):
		pass

	def help(self):
		Logger.printMessage(message=ht.getFunctionsNamesFromModule('ht_pepito'), debug_module=True)

	def hola(self, mensaje='', edad=23, casado=False):
		return '{m} - {e} - {ee}'.format(m=mensaje, e=edad, ee='estas casado' if casado else 'no te quiere nadie')