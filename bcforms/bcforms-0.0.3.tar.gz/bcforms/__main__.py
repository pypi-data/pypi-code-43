""" bcforms command line interface

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2019-06-25
:Copyright: 2019, Karr Lab
:License: MIT
"""

import cement
import bcforms
import bcforms.core
from wc_utils.util.chem import EmpiricalFormula

class BaseController(cement.Controller):
    """ Base controller for command line application """

    class Meta:
        label = 'base'
        description = "bcforms"
        help = "bcforms"
        arguments = [
            (['-v', '--version'], dict(action='version', version=bcforms.__version__)),
        ]

    @cement.ex(hide=True)
    def _default(self):
        self._parser.print_help()

class ValidateController(cement.Controller):
    """ Validate a biopolymer form
    
    Example::

        bcforms validate 'abc_a + abc_b'
    """

    class Meta:
        label = 'validate'
        description = 'Validate a biocomplex form'
        help = 'Validate a biocomplex form'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['form'], dict(type=str, help='BcForm to validate')),
        ]

    @cement.ex(hide=True)
    def _default(self):
        args = self.app.pargs

        try:
            bc_form = bcforms.core.BcForm().from_str(args.form)
        except Exception as error:
            raise SystemExit('Form is invalid: {}'.format(str(error)))

        errors = bc_form.validate()
        if errors:
            raise SystemExit('Form is invalid:\n  {}'.format('\n  '.join(errors)))


        print('Form is valid')

class GetFormulaController(cement.Controller):
    """ Calculate the chemical formula of a BcForm
    
    Example::

        bcforms get-formula 'abc_a + abc_b' '{abc_a:C5H10O, abc_b:C3H5O}'
    """

    class Meta:
        label = 'get-formula'
        description = 'Calculate the chemical formula of a BcForm'
        help = 'Calculate the chemical formula of a BcForm'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['form'], dict(type=str, help='input BcForm')),
            (['subunit_formulas'], dict(type=str, help='dictionary of subunit formulas')),
        ]

    @cement.ex(hide=True)
    def _default(self):
        args = self.app.pargs

        # validate form
        try:
            bc_form = bcforms.core.BcForm().from_str(args.form)
        except Exception as error:
            raise SystemExit('Form is invalid: {}'.format(str(error)))

        errors = bc_form.validate()
        if errors:
            raise SystemExit('Form is invalid:\n  {}'.format('\n  '.join(errors)))

        # parse formula
        subunit_formulas = {}
        try:
            for subunit in args.subunit_formulas[1:-1].split(','):
                id, formula = subunit.strip().split(':')
                subunit_formulas[id.strip()] = EmpiricalFormula(formula.strip())
        except Exception as error:
            raise SystemExit('Cannot parse subunit_formulas: {}'.format(str(error)))

        # calculate BcForm formula
        try:
            formula = bc_form.get_formula(subunit_formulas)
        except Exception as error:
            raise SystemExit('Unable to calculate BcForm formula: {}'.format(str(error)))

        print(formula)

class GetMolWtController(cement.Controller):
    """ Calculate the molecular weight of a BcForm
    
    Example:

        bcforms get-molwt 'abc_a + abc_b' '{abc_a:86, abc_b:57}'
    """

    class Meta:
        label = 'get-molwt'
        description = 'Calculate the molecular weight of a BcForm'
        help = 'Calculate the molecular weight of a BcForm'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['form'], dict(type=str, help='input BcForm')),
            (['subunit_mol_wts'], dict(type=str, help='dictionary of subunit molecular weights')),
        ]

    @cement.ex(hide=True)
    def _default(self):
        args = self.app.pargs

        # validate form
        try:
            bc_form = bcforms.core.BcForm().from_str(args.form)
        except Exception as error:
            raise SystemExit('Form is invalid: {}'.format(str(error)))

        errors = bc_form.validate()
        if errors:
            raise SystemExit('Form is invalid:\n  {}'.format('\n  '.join(errors)))

        # parse subunit_mol_wts
        subunit_mol_wts = {}
        try:
            for subunit in args.subunit_mol_wts[1:-1].split(','):
                id, mol_wt = subunit.strip().split(':')
                subunit_mol_wts[id.strip()] = float(mol_wt.strip())
        except Exception as error:
            raise SystemExit('Cannot parse subunit_mol_wts: {}'.format(str(error)))

        # calculate BcForm molecular weights
        try:
            mol_wt = bc_form.get_mol_wt(subunit_mol_wts)
        except Exception as error:
            raise SystemExit('Unable to calculate BcForm molecular weights: {}'.format(str(error)))

        print(mol_wt)

class GetChargeController(cement.Controller):
    """ Calculate the total charge of a BcForm
    
    Example::

        bcforms get-charge 'abc_a + abc_b' '{abc_a:+1, abc_b:-1}'
    """

    class Meta:
        label = 'get-charge'
        description = 'Calculate the total charge of a BcForm'
        help = 'Calculate the total charge of a BcForm'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['form'], dict(type=str, help='input BcForm')),
            (['subunit_charges'], dict(type=str, help='dictionary of subunit charge')),
        ]

    @cement.ex(hide=True)
    def _default(self):
        args = self.app.pargs

        # validate form
        try:
            bc_form = bcforms.core.BcForm().from_str(args.form)
        except Exception as error:
            raise SystemExit('Form is invalid: {}'.format(str(error)))

        errors = bc_form.validate()
        if errors:
            raise SystemExit('Form is invalid:\n  {}'.format('\n  '.join(errors)))

        # parse subunit_charges
        subunit_charges = {}
        try:
            for subunit in args.subunit_charges[1:-1].split(','):
                id, charge = subunit.strip().split(':')
                subunit_charges[id.strip()] = int(charge.strip())
        except Exception as error:
            raise SystemExit('Cannot parse subunit_charges: {}'.format(str(error)))

        # calculate BcForm charge
        try:
            charge = bc_form.get_charge(subunit_charges)
        except Exception as error:
            raise SystemExit('Unable to calculate BcForm charges: {}'.format(str(error)))

        print(charge)


class App(cement.App):
    """ Command line application """
    class Meta:
        label = 'bcforms'
        base_controller = 'base'
        handlers = [
            BaseController,
            ValidateController,
            GetFormulaController,
            GetMolWtController,
            GetChargeController,
        ]


def main():
    with App() as app:
        app.run()
