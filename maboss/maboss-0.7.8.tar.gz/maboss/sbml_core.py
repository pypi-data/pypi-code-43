import libsbml
import re
from .ast import logExp as logExpAST
from .ast import ASTReal, ASTVar, ASTBool, ASTNot, ASTAnd, ASTOr, ASTXor, ASTIFE

"""
	Here we want to use stochastic event execution to simulate maboss models
	The logic is : in sbml we can have various events, with the same trigger, and same priority, 
	competing to execute.
	
	If we have 2 such events, each event will have a probability p=0.5 to execute.
	We want to use that to execute stochastic transitions. 
	
	Let's say we have activation executing with rt_up = 1.0, and inactivation with rt_down = 5.0
	This could be translated to a model with two sets of 6 (5+1) events : 
	
	- The activation events, 5 of which would not change the variable state, and one actually activating it
	- The inactivation events, 1 of which would not change the variable state, and 5 which would actually activating it. 
	
	The   
	
"""

def getAST(formula):
	if formula is not None:
		return logExpAST.parseString(formula).asDict()['AST']



def booleanToSBML(node, forceBoolean=False):

	if isinstance(node, ASTReal):
		sbml_node = libsbml.ASTNode()
		if forceBoolean:
			if node.args == 1.0:
				sbml_node.setType(libsbml.AST_CONSTANT_TRUE)
			else:
				sbml_node.setType(libsbml.AST_CONSTANT_FALSE)
		else:
			sbml_node.setType(libsbml.AST_REAL)
			sbml_node.setValue(float(node.args[0]))
		return sbml_node

	elif isinstance(node, ASTBool):
		sbml_node = libsbml.ASTNode()

		if node.args[0] == 'TRUE':
			sbml_node.setType(libsbml.AST_CONSTANT_TRUE)
		elif node.args[0] == 'FALSE':
			sbml_node.setType(libsbml.AST_CONSTANT_FALSE)
		else:
			print("Unrecognized boolean value : %s" % node.args[0])
		return sbml_node

	elif isinstance(node, ASTVar):
		sbml_node = libsbml.ASTNode()
		sbml_node.setType(libsbml.AST_NAME)
		sbml_node.setName(node.args[0].replace('$', '_'))
		return sbml_node

	elif isinstance(node, ASTNot):
		sbml_node = libsbml.ASTNode()
		sbml_node.setType(libsbml.AST_LOGICAL_NOT)
		sbml_node.addChild(booleanToSBML(node.args[0]))
		return sbml_node

	elif isinstance(node, ASTAnd):
		sbml_node = libsbml.ASTNode()
		sbml_node.setType(libsbml.AST_LOGICAL_AND)

		for arg in node.args:
			sbml_node.addChild(booleanToSBML(arg))

		return sbml_node

	elif isinstance(node, ASTOr):
		sbml_node = libsbml.ASTNode()
		sbml_node.setType(libsbml.AST_LOGICAL_OR)

		for arg in node.args:
			sbml_node.addChild(booleanToSBML(arg))

		return sbml_node

	elif isinstance(node, ASTXor):
		sbml_node = libsbml.ASTNode()
		sbml_node.setType(libsbml.AST_LOGICAL_XOR)

		for arg in node.args:
			sbml_node.addChild(booleanToSBML(arg))

		return sbml_node

	elif isinstance(node, ASTIFE):

		sbml_node = libsbml.ASTNode()
		sbml_node.setType(libsbml.AST_FUNCTION_PIECEWISE)

		sbml_node.addChild(booleanToSBML(node.args[1]))
		sbml_node.addChild(booleanToSBML(node.args[0]))
		sbml_node.addChild(booleanToSBML(node.args[2]))

		return sbml_node

	else:
		print("Error : Unrecognized type : %s (%s)" % (type(node), str(node)))

def addContinuousSpecies(sbml_model, sid, species, initial_state):
	new_species = sbml_model.createSpecies()
	new_species.setName(species.name)
	new_species.setId(sid)
	new_species.setInitialAmount(initial_state)
	new_species.setCompartment("cell")
	new_species.setConstant(False)
	sbml_model.addSpecies(new_species)



def addParameter(sbml_model, name, value):

	new_param = sbml_model.createParameter()
	if name.startswith('$'):
		new_param.setName(name[1: len(name)])
		new_param.setId("_%s" % name[1: len(name)])
	else:
		new_param.setName(name)
		new_param.setId(name)

	new_param.setValue(value)
	sbml_model.addParameter(new_param)

def addCompartment(sbml_model, name="Cell", value=1):

	compartment = sbml_model.createCompartment()
	compartment.setName(name)
	compartment.setId(name.lower())
	compartment.setSize(value)

# def addIndividualEvent(sbml_model, species, formula, i_species):
#
# 	if not (isintance(species.rt_up, int) or isinstance(species.rt_up, float)):


def createResetTrigger(parameter, time_ech):

	node_reset = libsbml.ASTNode()
	node_reset.setType(libsbml.AST_NAME)
	node_reset.setName(parameter)

	node_time = libsbml.ASTNode()
	node_time.setType(libsbml.AST_NAME_TIME)
	node_time.setName("time")

	node_substraction = libsbml.ASTNode()
	node_substraction.setType(libsbml.AST_MINUS)
	node_substraction.addChild(node_time)
	node_substraction.addChild(node_reset)

	node_1 = libsbml.ASTNode()
	node_1.setType(libsbml.AST_REAL)
	node_1.setValue(time_ech)

	node_geq = libsbml.ASTNode()
	node_geq.setType(libsbml.AST_RELATIONAL_GEQ)
	node_geq.addChild(node_substraction)
	node_geq.addChild(node_1)

	return node_geq

