# REFACTORING-NOTE: Currently this class only supports ODE model exports, thus it should belong in .ode
# However the idea for the future is to support all kinds of model exports, in which case
# this class here should contain a common interface to all of them and the sbml import and
# export functions should be included in the respective model classes.


import libsbml
import warnings
import itertools

# I need this import for models using numpy to be able to use create_model_from_sbml,
# as otherwise they cannot access it. It's a bit hacky, but it works :)
# If you exec in your session or just save it to the file it will work without this
import numpy as np

###############################################################################
# MODELBASE TO SBML
###############################################################################


def _add_parameters(mb_model, sbml_model):
    for k, v in mb_model.get_all_parameters().items():
        par = sbml_model.createParameter()
        par.setId(k)
        par.setConstant(True)
        par.setValue(v)


def _add_compounds(mb_model, sbml_model):
    for cpd in mb_model.get_compounds().keys():
        s = sbml_model.createSpecies()
        s.setId(cpd)
        s.setName(cpd)


def _add_algebraic_modules(mb_model, sbml_model):
    for name, am_dict in mb_model._algebraic_modules.items():
        func, vars, der_vars = am_dict.values()

        for der_var in der_vars:
            module = sbml_model.createAssignmentRule()
            if name.endswith(f"_{der_var}"):
                module.setIdAttribute(f"{name}")
            else:
                module.setIdAttribute(f"{name}_{der_var}")
            module.setVariable(der_var)

            math_ast = libsbml.parseL3Formula(
                mb_model._module_templates[name].mod_func_strgs()[der_var]
            )
            module.setMath(math_ast)


def _add_reactions(mb_model, sbml_model):
    for reaction, stoichs in mb_model.get_stoichiometries().items():
        rec = sbml_model.createReaction()
        rec.setId(reaction)
        for species, stoich in stoichs.items():
            if stoich < 0:
                species_ref = rec.createReactant()
            else:
                species_ref = rec.createProduct()
            species_ref.setSpecies(species)
            species_ref.setStoichiometry(abs(stoich))
        for modifier in mb_model._ratelaws[reaction].modifiers:
            species_ref = rec.createModifier()
            species_ref.setSpecies(modifier)
        math_ast = libsbml.parseL3Formula(mb_model._ratelaws[reaction].rate_func_str())
        kinetic_law = rec.createKineticLaw()
        kinetic_law.setMath(math_ast)


def _convert_modelbase_to_sbml(mb_model):
    document = libsbml.SBMLDocument(3, 2)  # level, version
    sbml_model = document.createModel()
    _add_parameters(mb_model, sbml_model)
    _add_compounds(mb_model, sbml_model)
    _add_algebraic_modules(mb_model, sbml_model)
    _add_reactions(mb_model, sbml_model)
    return document


def write_to_sbml(m, filename=None):
    warnings.warn("Experimental class, API might change.", FutureWarning)
    document = _convert_modelbase_to_sbml(m)
    if filename is None:
        return libsbml.writeSBMLToString(document)
    libsbml.writeSBMLToFile(document, filename)


###############################################################################
# SBML TO MODELBASE
###############################################################################


def _split_math_string(math_string):
    return (
        math_string.replace("(", " ( ")
        .replace(")", " ) ")
        .replace(",", " , ")
        .replace("+", " + ")
        .replace("-", " - ")
        .replace("*", " * ")
        .replace("/", " / ")
        .split()
    )


def _replace_functions(i):
    replace_table = {
        "log": "np.log",
        "ln": "np.log",
        "log10": "np.log10",
        "pow": "np.pow",
        "exp": "np.exp",
        "root": "np.root",
        "sin": "np.sin",
        "cos": "np.cos",
        "tan": "np.tan",
        "sinh": "np.sinh",
        "cosh": "np.cosh",
        "tanh": "np.tanh",
        "arccos": "np.arccos",
        "arcsin": "np.arcsin",
        "arctan": "np.arctan",
        "arctanh": "np.arctanh",
        "floor": "np.floor",
        "ceil": "np.ceil",
        "ceiling": "np.ceil",
        "piecewise": "np.piecewise",
        "pi": "np.pi",
        "inf": "np.infty",
        "exponentiale": "np.e",
        "notanumber": "np.nan",
        "gt": "np.greater",
        "greater": "np.greater",
        "lt": "less",
        "less": "less",
        "ge": "np.greater_equal",
        "geq": "np.greater_equal",
        "greater_equal": "np.greater_equal",
        "le": "np.less_equal",
        "leq": "np.less_equal",
        "less_equal": "np.less_equal",
        "eq": "np.equal",
        "equal": "np.equal",
        "neq": "np.not_equal",
        "not_equal": "np.not_equal",
    }
    if i in replace_table:
        return replace_table[i]
    return i


