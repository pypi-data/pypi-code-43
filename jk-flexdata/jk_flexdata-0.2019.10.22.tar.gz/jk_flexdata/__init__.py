


from jk_testing import Assert

from .flexdata import FlexObject



bJSONCfgHelperAvailable = False
try:
	import jk_jsoncfghelper2
	import json
	bJSONCfgHelperAvailable = True
except ImportError:
    pass



#
# Load data from a file and check it against the structure <c>checkerName</c> defined in <c>scmgr</c>.
#
# @param	str filePath										The path of the file to load.
# @param	jk_jsoncfghelper2.StructureCheckerManager scmgr		The structure checker manager that holds the verification schemas
# @param	str structureTypeName								The name of the structure type the data should be conform to
# @return	FlexObject		A <c>FlexObject</c>.
#
def loadFromFile(filePath:str, scmgr = None, structureTypeName:str = None) -> FlexObject:
	assert isinstance(filePath, str)

	if bJSONCfgHelperAvailable:
		if scmgr or structureTypeName:
			Assert.isIn(scmgr.__class__.__name__, [ "StructureCheckerManager", "jk_jsoncfghelper2.StructureCheckerManager" ])
			Assert.isInstance(structureTypeName, str)

		with open(filePath, "r") as f:
			data = json.load(f)
		assert isinstance(data, dict)

		if scmgr or structureTypeName:
			checker = scmgr.getE(structureTypeName)
			if checker.checkB(scmgr, data):
				return FlexObject(data)
			else:
				raise Exception("Data does not match type " + repr(structureTypeName))	# TODO
		else:
			return FlexObject(data)

	else:
		if (scmgr is not None) or (structureTypeName is not None):
			raise Exception("As module jk_jsoncfghelper2 is not installed, scmgr and structureTypeName must noe None!")

		with open(filePath, "r") as f:
			data = json.load(f)
		assert isinstance(data, dict)

		return FlexObject(data)
#

#
# Convert the data and check it against the structure <c>checkerName</c> defined in <c>scmgr</c>.
#
# @param	dict data											The data.
# @param	jk_jsoncfghelper2.StructureCheckerManager scmgr		The structure checker manager that holds the verification schemas
# @param	str structureTypeName								The name of the structure type the data should be conform to
# @return	FlexObject		A <c>FlexObject</c>.
#
def createFromData(data:dict, scmgr = None, structureTypeName:str = None) -> FlexObject:
	assert isinstance(data, dict)

	if bJSONCfgHelperAvailable:
		if scmgr or structureTypeName:
			Assert.isIn(scmgr.__class__.__name__, [ "StructureCheckerManager", "jk_jsoncfghelper2.StructureCheckerManager" ])
			Assert.isInstance(structureTypeName, str)

		if scmgr or structureTypeName:
			checker = scmgr.getE(structureTypeName)
			if checker.checkB(scmgr, data):
				return FlexObject(data)
			else:
				raise Exception("Data does not match type " + repr(structureTypeName))	# TODO
		else:
			return FlexObject(data)

	else:
		if (scmgr is not None) or (structureTypeName is not None):
			raise Exception("As module jk_jsoncfghelper2 is not installed, scmgr and structureTypeName must noe None!")

		return FlexObject(data)
#






__version__ = "0.2019.10.22"

