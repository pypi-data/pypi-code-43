import numpy as np
import sympy
import re
import sys
import copy

eq_attr_regex = r"\$\{([a-zA-Z_\/]+[a-zA-Z0-9_\/\(\)]*)\}"
equation_regex = "^(?P<eq>[\S\s]+)(?:\[)(\"(?P<name>[\S\s]*)\"\,){0,1}(?P<unit>[\S\s]*)(?:\])$"


def print_error(msg):
    sys.stderr.write(str(msg) + "\n")


def _eval_equation_list(data, equationString, do_lambdify = True):
    parsed_eq = _parse_main_equation(equationString)
    ds_list = parsed_eq["vars"]
    expression  = sympy.S(parsed_eq["equation"])

    if parsed_eq["success"] is False:
        print_error("Error: Failed to parse main equation to calculate data list")
        return np.array([])

    lengths = list(set(map(lambda x: len(data[x]), parsed_eq["vars"])))
    if len(lengths) > 1:
        print_error("Error: Lists involved in the equation are not equal in length")
        return np.array([])
    num_of_elements = lengths[0]


    #initialize the output array
    output_array    = np.empty(num_of_elements)
    output_array[:] = np.NaN

    if do_lambdify:
        try:
            lam_f = sympy.lambdify(tuple(ds_list), expression, modules='numpy')
        except:
            print_error("Error: Exception thrown while trying to lambdify the equation.")

        try:
            replacement_list = (np.array(data[ds_list[j]]) for j in range(len(ds_list)))
            output_array = np.double(lam_f(*replacement_list))
        except Exception as e:
            print_error("Error while evaluating equation expression. Exception says: " + str(e))

        is_nans_list = list(set(np.isnan(output_array)))
        if is_nans_list[0] == True and len(is_nans_list) == 1:
            print("Error: All equation output elements are NaN, which shows that the evaluation"
                  " of the equation failed. The output values will be replaced by zeros.")
            output_array = np.zeros(num_of_elements)
    else:

        for i in range(num_of_elements):
            rep_vals = {}
            for ds in ds_list:
                if re.match("___attr___(?P<attribute>[\w]+)", ds) is None:
                    rep_vals[ds] = data[ds][i]
                else:
                    rep_vals[ds] = data[ds][0]
            try:
                val = np.double(expression.subs(rep_vals))
            except Exception as e:
                print_error("Error while evaluating equation expression. Exception says: " + str(e))
                val = np.nan
            output_array[i] = val

    return output_array


def _parse_main_equation_multiple(eq_str):
    eq_str_split = eq_str.split("::")
    ret = []
    for eq in eq_str_split:
        ret.append(_parse_main_equation(eq))
    return ret


def _parse_main_equation(eq_str):
    """
    Parse the MainEquation and verify its validity
    Parameter: eqStr: The equation string
    Return: A dict with results. The element "success" of that dict
        is a boolean that indicates whether the parsing is success
    """
    if "__" in eq_str:
        print("Main equation cannot contain any variables with more than 1 underscore consequtively (_).")
        return {"success": False}

    def rep_ds_with_index_forward(s):
        # replace dataset's [[x]] with _____x_____ to avoid sympy replacement problems
        sv = str(s.group(0))
        sv = sv.replace("[[","")
        sv = sv.replace("]]","")
        return "_____" + sv + "_____"

    def rep_attr_forward(s):
        # replace attribute with ___attr___attribname to avoid sympy replacement problems
        sv = str(s.group(0))
        sv = sv.replace("${", "")
        sv = sv.replace("}", "")
        sv = sv.replace("/", "__")
        return "___attr___" + sv

    try:
        mt = re.match(equation_regex, eq_str)
        unit = mt.group("unit")
        name = mt.group("name")
        eq = mt.group("eq")
        eq = re.sub("\s+", "", eq)
        # replace for datasets with indices to indicate column number, so x[[5]]
        eq_tmp_reps = re.sub(r"\[\[\d+\]\]", rep_ds_with_index_forward, eq)
        # replace for attributes in the form ${dataset,attr}
        #eq_tmp_reps = re.sub(eq_attr_regex, rep_attr_forward, eq_tmp_reps)
        all_symbols = [str(x) for x in sympy.S(eq_tmp_reps).atoms(sympy.Symbol)]
        datasets = list(map(lambda x: re.sub(r"_____(\d)+_____", "", x), all_symbols))
        return {"success": True, "vars": all_symbols, "datasets": datasets, "units": unit,
                "equation": eq_tmp_reps, "original_equation": eq_str, "name": name}

    except Exception as e:
        print_error(e)
        return {"success": False}