def _get_parameters(model):
    return {i.getId(): i.getValue() for i in model.getListOfParameters()}


def _get_compounds(model):
    compounds = [i.getId() for i in model.getListOfSpecies()]
    return compounds


def _get_all_compounds(model):
    compounds = _get_compounds(model).copy()
    for rec in model.getListOfReactions():
        for i in rec.getListOfReactants():
            i = i.getSpecies()
            if i not in compounds:
                compounds.append(i)
        for i in rec.getListOfProducts():
            i = i.getSpecies()
            if i not in compounds:
                compounds.append(i)
        for i in rec.getListOfModifiers():
            i = i.getSpecies()
            if i not in compounds:
                compounds.append(i)
    if "time" in compounds:
        compounds.remove("time")
    return compounds


def _get_reactions(model, parameters, compounds):
    reactions = {}
    for rec in model.getListOfReactions():
        name = rec.getId()
        substrate_stoichs = {
            i.getSpecies(): i.getStoichiometry() * -1 for i in rec.getListOfReactants()
        }
        product_stoichs = {
            i.getSpecies(): i.getStoichiometry() for i in rec.getListOfProducts()
        }
        stoichs = dict(**substrate_stoichs, **product_stoichs)

        substrates = list(substrate_stoichs.keys())
        modifiers = [i.getSpecies() for i in rec.getListOfModifiers()]
        rate_vars = substrates + modifiers

        formula = rec.getKineticLaw().getFormula()
        rate_law = _split_math_string(formula)
        rate_law = [_replace_functions(i) for i in rate_law]

        pars = []
        for i in rate_law:
            if i in parameters:
                if i not in pars:
                    pars.append(i)
        rate_func = "".join([f"p.{i}" if i in parameters else i for i in rate_law])

        rlf = f"class {name}(modelbase.ode.ratelaws.BaseRateLaw):\n"
        rlf += f"    def __init__(self, {', '.join(pars)}, substrates, modifiers):\n"
        rlf += f"        super().__init__(substrates=substrates, modifiers=modifiers)\n"
        for p in pars:
            rlf += f'        self.pars["{p}"] = {p}\n'
        rlf += "\n"
        rlf += "    def rate_func_str(self):\n"
        rlf += f'        return "{formula}"\n\n'
        rlf += f"    def rate_func({', '.join(['self', 'p'] + rate_vars)}):\n"
        rlf += f"        return {rate_func}\n"

        reactions[name] = {
            "ratelaw": rlf,
            "stoich": stoichs,
            "parameters": pars,
            "substrates": substrates,
            "modifiers": modifiers,
        }
    return reactions


def _get_algebraic_modules(model, parameters, compounds):
    modules = {}
    for rule in model.getListOfRules():
        name = rule.getIdAttribute()
        der_var = rule.getVariable()
        formula = rule.getFormula()
        mod_formula = _split_math_string(formula)
        mod_formula = [_replace_functions(i) for i in mod_formula]
        variables = [i for i in mod_formula if i in compounds]
        pars = []
        for i in mod_formula:
            if i in parameters:
                if i not in pars:
                    pars.append(i)
        mod_formula = "".join([f"p.{i}" if i in parameters else i for i in mod_formula])

        rlf = f"class {name}(modelbase.ode.ratelaws.BaseAlgebraicModule):\n"
        rlf += f"    def __init__(self, {', '.join(pars)}, variables, derived_variables):\n"
        rlf += f"        super().__init__(variables=variables, derived_variables=derived_variables)\n"
        for p in pars:
            rlf += f'        self.pars["{p}"] = {p}\n'
        rlf += "\n"
        rlf += "    def mod_func_strgs(self):\n"
        formula = '"' + "".join(formula.split()) + '"'
        rlf += "        return {self.derived_variables[0]:" + formula + "}\n\n"
        rlf += f"    def mod_func({', '.join(['self', 'p'] + variables)}):\n"
        rlf += f"        return [{mod_formula}]\n"

        modules[name] = {
            "func": rlf,
            "parameters": pars,
            "vars": variables,
            "der_vars": [der_var],
        }
    return modules