def addExistingValueToReset(parameter, species, existing_value, time_ech):

	node_value = libsbml.ASTNode()
	node_value.setType(libsbml.AST_REAL)
	node_value.setValue(existing_value)

	node_species = libsbml.ASTNode()
	node_species.setType(libsbml.AST_NAME)
	node_species.setName(species)

	node_equal = libsbml.ASTNode()
	node_equal.setType(libsbml.AST_RELATIONAL_EQ)
	node_equal.addChild(node_value)
	node_equal.addChild(node_species)

	node_and = libsbml.ASTNode()
	node_and.setType(libsbml.AST_LOGICAL_AND)
	node_and.addChild(node_equal)
	node_and.addChild(createResetTrigger(parameter, time_ech))

	return node_and

def addResetToTrigger(tree, parameter, species, existing_value, time_ech):

	node_geq = addExistingValueToReset(parameter, species, existing_value, time_ech)

	new_node = libsbml.ASTNode()
	new_node.setType(libsbml.AST_LOGICAL_AND)
	new_node.addChild(booleanToSBML(tree))
	new_node.addChild(node_geq)

	return new_node

def addResetAssignment(event, reset_var):

	# The reset assignment
	assignment_reset = event.createEventAssignment()
	assignment_reset.setVariable(reset_var)

	ast_time = libsbml.ASTNode()
	ast_time.setType(libsbml.AST_NAME_TIME)
	ast_time.setName("time")

	assignment_reset.setMath(ast_time)


def addRealEvent(sbml_model, trigger, species, reset_var, new_value):

	event = sbml_model.createEvent()

	ast_priority = libsbml.ASTNode()
	ast_priority.setType(libsbml.AST_REAL)
	ast_priority.setValue(1.0)
	event_priority = event.createPriority()
	event_priority.setMath(ast_priority)

	event_trigger = event.createTrigger()
	event_trigger.setPersistent(False)
	event_trigger.setMath(trigger)

	# The reset assignment
	addResetAssignment(event, reset_var)

	# The real assignment
	event_assignment_var = event.createEventAssignment()
	event_assignment_var.setVariable(species)

	ast_new_value = libsbml.ASTNode()
	ast_new_value.setType(libsbml.AST_REAL)
	ast_new_value.setValue(new_value)

	event_assignment_var.setMath(ast_new_value)

def addFakeEvent(sbml_model, trigger, reset_var):

	event = sbml_model.createEvent()

	ast_priority = libsbml.ASTNode()
	ast_priority.setType(libsbml.AST_REAL)
	ast_priority.setValue(1.0)
	event_priority = event.createPriority()
	event_priority.setMath(ast_priority)

	event_trigger = event.createTrigger()
	event_trigger.setPersistent(False)
	event_trigger.setMath(trigger)

	addResetAssignment(event, reset_var)

def addAction(sbml_model, species, tree, reset_var, existing_value, new_value, time_ech):

	if tree.operator == 'ife':
		# Then we have the trigger, the rate is true, and the rate if false
		# Meaning we will have 4 events :
		# - two competing if trigger is true
		# - two competing if trigger is false
		condition_true = tree.args[0]
		# First, if trigger is true:
		# The real activation
		eup_trigger_formula = addResetToTrigger(condition_true, reset_var, species, existing_value, time_ech)

		addRealEvent(sbml_model, eup_trigger_formula, species, reset_var, new_value)
		addFakeEvent(sbml_model, eup_trigger_formula, reset_var)

	elif tree.operator == 'real':

		# reset_up_var = "reset_up_%d" % i_species
		eup_trigger_formula = addExistingValueToReset(reset_var, species, existing_value, time_ech)
		addRealEvent(sbml_model, eup_trigger_formula, species, reset_var, new_value)
		addFakeEvent(sbml_model, eup_trigger_formula, reset_var)



def addEvents(sbml_model, species, i_species, time_ech):

	internal_var = {("@%s" % key): getAST(value) for key, value in species.internal_var.items()}

	tree = getAST(species.rt_up).develop(getAST(species.logExp), internal_var)
	addAction(sbml_model, species.name, tree, "reset_up_%d" % i_species, 0.0, 1.0, time_ech)

	tree = getAST(species.rt_down).develop(getAST(species.logExp), internal_var)
	addAction(sbml_model, species.name, tree, "reset_down_%d" % i_species, 1.0, 0.0, time_ech)



def to_sbml(model, filename, time_ech=1):

	sbml_doc = libsbml.SBMLDocument(3, 1)
	sbml_model = sbml_doc.createModel()

	addCompartment(sbml_model)

	initial_state = model.get_initial_state()

	for ind, (sid, species) in enumerate(model.network.items()):
		addContinuousSpecies(sbml_model, sid, species, initial_state[sid])
		addParameter(sbml_model, 'reset_up_%d' % ind, 0)
		addParameter(sbml_model, 'reset_down_%d' % ind, 0)
		addEvents(sbml_model, species, ind, time_ech)

	for param, value in model.param.items():
		if param.startswith("$"):
			addParameter(sbml_model, param, float(value))



	libsbml.writeSBMLToFile(sbml_doc, filename)
	return sbml_doc