# def GetHDF5FileData(fileObj,datasetsList):
#     """
#     Retrieves the data from a file.
#     The data can be a dataset in the form "dsName_____index_____" or
#             or an attribute of the form "___attr___attributeName___
#
#     Param: fileObj: HDF5 file object that's open
#     Param: datasetsList: List of string parameters to get
#     """
#     returnedData = {}
#     for ds in datasetsList:
#         only_ds = re.sub(r"_____\d+_____", "", ds)  #this doesn't contain indices
#         match_attr = re.match("___attr___(?P<dataset>[\w]+)__(?P<attribute>[\w]+)",only_ds)
#         match_attr_root = re.match("___attr___(?P<attribute>[\w]+)",only_ds)
#         if match_attr is not None:
#             attr_ds = match_attr.group("dataset")
#             attr_attr = match_attr.group("attribute")
#             returnedData[only_ds] = fileObj[attr_ds].attrs[attr_attr]
#         elif match_attr_root is not None:
#             attr_attr = match_attr_root.group("attribute")
#             returnedData[only_ds] = fileObj.attrs[attr_attr]
#         else:
#             if len(fileObj[only_ds].value.shape) == 1:
#                 ds_match = re.match(r"\S+_____\d+_____", ds)
#                 if ds_match is None:
#                     returnedData[ds] = fileObj[only_ds].value
#                 else:
#                     raise IndexError("Tried to choose an index for a single column dataset.")
#             elif len(fileObj[only_ds].value.shape) == 2: #if contains multiple columns, extract the column number
#                 ds_match = re.match(r"(?P<dsName>\S+)_____(?P<idx>\d*)_____", ds)
#                 if ds_match is None:
#                     raise re.error("Error: While the dimensionality of the data is 2, unable to match the requested variable (" + ds + ") with an index. Datasets provided: " + str(datasetsList))
#                 else:
#                     returnedData[ds] = fileObj[only_ds].value[:,int(ds_match.group("idx"))]
#
#             else:
#                 raise IndexError("Error: The dimensionality of the data in the dataset " + ds + " is not 1 or 2. This is not supported.")
#     return returnedData


def decode_string(str_in):
    if isinstance(str_in, bytes):
        ret_str = str_in.decode("ascii")
    else:
        ret_str = str_in
    return ret_str


def to_string(v):
    try:
        ret_val = v.astype(str)
    except AttributeError:
        ret_val = decode_string(v)
    return ret_val

def parse_equation_multiple(equations):
    equations_split = equations.split("::")
    ret = []
    for eq in equations_split:
        ret.append(parse_equation(eq))
    return ret

def parse_equation(equation):
    """
    Parse the MainEquation and verify its validity
    Parameter: equation: The equation string
    Return: A dict with results. The element "success" of that dict
        is a boolean that indicates whether the parsing is success.
        The following are expected returns in the dict:
        If "success" is False:
            "msg": Error message
        If "success" is True:
           "units": units parsed
           "name": name of the value parsed
           "datasets": datasets involved
           "datasets_indices": datasets involved, including indices in the form dataset_____idx_____
               where idx is the column number
           "attrs": attributes involved in the equation, if any
           "eq": The equation, stripped from units and name
    """
    attribs_list = []
    counter = [0]
    def rep_ds_with_index_forward(s):
        # replace dataset's [[x]] with _____x_____ to avoid sympy replacement problems
        sv = str(s.group(0))
        sv = sv.replace("[[","")
        sv = sv.replace("]]","")
        return "_____" + sv + "_____"

    def _rep_attr(s):
        # replace attribute with ___attr___attribname to avoid sympy replacement problems
        attrname = str(s.group(0))
        attrname = attrname.replace("${", "")
        attrname = attrname.replace("}", "")
        counter[0] += 1
        ret = "_____attr_____" + str(counter[0])
        attribs_list.append([attrname,ret])
        for i in range(len(attribs_list)-1):
            # replace recursive values that are named with temporary names
            attribs_list[-1][0] = attribs_list[-1][0].replace(attribs_list[i][1],attribs_list[i][0])
        return ret

    try:
        mt = re.match(equation_regex, equation)
        if mt is None:
            raise SyntaxError("Parsing equation failed. It doesn't follow the standard syntax.")
        unit = mt.group("unit")
        name = mt.group("name")
        eq = mt.group("eq")
        eq = re.sub("\s+", "", eq)  # remove spaces

        # recursively, substitute all attributes, until substitutions don't make any change
        prev_eq = eq
        curr_eq = eq
        while True:
            curr_eq = re.sub(eq_attr_regex, _rep_attr, prev_eq)
            # if no more substitutions change the equation, stop!
            if curr_eq == prev_eq:
                break
            else:
                prev_eq = curr_eq

        # replace for datasets with indices to indicate column number, so x[[5]]
        curr_eq = re.sub(r"\[\[\d+\]\]", rep_ds_with_index_forward, curr_eq)

        variables = [str(x) for x in sympy.S(curr_eq).atoms(sympy.Symbol)]
        variables = [x for x in variables if (re.match(r"_____attr_____\d+", x) is None)]  # remove attributes
        attribs_list = [x[0] for x in attribs_list]
        datasets = [re.sub(r"_____\d+_____", "", x) for x in variables]  # remove datasets indices
        return {"success": True, "units": unit, "name": name, "datasets": datasets, "datasets_indices": variables,
                "attrs": attribs_list, "equation": eq}

    except Exception as e:
        print_error("Failed to parse equation. Error: " + str(e))
        return {"success": False, "msg": str(e)}