def _read_sbml_document(xml):
    """Read file or string"""
    if xml.startswith("<?xml"):
        document = libsbml.readSBMLFromString(xml)
    else:
        document = libsbml.readSBMLFromFile(xml)
    if document.getLevel() != 3 or document.getVersion() != 2:
        warnings.warn("Support for SBML versions != 3.2 is not tested")
    return document.getModel()


def _generate_algebraic_module_templates(algebraic_modules):
    s = ""
    for name, d in algebraic_modules.items():
        func, pars, variables, der_vars = d.values()
        s += func + "\n\n"
    return s


def _generate_rate_law_templates(reactions):
    s = ""
    for name, d in reactions.items():
        func, stoich, pars, substrates, modifiers = d.values()
        s += func + "\n\n"
    return s


def _generate_algebraic_module_functions(model_name, algebraic_modules):
    s = ""
    for name, d in algebraic_modules.items():
        func, pars, variables, der_vars = d.values()
        s += f"{model_name}.add_algebraic_module_from_template(\n"
        s += f"    name='{name}',\n"
        s += f"    module_template={name},\n"
        s += f"    parameters={pars},\n"
        s += f"    variables={variables},\n"
        s += f"    derived_variables={der_vars}\n"
        s += f")\n"
    return s


def _generate_reaction_functions(model_name, reactions):
    s = ""
    for name, d in reactions.items():
        func, stoich, pars, substrates, modifiers = d.values()
        s += f"{model_name}.add_reaction_from_ratelaw(\n"
        s += f"    name='{name}',\n"
        s += f"    ratelaw={name},\n"
        s += f"    stoichiometries={stoich},\n"
        s += f"    parameters={pars},\n"
        s += f"    substrates={substrates},\n"
        s += f"    modifiers={modifiers},\n"
        s += f")\n"
    s += "\n"
    return s


def _generate_initial_conditions(compounds, model):
    s = ""
    y0 = dict(zip(compounds, itertools.repeat(0)))
    for i in model.getListOfSpecies():
        if i.isSetInitialAmount():
            y0[i.id] = i.getInitialAmount()
    s += f"y0 = {y0}\n"
    return s


def generate_modelbase_sourcecode_from_sbml(xml, model_name="m"):
    """Read sbml xml file or string and return the modelbase representation of the model.
    xml : path or str
        xml file or string
    model_name: str
        The name of the python variable for the model
    """
    warnings.warn("Experimental class, API might change.", FutureWarning)
    model = _read_sbml_document(xml)
    parameters = _get_parameters(model)
    compounds = _get_compounds(model)
    all_compounds = _get_all_compounds(model)
    reactions = _get_reactions(model, parameters, all_compounds)
    algebraic_modules = _get_algebraic_modules(model, parameters, all_compounds)

    s = "import modelbase\n"
    s += "import numpy as np\n\n"

    s += _generate_algebraic_module_templates(algebraic_modules)
    s += _generate_rate_law_templates(reactions)

    # Model instantiation
    s += f"parameters = {parameters}\n\n"
    s += f"{model_name} = modelbase.ode.Model(parameters)\n"
    s += f"{model_name}.add_compounds({compounds})\n\n"

    s += _generate_algebraic_module_functions(model_name, algebraic_modules)
    s += _generate_reaction_functions(model_name, reactions)
    s += _generate_initial_conditions(compounds, model)
    return s


def create_model_from_sbml(xml, model_name="m"):
    """Read sbml xml file or string and return a modelbase model object.
    xml : path or str
        xml file or string
    model_name: str
        The name of the python variable for the model
    """
    warnings.warn("Experimental class, API might change.", FutureWarning)
    source_code = generate_modelbase_sourcecode_from_sbml(xml, model_name)
    exec(source_code, globals(), locals())
    return locals()[model_name]
