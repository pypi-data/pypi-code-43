#!/usr/bin/python3

"""
simple_plotter - simple 2d curve plotting front-end and numpy/matplotlib code generator
Copyright (C) 2018, 2019  Thies Hecker

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import matplotlib.pyplot as plt
import numpy as np  # needs to be imported, since we launch code with exec which contains numpy statements
import jsonpickle
import json

# might be helpful for debugging, when parser is launched from GUI...
try:
    import faulthandler
    faulthandler.enable()
except ModuleNotFoundError:
    print("faulthandler module not found. If you want additional program output for debugging purposes, "
          "please install the faulthandler module.")


def check_valid_input(input_value):
    """Checks if an input value corresponds to a valid value - i.e. not None, "", "None",...

    Args:
        input_value: Any type of input value

    Returns:
        bool: True if valid

    """

    if input_value is None or input_value == "" or input_value == "None":
        valid = False
    else:
        valid = True

    return valid


class Formula:

    def __init__(self, function_name='y', var_name='x', equation='x**2',
                 constants=None, set_var_name=None, set_min_val=None,
                 set_max_val=None, no_sets=None, var_unit=None, function_unit=None, set_var_unit=None,
                 explicit_set_values=None):
        """
        Data container for definition of the equation

        Args:
            function_name(str): Name of the "return value" - e.g. y = ...
            var_name(str): Name of the function variable - e.g. x
            equation(str): String representation of an equation (python, numpy code)
            constants(list): List with a dictionary for each constant - see notes
            set_var_name(str): Name of the set parameter
            set_min_val(float): Min. value of the set parameter
            set_max_val(float): Max. value of the set parameter
            no_sets(int): Number of set parameter values to create between min. and max. value
            var_unit(str): Unit for the variable (only used for display)
            function_unit(str): Unit of the function return value (only used for display)
            set_var_unit(str): Unit of set parameter (only used for display)
            explicit_set_values(str): String of explicit values for set parameters (like a list separated with comma)

        Notes:
            * the constants dictionary consists of following keys (all values are strings): "Const. name", "Value",
              "Unit" and "Comment"
        """
        self.function_name = function_name
        self.function_unit = function_unit
        self.var_name = var_name
        self.var_unit = var_unit
        self.equation = equation
        if constants is None:
            self.constants = []
        else:
            self.constants = constants
        self.set_var_name = str(set_var_name)
        self.set_var_unit = str(set_var_unit)
        self.set_min_val = set_min_val
        self.set_max_val = set_max_val
        self.no_sets = no_sets
        self.explicit_set_values = explicit_set_values


class PlotData:

    def __init__(self, start_val=-10.0, end_val=10.0, no_pts=50, x_log=False, y_log=False, swap_xy=False, grid=False,
                 user_data=None, y_min=None, y_max=None, plot_title=None):
        """Data container for plot definition

        Args:
            start_val(float): start of x value range
            end_val(float): end of x value range
            no_pts(int): Number of data points for x value
            x_log(bool): Sets x scale to logarithmic if True
            y_log(bool): Sets y scale to logarithmic if True
            swap_xy(bool): Swaps x and y axis if True
            grid(bool): Enables grid if True
            user_data(list): Not implemented yet
            y_min(float): Min y value for plot display
            y_max(float): Max y value for plot display
            plot_title(str): Manually defined plot title (if None, plot title will be created from formula
                             automatically)

        Notes:

            * All float values will be converted to str and may also be passed as str directly.
        """
        self.start_val = start_val
        self.end_val = end_val
        self.no_pts = no_pts
        self.x_log = x_log
        self.y_log = y_log
        self.swap_xy = swap_xy
        self.grid = grid
        if user_data is None:
            self.user_data = []
        else:
            self.user_data = user_data
        self.y_min = y_min
        self.y_max = y_max
        self.plot_title = plot_title


class DataHandler:

    def __init__(self, formula, plot_data, export_csv=False, filename=None):
        """
        Main class for parser - includes all code generator methods

        Args:
            formula(Formula): Formula container object
            plot_data(PlotData): plot data container object
            export_csv(bool): If true code to export curve values to csv will be embedded
            filename(str): Name of the project file (JSON)
        """
        self.formula = formula
        self.plot_data = plot_data
        self.export_csv = export_csv
        self.filename = filename

    @staticmethod
    def check_valid_input(input_value):
        """Checks if an input value corresponds to a valid value - i.e. not None, "", "None",...

        Returns:
            bool: True if valid input value
        """

        return check_valid_input(input_value)

    def write_py_file(self, filename):
        """
        writes a python file with code generated by combine_code
        """
        with open(filename, "w") as file:
            file.write(self.combine_code())

        print('Python source code exported to '+filename)

    def combine_code(self):
        """Combines output from write_defs, write_plot_code and write_csv_export

        Returns:
            str: combined python code
        """

        code_str = self.write_defs() + self.write_plot_code()

        if self.export_csv:
            code_str += self.write_csv_export()

        return code_str

    def write_defs(self):
        """writes definitions (imports, variables, constants,...)

        Returns:
            str: python code for definitions
        """

        code_str = ""

        code_str += '#!/usr/bin/python3\n'
        code_str += '# this code was automatically generated by simple_plotter\n'

        # imports
        code_str += '\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport csv\n'

        # function definiton
        code_str += '\n\n# formula definintion\ndef f(' + self.formula.var_name
        if self.formula.set_var_name != 'None':
            code_str += ', ' + self.formula.set_var_name
        for constSet in self.formula.constants:
            code_str += ', ' + constSet["Const. name"]
        code_str += '):\n'
        code_str += '    return ' + self.formula.equation + '\n'

        # constants
        code_str += '\n\n# constants\n'
        for constSet in self.formula.constants:
            code_str += "{} = {}  # {}, {}\n".format(constSet["Const. name"], constSet["Value"], constSet["Unit"],
                                                     constSet["Comment"])
        # variables
        code_str += '\n# variable definition\n'
        if self.plot_data.x_log:
            code_str += self.formula.var_name + ' = np.logspace(np.log10(' + str(self.plot_data.start_val) + \
                    '), np.log10(' + str(self.plot_data.end_val) + '), num=' + str(self.plot_data.no_pts) + ')\n'
        else:
            code_str += self.formula.var_name + ' = np.linspace(' + str(self.plot_data.start_val) + ', ' + str(
                self.plot_data.end_val) + ', num=' + str(self.plot_data.no_pts) + ')\n'

        # set constants
        if self.check_valid_input(self.formula.set_var_name):
            code_str += '\n# set constants definition\n'
            if self.check_valid_input(self.formula.explicit_set_values):
                code_str += '{} = [{}]'.format(self.formula.set_var_name, self.formula.explicit_set_values)
            else:
                code_str += '{} = np.linspace({}, {}, num={})'.format(self.formula.set_var_name,
                                                                      str(self.formula.set_min_val),
                                                                      str(self.formula.set_max_val),
                                                                      str(self.formula.no_sets))
            if self.check_valid_input(self.formula.set_var_unit):
                code_str += '  # in ' + str(self.formula.set_var_unit)
            code_str += '\n'

        return code_str

    def write_plot_code(self):
        """writes the plot code

        Returns:
            str: python code for plotting section
        """
        
        code_str = ""

        # plt.plot
        code_str += '\n# plotting setup\n'
        if self.formula.set_var_name != 'None':
            code_str += 'for setConst in ' + self.formula.set_var_name + ':\n   '
        if self.plot_data.swap_xy:
            code_str += 'plt.plot(f(' + self.formula.var_name
        else:
            code_str += 'plt.plot(' + self.formula.var_name + ', f(' + self.formula.var_name
        if self.formula.set_var_name != 'None':
            code_str += ', setConst'
        if len(self.formula.constants) > 0:
            for constSet in self.formula.constants:
                code_str += ', ' + constSet["Const. name"]
        code_str += ')'  # closes f(x,...)
        if self.plot_data.swap_xy:
            code_str += ', ' + self.formula.var_name
        if self.check_valid_input(self.formula.set_var_name):
            code_str += ', label=\'' + self.formula.set_var_name + '=\'+str(setConst)'
            if self.check_valid_input(self.formula.set_var_unit):
                code_str += '+\' ' + self.formula.set_var_unit + '\''
        code_str += ')'  # closes plt.plot(...)

        # labels, tilte. scale, etc.
        if self.check_valid_input(self.formula.var_unit):
            var_name = "{} [{}]".format(self.formula.var_name, self.formula.var_unit)
        else:
            var_name = self.formula.var_name

        if self.check_valid_input(self.formula.function_unit):
            func_name = "{} [{}]".format(self.formula.function_name, self.formula.function_unit)
        else:
            func_name = self.formula.function_name

        if self.plot_data.swap_xy:
            code_str += '\nplt.xlabel(\'' + func_name + '\')'
            code_str += '\nplt.ylabel(\'' + var_name + '\')'
        else:
            code_str += '\nplt.xlabel(\'' + var_name + '\')'
            code_str += '\nplt.ylabel(\'' + func_name + '\')'

        # title
        if self.check_valid_input(self.plot_data.plot_title):
            plot_title = self.plot_data.plot_title
        else:
            plot_title = "{}({}) = {}".format(self.formula.function_name, self.formula.var_name,
                                              self.formula.equation)
        code_str += '\nplt.title(\'{}'.format(plot_title)

        # append constant definitions to plot title
        for constSet in self.formula.constants:
            if self.check_valid_input(constSet["Unit"]):
                const_unit = constSet["Unit"]
            else:
                const_unit = ""
            code_str += (', {} = {} {}'.format(constSet["Const. name"], str(constSet["Value"]), const_unit))
        code_str += '\')'

        if self.plot_data.x_log:
            code_str += '\nplt.xscale(\'log\')'
        if self.plot_data.y_log:
            code_str += '\nplt.yscale(\'log\')'

        # plot axis limits
        code_str += '\nplt.xlim(left={}, right={})'.format(self.plot_data.start_val, self.plot_data.end_val)

        if self.check_valid_input(self.plot_data.y_min):
            code_str += '\nplt.ylim(bottom={})'.format(str(self.plot_data.y_min))
        if self.check_valid_input(self.plot_data.y_max):
            code_str += '\nplt.ylim(top={})'.format(str(self.plot_data.y_max))

        if self.plot_data.grid:
            code_str += '\nplt.grid()'
        code_str += '\nplt.legend()\nplt.show()'
        
        return code_str

    def write_csv_export(self):
        """writes the code to export to filename.csv

        Returns:
            str: python code for export to csv file
        """

        if self.filename in ["", None]:
            filename = "temp"
        else:
            filename = self.filename
        
        code_str = ""

        code_str += '\n\n#csv export code'
        code_str += '\nheader = \'#' + self.formula.var_name + '\''
        if self.check_valid_input(self.formula.set_var_name):
            code_str += '\nfor setConst in ' + self.formula.set_var_name + ':\n    header+=\', ' + \
                        self.formula.set_var_name + '=\'+str(setConst)'
        else:
            code_str += '\nheader+=\', \'' + self.formula.function_name
        code_str += '\ndata = []\ndata.append(' + self.formula.var_name + ')\n'
        if self.check_valid_input(self.formula.set_var_name):
            code_str += 'for setConst in ' + self.formula.set_var_name + ':\n   '
        code_str += 'data.append(f(' + self.formula.var_name
        if self.check_valid_input(self.formula.set_var_name):
            code_str += ', setConst'
        for constSet in self.formula.constants:
            code_str += ', ' + constSet[0] + ')'
        code_str += ')'
        code_str += '\ndata = np.transpose(data)'
        code_str += '\nwith open(\'' + filename + '.csv\', \'w\', newline=\'\') as f:'
        code_str += '\n    code_str += (header+\'\\n\')'
        code_str += '\n    writer = csv.writer(f)'
        code_str += '\n    writer.writerows(data)'

        return code_str

    def check_const_validity(self):
        """Checks the validity of defined constants

        Returns:
            bool: True if all constants are valid, false otherwise

        Note:
            Constants need to have at least a name and a value
        """

        valid = True

        for const_def in self.formula.constants:
            if const_def["Const. name"] in ["", None]:
                valid = False
            if const_def["Value"] in ["", None]:
                valid = False

        return valid

    def plot(self):
        """
        plots the function

        Returns:
            int: Error code:

                * 0: no error
                * 1: invalid constant definition
        """

        # check if constants are defined correctly - need to have at least name and value
        const_valid = self.check_const_validity()

        if const_valid:
            code_str = self.combine_code()
            plt.figure()    # create a new figure for each plot
            exec(code_str)
            error_code = None
        else:
            error_code = 1

        return error_code

    def save_project(self, filename):
        """
        saves project object to JSON file
        """
        if ".json" not in filename:
            filename += ".json"

        with open(filename, 'w') as f:
            f.write(jsonpickle.encode(self))

        print('Project saved to '+filename)

    def load_project(self, filename):
        """
        loads a project from JSON file
        """
        with open(filename, 'r') as f:
            read_data = f.read()

        json_data = json.loads(read_data)

        formula_args = json_data["formula"]
        del formula_args["py/object"]
        plot_args = json_data["plot_data"]
        del plot_args["py/object"]
        self.formula = Formula(**formula_args)
        self.plot_data = PlotData(**plot_args)

        # removed jsonpickle decode to maintain backwards compatibility!

        # JSONimport = jsonpickle.decode(read_data)
        # self.formula = JSONimport.formula
        # self.plotData = JSONimport.plotData
        print('Project loaded from ' + filename)