def eval_equation_multiple(equations, do_lambdify = True, file=None,
                           dataset_getter=None, attr_getter=None):
    equations_split = equations.split("::")
    ret = []
    for eq in equations_split:
        ret.append(eval_equation(eq, do_lambdify, file,
                                          dataset_getter, attr_getter))
    return ret


def eval_equation(equation, do_lambdify = True, file = None,
                  dataset_getter = None, attr_getter = None):
    """
    Uses an HDF5 file object or dataset and attribute getters to evaluate an equation
    Format of the equation: Datasets as variables, attributes as ${attr}
        for global attributes and ${Dataset/attr} for attributes in datasets
    You can either specify a file, OR dataset_getter and attr_getter functions;
        these functions take 1 parameter only, which is the attribute name in
        the format dataset/attribute or a global attribute name. For datasets,
        if there are multiple columns, it should be supplied as dataset[i]
    Param: equation: Equation to be evaluated
    Param: file: HDF5 file object that's open
    """
    def _default_get_attr_from_file(attr):
        parts = attr.split("/")
        if len(parts) == 1:
            return to_string(file.attrs[parts[0]])
        elif len(parts) == 2:
            return to_string(file[parts[0]].attrs[parts[1]])
        else:
            raise SyntaxError("Only 1 level datasets are supported "
                              "for exctracting attributes. E.g.: "
                              "${dataset/attr} or ${attr}.")

    def _default_get_dataset_from_file(dataset):
        only_ds = re.sub(r"_____\d+_____", "", ds)  #this doesn't contain indices
        if len(file[only_ds].value.shape) == 1:
            ds_match = re.match(r"\S+_____\d+_____", ds)
            if ds_match is None:
                return copy.copy(file[only_ds].value)
            else:
                raise IndexError("Tried to choose an index for a single column dataset.")
        elif len(file[only_ds].value.shape) == 2: #if contains multiple columns, extract the column number
            ds_match = re.match(r"(?P<dsName>\S+)_____(?P<idx>\d*)_____", ds)
            if ds_match is None:
                raise re.error("Error: While the dimensionality of the data is 2, unable to match the requested variable (" + ds + ") with an index. Datasets provided: " + str(parsed_eq["vars"]))
            else:
                return copy.copy(file[only_ds].value[:,int(ds_match.group("idx"))])
        else:
            raise IndexError("Error: The dimensionality of the data in the dataset " + ds + " is not 1 or 2. This is not supported.")

    if file is None and dataset_getter is None and attr_getter is None:
        print_error("You should either set a file object or dataset and attribute getters")
        return []

    if file is not None:
        attr_getter_internal = _default_get_attr_from_file
        dataset_getter_internal = _default_get_dataset_from_file
    else:
        if dataset_getter is None and attr_getter is None:
            raise IOError("You should either specify a file, or "
                          "dataset and attribute getters")
        else:
            dataset_getter_internal = dataset_getter
            attr_getter_internal = attr_getter

    def _rep_attr(s):
        # replace attribute's format ${attrib} with ___attr___attribname to avoid sympy replacement problems
        if attr_getter_internal is None:
            raise IOError("Requested attributes without setting attr_getter"
                          " or setting a file object")
        sv = str(s.group(0))
        sv = sv.replace("${", "")
        sv = sv.replace("}", "")
        try:
            ret = attr_getter_internal(sv)
            return ret
        except Exception as e:
            print_error("Attribute substitution failed. Exception says: " + str(e))
            raise

    # recursively, substitute all attributes
    prev_eq = equation
    curr_eq = equation
    while True:
        curr_eq = re.sub(eq_attr_regex, _rep_attr, prev_eq)
        # if no more substitutions change the equation, stop!
        if curr_eq == prev_eq:
            break
        else:
            prev_eq = curr_eq
    returned_data = {}
    parsed_eq = parse_equation(curr_eq)
    if not parsed_eq["success"]:
        raise SyntaxError("Parsing equation failed. Error says: " + str(parsed_eq["msg"]))

    if len(parsed_eq["datasets_indices"]) != 0:
        if dataset_getter_internal is None:
            raise IOError("Requested datasets without setting dataset_getter"
                          " or setting a file object")

    for ds in parsed_eq["datasets_indices"]:
        try:
            returned_data[ds] = dataset_getter_internal(ds)
        except Exception as e:
            print_error("Dataset pulling failed. Exception says: " + str(e))
            raise

    return _eval_equation_list(returned_data, curr_eq, do_lambdify)
