# -*- coding: utf-8 -*-

import glob
from inspect import isclass
from os import path
from imp import find_module, load_module
import logging

from openfisca_core.variables import Variable
from openfisca_core.taxbenefitsystems import TaxBenefitSystem
from . import entities


log = logging.getLogger(__name__)


def add_variables_from_file(self, file_path, ignored_variables = None, replaced_variables = None,
        updated_variables = None):
    """
    Adds all OpenFisca variables contained in a given file to the tax and benefit system.
    """
    try:
        file_name = path.splitext(path.basename(file_path))[0]

        #  As Python remembers loaded modules by name, in order to prevent collisions, we need to make sure that:
        #  - Files with the same name, but located in different directories, have a different module names. Hence the file path hash in the module name.
        #  - The same file, loaded by different tax and benefit systems, has distinct module names. Hence the `id(self)` in the module name.
        module_name = '{}_{}_{}'.format(id(self), hash(path.abspath(file_path)), file_name)

        module_directory = path.dirname(file_path)
        try:
            module = load_module(module_name, *find_module(file_name, [module_directory]))
        except NameError as e:
            logging.error(str(e) + ": if this code used to work, this error might be due to a major change in OpenFisca-Core. Checkout the changelog to learn more: <https://github.com/openfisca/openfisca-core/blob/master/CHANGELOG.md>")
            raise
        potential_variables = [getattr(module, item) for item in dir(module) if not item.startswith('__')]
        for pot_variable in potential_variables:
            # We only want to get the module classes defined in this module (not imported)
            if isclass(pot_variable) and issubclass(pot_variable, Variable) and pot_variable.__module__ == module_name:
                if ignored_variables is not None and pot_variable.__name__ in ignored_variables:
                    continue
                elif replaced_variables is not None and pot_variable.__name__ in replaced_variables:
                    self.replace_variable(pot_variable)
                elif updated_variables is not None and pot_variable.__name__ in updated_variables:
                    self.update_variable(pot_variable)
                else:
                    self.add_variable(pot_variable)
    except Exception:
        log.error('Unable to load OpenFisca variables from file "{}"'.format(file_path))
        raise


def add_variables_from_directory(self, directory, ignored_variables = None, replaced_variables = None,
        updated_variables = None):
    """
    Recursively explores a directory, and adds all OpenFisca variables found there to the tax and benefit system.
    """
    py_files = glob.glob(path.join(directory, "*.py"))
    for py_file in py_files:
        self.add_variables_from_file(py_file, ignored_variables, replaced_variables, updated_variables)
    subdirectories = glob.glob(path.join(directory, "*/"))
    for subdirectory in subdirectories:
        self.add_variables_from_directory(subdirectory, ignored_variables, replaced_variables, updated_variables)


TaxBenefitSystem.add_variables_from_directory = add_variables_from_directory
TaxBenefitSystem.add_variables_from_file = add_variables_from_file


COUNTRY_DIR = path.dirname(path.abspath(__file__))


class CountryTaxBenefitSystem(TaxBenefitSystem):

    def __init__(self):
        # We initialize our tax and benefit system with the general constructor
        super(CountryTaxBenefitSystem, self).__init__(entities.entities)

        # We add to our tax and benefit system all the variables
        self.add_variables_from_directory(path.join(COUNTRY_DIR, 'variables'))
        # No parameter file for CEQ so far
        # We add to our tax and benefit system all the legislation parameters defined in the  parameters files
        # param_path = path.join(COUNTRY_DIR, 'parameters')
        # self.load_parameters(param_path)
