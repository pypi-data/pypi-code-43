""" BcForms

:Author: Mike Zheng <xzheng20@colby.edu>
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2019-06-25
:Copyright: 2019, Karr Lab
:License: MIT
"""

from bpforms import BondOrder, BondStereo
from bpforms.util import gen_genomic_viz
from ruamel import yaml
from wc_utils.util.chem import EmpiricalFormula, OpenBabelUtils, draw_molecule
import abc
import bpforms
import itertools
import lark
import openbabel
import os
import pkg_resources
import wc_utils.cache

# setup cache
cache_dir = os.path.expanduser('~/.cache/bcforms')
if not os.path.isdir(cache_dir):
    os.makedirs(cache_dir)
cache = wc_utils.cache.Cache(directory=cache_dir)


class Subunit(object):
    """ Subunit in a BcForm macromolecular complex

    Attributes:
        id (:obj:`str`): id of the subunit
        stoichiometry (:obj:`int`): stoichiometry of the subunit
        structure (:obj:`bpforms.BpForm` or :obj:`openbabel.OBMol`, optional): structure of the subunit
        formula (:obj:`EmpiricalFormula`, optional): formula of the subunit
        mol_wt (:obj:`float`, optional): molecular weight of the subunit
        charge (:obj:`int`, optional): charge of the subunit
    """

    def __init__(self, id, stoichiometry, structure=None, formula=None, mol_wt=None, charge=None):
        """

        Args:
            id (:obj:`str`): id of the subunit
            stoichiometry (:obj:`int`): stoichiometry of the subunit
            structure (:obj:`bpforms.BpForm` or :obj:`openbabel.OBMol`, optional): structure of the subunit
            formula (:obj:`EmpiricalFormula`, optional): formula of the subunit
            mol_wt (:obj:`float`, optional): molecular weight of the subunit
            charge (:obj:`int`, optional): charge of the subunit
        """
        self.id = id
        self.stoichiometry = stoichiometry
        self.structure = structure
        if structure is None:
            self.formula = formula
            self.charge = charge
            if formula is None:
                self.mol_wt = mol_wt

    @property
    def id(self):
        """ Get the id of the subunit

        Returns:
            :obj:`str`: id of the subunit

        """
        return self._id

    @id.setter
    def id(self, value):
        """ Set the id of the subunit

        Args:
            value (:obj:`str`): id of the subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`str`
        """
        if not isinstance(value, str):
            raise ValueError('`value` must be an instance of `str`')
        self._id = value

    @property
    def stoichiometry(self):
        """ Get the stoichiometry of the subunit

        Returns:
            :obj:`int`: stoichiometry of the subunit

        """
        return self._stoichiometry

    @stoichiometry.setter
    def stoichiometry(self, value):
        """ Set the stoichiometry of the subunit

        Args:
            value (:obj:`int`): stoichiometry of the subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`int`
        """
        if not isinstance(value, int):
            raise ValueError('`value` must be an instance of `int`')
        self._stoichiometry = value

    @property
    def structure(self):
        """ Get the structure of the subunit

        Returns:
            :obj:`bpforms.BpForm` or :obj:`openbabel.OBMol` or None: structure of the subunit

        """
        return self._structure

    @structure.setter
    def structure(self, value):
        """ Set the structure of the subunit

        * setting structure will automaticall set formula, mol_wt, charge

        Args:
            value (:obj:`bpforms.BpForm` or :obj:`openbabel.OBMol` or :obj:`str` (SMILES-encoded string) or None): structure of the subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`bpforms.BpForm` or :obj:`openbabel.OBMol` or None
            :obj:`ValueError`: unable to convert smiles-encoded string to structure
        """
        if not isinstance(value, bpforms.BpForm) and not isinstance(value, openbabel.OBMol) and not isinstance(value, str) and value is not None:
            raise ValueError('`value` must be an instance of `bpforms.BpForm` or `openbabel.OBMol` or None')

        if isinstance(value, str):
            ob_mol = openbabel.OBMol()
            conversion = openbabel.OBConversion()
            conversion.SetInFormat('smi')
            if not conversion.ReadString(ob_mol, value):
                raise ValueError('unable to convert smiles-encoded string to structure')
            self._structure = ob_mol
        else:
            self._structure = value

        if isinstance(self._structure, openbabel.OBMol):
            self._formula = OpenBabelUtils.get_formula(self._structure)
            self._mol_wt = self.formula.get_molecular_weight()
            self._charge = self._structure.GetTotalCharge()
        elif isinstance(self._structure, bpforms.BpForm):
            self._formula = self._structure.get_formula()
            self._mol_wt = self._structure.get_mol_wt()
            self._charge = self._structure.get_charge()

    @property
    def formula(self):
        """ Get the empirical formula of the subunit

        Returns:
            :obj:`EmpiricalFormula` or None: formula of the subunit

        """
        return self._formula

    @formula.setter
    def formula(self, value):
        """ Set the formula of the subunit

        Args:
            value (:obj:`EmpiricalFormula` or :obj:`str` (string representation of the formula) None): formula of the subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`EmpiricalFormula` or None
            :obj:`ValueError`: if formula already set by setting structure attribute
        """
        if not isinstance(value, EmpiricalFormula) and not isinstance(value, str) and value is not None:
            raise ValueError(':obj:`value` is not an instance of :obj:`EmpiricalFormula` or :obj:`str` or None')

        if self.structure is not None:
            raise ValueError('formula already set by setting structure attribute')

        if isinstance(value, str):
            self._formula = EmpiricalFormula(value)
        else:
            self._formula = value

        if isinstance(self._formula, EmpiricalFormula):
            self._mol_wt = self._formula.get_molecular_weight()

    @property
    def mol_wt(self):
        """ Get the molecular weight of the subunit

        Returns:
            :obj:`float` or None: molecular weight of the subunit

        """
        return self._mol_wt

    @mol_wt.setter
    def mol_wt(self, value):
        """ Set the molecular weight of the subunit

        Args:
            value (:obj:`float` or :obj:`int` or :obj:`None`): molecular weight of the subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`float` or :obj:`int` or None
            :obj:`ValueError`: if mol_wt already set by setting structure attribute or formula attribute
            :obj:`ValueError`: if mol_wt is not non-negative
        """
        if not isinstance(value, float) and not isinstance(value, int) and value is not None:
            raise ValueError(':obj:`value` is not an instance of :obj:`float` or :obj:`int` or None')

        if self.formula is not None:
            raise ValueError('mol_wt already set by setting structure attribute or formula attribute')

        if isinstance(value, int):
            value = float(value)

        if isinstance(value, float):
            if value < 0:
                raise ValueError('mol_wt must be non-negative')

        self._mol_wt = value

    @property
    def charge(self):
        """ Get the charge of the subunit

        Returns:
            :obj:`int` or None: charge of the subunit

        """
        return self._charge

    @charge.setter
    def charge(self, value):
        """ Set the charge of the subunit

        Args:
            value (:obj:`int` or :obj:`None`): charge of the subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`int` or None
            :obj:`ValueError`: if charge already set by setting structure attribute
        """
        if not isinstance(value, int) and value is not None:
            raise ValueError(':obj:`value` is not an instance of :obj:`int` or None')

        if self.structure is not None:
            raise ValueError('charge already set by setting structure attribute')

        self._charge = value

    def __str__(self):
        return str(self.stoichiometry) + ' * ' + self.id

    def is_equal(self, other):
        """ Check if two Subunits are semantically equal

        * Check id and stoichiometry; do not check structure yet

        Args:
            other (:obj:`Subunit`): another Subunit

        Returns:
            :obj:`bool`: :obj:`True`, if the Subunits are semantically equal

        """
        if self is other:
            return True
        if self.__class__ != other.__class__:
            return False

        attrs = ['id', 'stoichiometry']

        for attr in attrs:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    def get_formula(self, formula=None):
        """ Get the empirical formula

        Args:
            formula (:obj:`EmpiricalFormula` or :obj:`None`): Subunit empirical formula per copy

        Returns:
            :obj:`EmpiricalFormula` or None: the empirical formula of the Subunit

        """

        if formula is not None:
            self.formula = formula

        if self.formula is not None:
            return self.formula * self.stoichiometry

        return None

    def get_mol_wt(self, mol_wt=None):
        """ Get the molecular weight

        Args:
            mol_wt (:obj:`float` or :obj:`None`): Subunit molecular weight per copy

        Returns:
            :obj:`float` or None: the molecular weight of the Subunit
        """

        if mol_wt is not None:
            self.mol_wt = mol_wt

        if self.mol_wt is not None:
            return self.mol_wt * self.stoichiometry

        return None

    def get_charge(self, charge=None):
        """ Get the total charge

        Args:
            charge (:obj:`int` or :obj:`None`): Subunit charge per copy

        Returns:
            :obj:`int` or None: the total charge of the Subunit
        """

        if charge is not None:
            self.charge = charge

        if self.charge is not None:
            return self.charge * self.stoichiometry

        return None

    def get_structure(self):
        """ Get an Open Babel molecule of the structure

        Returns:
            :obj:`tuple`:
                * :obj:`openbabel.OBMol`: Open Babel molecule of the structure
                * :obj:`dict` of obj:`dict`: dictionary which maps :obj:`subunit_idx` to
                    atom_maps

        Raises:
            :obj:`ValueError`: Subunit structure is :obj:`None`
        """

        if self.structure is None:
            raise ValueError('Structure is None')

        # join the subunits
        mol = openbabel.OBMol()

        subunit_atom_map = {}
        subunit_idx = 1
        for i in range(self.stoichiometry):

            # get structure
            atom_map = {}
            if isinstance(self.structure, openbabel.OBMol):
                structure = self.structure
                atom_map[1] = {}
                atom_map[1]['monomer'] = {}
                for i_atom in range(structure.NumAtoms()):
                    atom_map[1]['monomer'][i_atom+1] = i_atom+1
            else:
                # structure is a BpForm object
                structure, atom_map = self.structure.get_structure()

            num_atoms = structure.NumAtoms()
            total_atoms = sum(sum(len(y) for y in x.values()) for x in atom_map.values())
            # print(num_atoms, total_atoms)

            mol += structure
            for monomer in atom_map.values():
                for atom_type in monomer.values():
                    for i_atom, atom in atom_type.items():
                        atom_type[i_atom] = atom + num_atoms*(subunit_idx-1)

            subunit_atom_map[subunit_idx] = atom_map
            subunit_idx += 1

        return mol, subunit_atom_map

    def export(self, format='smiles', options=[]):
        """ Export the structure to string

        Args:
            format (:obj:`str`, optional): export format
            options (:obj:`list`, optional): export options

        Returns:
            :obj:`str`: exported string representation of the structure

        """
        if self.structure is None:
            return ''

        return OpenBabelUtils.export(self.get_structure()[0], format=format, options=options)


class Atom(object):
    """ Atom in a crosslink

    Attributes:
        subunit (:obj:`str`): id of subunit
        subunit_idx (:obj:`int`): index of the subunit for homomers
        element (:obj:`str`): code of the element
        position (:obj:`int`): SMILES position of the atom within the compound
        monomer (:obj:`int`): index of parent monomer
        charge (:obj:`int`): charge of the atom
        component_type (:obj:`str`): type of component the atom belongs to:
            either 'monomer' or 'backbone'

    """

    def __init__(self, subunit, element, position, monomer, charge=0, subunit_idx=None, component_type=None):
        """

        Args:
            subunit (:obj:`str`): id of subunit
            element (:obj:`str`): code of the element
            position (:obj:`int`): SMILES position of the atom within the compound
            monomer (:obj:`int`): index of parent monomer
            charge (:obj:`int`, optional): charge of the atom
            subunit_idx (:obj:`int`, optional): index of the subunit for homomers
            component_type (:obj:`str`, optional): type of component the atom belongs to:
                either 'monomer' or 'backbone'
        """

        self.subunit = subunit
        self.subunit_idx = subunit_idx
        self.element = element
        self.position = position
        self.monomer = monomer
        self.charge = charge
        if component_type == 'm':
            self.component_type = 'monomer'
        elif component_type == 'b':
            self.component_type = 'backbone'
        elif component_type is None:
            self.component_type = 'monomer'
        else:
            self.component_type = component_type

    @property
    def subunit(self):
        """ Get the subunit that the atom belongs to

        Returns:
            :obj:`str`: subunit

        """
        return self._subunit

    @subunit.setter
    def subunit(self, value):
        """ Set the subunit that the atom belongs to

        Args:
            value (:obj:`str`): subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`str`
        """
        if not isinstance(value, str):
            raise ValueError('`value` must be an instance of `str`')
        self._subunit = value

    @property
    def subunit_idx(self):
        """ Get the index of the homomer of the subunit that the atom belongs to

        Returns:
            :obj:`int`: subunit_idx or None

        """
        return self._subunit_idx

    @subunit_idx.setter
    def subunit_idx(self, value):
        """ Set the index of the homomer of the subunit that the atom belongs to

        Args:
            value (:obj:`int`): subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not None or a positive integer
        """
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError('`value` must be a None or a positive integer')
        self._subunit_idx = value

    @property
    def element(self):
        """ Get the element of the atom

        Returns:
            :obj:`str`: element

        """
        return self._element

    @element.setter
    def element(self, value):
        """ Set the element of the atom

        Args:
            value (:obj:`str`): element

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`str`
        """
        if not isinstance(value, str):
            raise ValueError('`value` must be an instance of `str`')
        self._element = value

    @property
    def position(self):
        """ Get the position of the atom in the compound

        Returns:
            :obj:`int`: position

        """
        return self._position

    @position.setter
    def position(self, value):
        """ Set the position of the atom in the compound

        Args:
            value (:obj:`int`): position

        Raises:
            :obj:`ValueError`: if :obj:`value` is not a positive :obj:`int`
        """
        if not isinstance(value, int) or value < 1:
            raise ValueError('`value` must be a positive integer')
        self._position = value

    @property
    def monomer(self):
        """ Get the position in the subunit of the monomer that the atom belongs to

        Returns:
            :obj:`int`: monomer position

        """
        return self._monomer

    @monomer.setter
    def monomer(self, value):
        """ Set the position in the subunit of the monomer that the atom belongs to

        Args:
            value (:obj:`int`): monomer position

        Raises:
            :obj:`ValueError`: if `value` is not a positive integer
        """
        if not isinstance(value, int) or value < 1:
            raise ValueError('`value` must be a positive integer')
        self._monomer = value

    @property
    def charge(self):
        """ Get the charge of the atom

        Returns:
            :obj:`int`: charge

        """
        return self._charge

    @charge.setter
    def charge(self, value):
        """ Set the charge of the atom

        Args:
            value (:obj:`int`): charge

        Raises:
            :obj:`ValueError`: if `value` is not an integer
        """
        if not isinstance(value, int):
            raise ValueError('`value` must be an integer')
        self._charge = value

    @property
    def component_type(self):
        """ Get the type of component the atom belongs to

        Returns:
            :obj:`str`: component type

        """
        return self._component_type

    @component_type.setter
    def component_type(self, value):
        """ Set the type of component the atom belongs to

        Raises:
            :obj:`ValueError`: component_type must be either 'monomer' or 'backbone'

        """
        if value not in ['monomer', 'backbone']:
            raise ValueError('`component_type` must be either "monomer" or "backbone"')
        else:
            self._component_type = value

    def __str__(self):
        """ Generate a string representation

        Returns:
            :obj:`str`: string representation
        """

        if self.charge == 0:
            charge = ''
        else:
            charge = '{:+d}'.format(self.charge)

        if self.subunit_idx is None:
            subunit_idx = ''
        else:
            subunit_idx = '(' + str(self.subunit_idx) + ')'
        return '{}{}-{}{}{}{}'.format(self.subunit, subunit_idx, self.monomer, self.element, self.position, charge)

    def is_equal(self, other):
        """ Check if two atoms are semantically equal (belong to the same subunit/monomer and
        have the same element, position, and charge)

        Args:
            other (:obj:`Atom`): another atom

        Returns:
            :obj:`bool`: :obj:`True`, if the atoms are semantically equal

        """
        if self is other:
            return True
        if self.__class__ != other.__class__:
            return False

        attrs = ['subunit', 'element', 'position', 'monomer', 'charge']

        for attr in attrs:
            if getattr(self, attr) != getattr(other, attr):
                return False

        self_subunit_idx = self.subunit_idx if self.subunit_idx is not None else 1
        other_subunit_idx = other.subunit_idx if other.subunit_idx is not None else 1
        if self_subunit_idx != other_subunit_idx:
            return False

        return True


class Crosslink(abc.ABC):
    """ Abstract class of a crosslink between subunits

    """

    @abc.abstractmethod
    def get_l_bond_atoms(self):
        """ Get the left bond atoms

        Returns:
            :obj:`list` of :obj:`Atom`: left bond atoms

        """
        pass

    @abc.abstractmethod
    def get_r_bond_atoms(self):
        """ Get the right bond atoms

        Returns:
            :obj:`list` of :obj:`Atom`: right bond atoms

        """
        pass

    @abc.abstractmethod
    def get_l_displaced_atoms(self):
        """ Get the left displaced atoms

        Returns:
            :obj:`list` of :obj:`Atom`: left displaced atoms

        """
        pass

    @abc.abstractmethod
    def get_r_displaced_atoms(self):
        """ Get the right displaced atoms

        Returns:
            :obj:`list` of :obj:`Atom`: right displaced atoms

        """
        pass

    @abc.abstractmethod
    def get_order(self):
        """ Get the order

        Returns:
            :obj:`BondOrder`: order

        """
        pass

    @abc.abstractmethod
    def get_stereo(self):
        """ Get the stereochemistry

        Returns:
            :obj:`BondStereo`: stereochemistry

        """
        pass

    @abc.abstractmethod
    def __str__(self):
        """Generate a string representation

        Returns:
            :obj:`str`: string representation
        """
        pass

    def is_equal(self, other):
        """ Check if two crosslinks are semantically equal (have the same bond atoms)

        Args:
            other (:obj:`Crosslink`): another crosslink

        Returns:
            :obj:`bool`: :obj:`True`, if the crosslinks are semantically equal

        """

        if self is other:
            return True
        if self.__class__ != other.__class__ and self.__class__.__bases__ != other.__class__.__bases__:
            return False

        attrs = ['l_bond_atoms', 'l_displaced_atoms', 'r_bond_atoms', 'r_displaced_atoms']

        for attr in attrs:
            self_atoms = getattr(self, 'get_'+attr)()
            other_atoms = getattr(other, 'get_'+attr)()
            if len(self_atoms) != len(other_atoms):
                return False
            for self_atom, other_atom in zip(self_atoms, other_atoms):
                if not self_atom.is_equal(other_atom):
                    return False

        if self.get_order() != other.get_order() or self.get_stereo() != other.get_stereo():
            return False

        return True


class InlineCrosslink(Crosslink):
    """ A crosslink between subunits defined inline

    Attributes:
        l_bond_atoms (:obj:`list` of :obj:`Atom`): atoms from the left subunit that bond with the right subunit
        r_bond_atoms (:obj:`list` of :obj:`Atom`): atoms from the right subunit that bond with the left subunit
        l_displaced_atoms (:obj:`list` of :obj:`Atom`): atoms from the left subunit displaced by the crosslink
        r_displaced_atoms (:obj:`list` of :obj:`Atom`): atoms from the right subunit displaced by the crosslink
        order (:obj:`BondOrder`): order
        stereo (:obj:`BondStereo`): stereochemistry
        comments (:obj:`str`): comments
    """

    def __init__(self, l_bond_atoms=None, r_bond_atoms=None, l_displaced_atoms=None, r_displaced_atoms=None,
                 order=BondOrder.single, stereo=None,
                 comments=None):
        """

        Args:
            l_bond_atoms (:obj:`list`): atoms from the left subunit that bond with the right subunit
            r_bond_atoms (:obj:`list`): atoms from the right subunit that bond with the left subunit
            l_displaced_atoms (:obj:`list`): atoms from the left subunit displaced by the crosslink
            r_displaced_atoms (:obj:`list`): atoms from the right subunit displaced by the crosslink
            order (:obj:`BondOrder`, optional): order
            stereo (:obj:`BondStereo`, optional): stereochemistry
            comments (:obj:`str`): comments
        """
        if l_bond_atoms is None:
            self.l_bond_atoms = []
        else:
            self.l_bond_atoms = l_bond_atoms

        if r_bond_atoms is None:
            self.r_bond_atoms = []
        else:
            self.r_bond_atoms = r_bond_atoms

        if l_displaced_atoms is None:
            self.l_displaced_atoms = []
        else:
            self.l_displaced_atoms = l_displaced_atoms

        if r_bond_atoms is None:
            self.r_displaced_atoms = []
        else:
            self.r_displaced_atoms = r_bond_atoms

        self.order = order
        self.stereo = stereo

        self.comments = comments

    @property
    def l_bond_atoms(self):
        """ Get the left bond atoms

        Returns:
            :obj:`list` of :obj:`Atom`: left bond atoms

        """
        return self._l_bond_atoms

    @l_bond_atoms.setter
    def l_bond_atoms(self, value):
        """ Set the left bond atoms

        Args:
            value (:obj:`list` of :obj:`Atom`): left bond atoms

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`list`

        """
        if not isinstance(value, list):
            raise ValueError('`value` must be an instance of `list`')
        self._l_bond_atoms = value

    @property
    def r_bond_atoms(self):
        """ Get the right bond atoms

        Returns:
            :obj:`list` of :obj:`Atom`: right bond atoms

        """
        return self._r_bond_atoms

    @r_bond_atoms.setter
    def r_bond_atoms(self, value):
        """ Set the right bond atoms

        Args:
            value (:obj:`list` of :obj:`Atom`): right bond atoms

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`list`

        """
        if not isinstance(value, list):
            raise ValueError('`value` must be an instance of `list`')
        self._r_bond_atoms = value

    @property
    def l_displaced_atoms(self):
        """ Get the left displaced atoms

        Returns:
            :obj:`list` of :obj:`Atom`: left displaced atoms

        """
        return self._l_displaced_atoms

    @l_displaced_atoms.setter
    def l_displaced_atoms(self, value):
        """ Set the left displaced atoms

        Args:
            value (:obj:`list` of :obj:`Atom`): left displaced atoms

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`list`

        """
        if not isinstance(value, list):
            raise ValueError('`value` must be an instance of `list`')
        self._l_displaced_atoms = value

    @property
    def r_displaced_atoms(self):
        """ Get the right displaced atoms

        Returns:
            :obj:`list` of :obj:`Atom`: right displaced atoms

        """
        return self._r_displaced_atoms

    @r_displaced_atoms.setter
    def r_displaced_atoms(self, value):
        """ Set the right displaced atoms

        Args:
            value (:obj:`list` of :obj:`Atom`): right displaced atoms

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`list`

        """
        if not isinstance(value, list):
            raise ValueError('`value` must be an instance of `list`')
        self._r_displaced_atoms = value

    @property
    def order(self):
        """ Get the order

        Returns:
            :obj:`BondOrder`: order
        """
        return self._order

    @order.setter
    def order(self, value):
        """ Set the order

        Args:
            value (:obj:`BondOrder`): order

        Raises:
            :obj:`ValueError`: if `order` is not an instance of `BondOrder`
        """
        if not isinstance(value, BondOrder):
            raise ValueError('`order` must be an instance of `BondOrder`')
        self._order = value

    @property
    def stereo(self):
        """ Get the stereochemistry

        Returns:
            :obj:`BondStereo`: stereochemistry
        """
        return self._stereo

    @stereo.setter
    def stereo(self, value):
        """ Set the stereo

        Args:
            value (:obj:`BondStereo`): stereochemistry

        Raises:
            :obj:`ValueError`: if `stereo` is not an instance of `BondStereo`
        """
        if value is not None and not isinstance(value, BondStereo):
            raise ValueError('`stereo` must be an instance of `BondStereo` or `None`')
        self._stereo = value

    @property
    def comments(self):
        """ Get comments

        Returns:
            :obj:`str`: comments
        """
        return self._comments

    @comments.setter
    def comments(self, value):
        """ Set comments

        Args:
            value (:obj:`str`): comments

        Raises:
            :obj:`ValueError`: if value is not a str or None
        """
        if value and not isinstance(value, str):
            raise ValueError('`comments` must be a string or None')
        self._comments = value

    def __str__(self):
        """Generate a string representation

        Returns:
            :obj:`str`: string representation
        """
        s = 'x-link: ['

        atom_types = ['l_bond_atoms', 'l_displaced_atoms', 'r_bond_atoms', 'r_displaced_atoms']
        for atom_type in atom_types:
            for atom in getattr(self, atom_type):
                s += ' {}: {} |'.format(atom_type[:-1].replace('_', '-'), str(atom))

        if self.order != BondOrder.single:
            s += ' order: "{}" |'.format(self.order.name)
        if self.stereo is not None:
            s += ' stereo: "{}" |'.format(self.stereo.name)

        if self.comments:
            s += ' comments: "{}" |'.format(self.comments.replace('"', '\\"'))

        s = s[:-1] + ']'
        return s

    def get_l_bond_atoms(self):
        """ Get the left bond atoms

        Returns:
            :obj:`list` of :obj:`Atom`: left bond atoms

        """
        return self.l_bond_atoms

    def get_r_bond_atoms(self):
        """ Get the right bond atoms

        Returns:
            :obj:`list` of :obj:`Atom`: right bond atoms

        """
        return self.r_bond_atoms

    def get_l_displaced_atoms(self):
        """ Get the left displaced atoms

        Returns:
            :obj:`list` of :obj:`Atom`: left displaced atoms

        """
        return self.l_displaced_atoms

    def get_r_displaced_atoms(self):
        """ Get the right displaced atoms

        Returns:
            :obj:`list` of :obj:`Atom`: right displaced atoms

        """
        return self.r_displaced_atoms

    def get_order(self):
        """ Get the order

        Returns:
            :obj:`BondOrder`: order
        """
        return self.order

    def get_stereo(self):
        """ Get the stereochemistry

        Returns:
            :obj:`BondStereo`: stereochemistry
        """
        return self.stereo


_xlink_filename = pkg_resources.resource_filename('bpforms', 'xlink/xlink.yml')


@cache.memoize(typed=False, expire=30 * 24 * 60 * 60, filename_args=[0])
def parse_yaml(path):
    """ Read a YAML file

    Args:
        path (:obj:`str`): path to YAML file which defines alphabet

    Returns:
        :obj:`object`: content of file
    """
    yaml_reader = yaml.YAML()
    with open(path, 'rb') as file:
        return yaml_reader.load(file)


class OntologyCrosslink(Crosslink):
    """ A pre-defined crosslink between subunits

    Attributes:
        type (:obj:`str`): type of the pre-defined crosslink
        l_subunit (:obj:`str`): name of the left subunit
        l_subunit_idx (:obj:`int`, optional): index of the left subunit, optional if only one copy of the subunit
        l_monomer (:obj:`int`): index of the monomer from the left subunit
        r_subunit (:obj:`str`): name of the left subunit
        r_subunit_idx (:obj:`int`, optional): index of the left subunit, optional if only one copy of the subunit
        r_monomer (:obj:`int`): index of the monomer from the right subunit
        xlink_details (:obj:`tuple`): detailed information about the abstracted crosslink

        _xlink_atom_parser (:obj:`lark.Lark`): lark grammar parser used to parse atom strings

    """

    def __init__(self, type, l_subunit, l_monomer, r_subunit, r_monomer, l_subunit_idx=None, r_subunit_idx=None):
        """

        Args:
            type (:obj:`str`): type of the pre-defined crosslink
            l_subunit (:obj:`str`): name of the left subunit
            l_subunit_idx (:obj:`int`, optional): index of the left subunit, optional if only one copy of the subunit
            l_monomer (:obj:`int`): index of the monomer from the left subunit
            r_subunit (:obj:`str`): name of the left subunit
            r_subunit_idx (:obj:`int`, optional): index of the left subunit, optional if only one copy of the subunit
            r_monomer (:obj:`int`): index of the monomer from the right subunit

        """

        self.type = type
        self.l_subunit = l_subunit
        self.l_subunit_idx = l_subunit_idx
        self.l_monomer = l_monomer
        self.r_subunit = r_subunit
        self.r_subunit_idx = r_subunit_idx
        self.r_monomer = r_monomer
        self.xlink_details = self.get_details()

    @property
    def type(self):
        """ Get the type of the abstracted crosslink

        Returns:
            :obj:`str`: type of the crosslink

        """
        return self._type

    @type.setter
    def type(self, value):
        """ Set the type of the abstracted crosslink

        Args:
            value (:obj:`str`): type of the crosslink

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`str`

        """
        if not isinstance(value, str):
            raise ValueError('`value` must be an instance of `str`')
        self._type = value

    @property
    def l_subunit(self):
        """ Get the name of the left subunit in the crosslink

        Returns:
            :obj:`str`: name of the left subunit

        """
        return self._l_subunit

    @l_subunit.setter
    def l_subunit(self, value):
        """ Set the name of the left subunit in the crosslink

        Args:
            value (:obj:`str`): name of the left subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`str`

        """
        if not isinstance(value, str):
            raise ValueError('`value` must be an instance of `str`')
        self._l_subunit = value

    @property
    def l_subunit_idx(self):
        """ Get the index of the left subunit in the crosslink

        Returns:
            :obj:`int`: index of the left subunit

        """
        return self._l_subunit_idx

    @l_subunit_idx.setter
    def l_subunit_idx(self, value):
        """ Set the index of the left subunit in the crosslink

        Args:
            value (:obj:`int` or None): index of the left subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`int` or None

        """
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError('`value` must be an instance of `int` or None')
        self._l_subunit_idx = value

    @property
    def l_monomer(self):
        """ Get the index of the left monomer in the crosslink

        Returns:
            :obj:`int`: index of the left monomer

        """
        return self._l_monomer

    @l_monomer.setter
    def l_monomer(self, value):
        """ Set the index of the left monomer in the crosslink

        Args:
            value (:obj:`int`): index of the left monomer

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`int`

        """
        if not isinstance(value, int):
            raise ValueError('`value` must be an instance of `int`')
        self._l_monomer = value

    @property
    def r_subunit(self):
        """ Get the name of the right subunit in the crosslink

        Returns:
            :obj:`str`: name of the right subunit

        """
        return self._r_subunit

    @r_subunit.setter
    def r_subunit(self, value):
        """ Set the name of the right subunit in the crosslink

        Args:
            value (:obj:`str`): name of the right subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`str`

        """
        if not isinstance(value, str):
            raise ValueError('`value` must be an instance of `str`')
        self._r_subunit = value

    @property
    def r_subunit_idx(self):
        """ Get the index of the right subunit in the crosslink

        Returns:
            :obj:`int`: index of the right subunit

        """
        return self._r_subunit_idx

    @r_subunit_idx.setter
    def r_subunit_idx(self, value):
        """ Set the index of the right subunit in the crosslink

        Args:
            value (:obj:`int` or None): index of the right subunit

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`int` or None

        """
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError('`value` must be an instance of `int` or None')
        self._r_subunit_idx = value

    @property
    def r_monomer(self):
        """ Get the index of the right monomer in the crosslink

        Returns:
            :obj:`int`: index of the right monomer

        """
        return self._r_monomer

    @r_monomer.setter
    def r_monomer(self, value):
        """ Set the index of the right monomer in the crosslink

        Args:
            value (:obj:`int`): index of the right monomer

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`int`

        """
        if not isinstance(value, int):
            raise ValueError('`value` must be an instance of `int`')
        self._r_monomer = value

    _xlink_atom_parser = lark.Lark("""
        start: atom_element atom_position atom_charge?
        atom_element: /[A-Z][a-z]?/
        atom_position: /[0-9]+/
        atom_charge: /[\+\-][0-9]+/
    """)

    class ParseTreeTransformer(lark.Transformer):
        # Class that processes the parsetree

        @lark.v_args(inline=True)
        def start(self, *args):
            atom_element = args[0][1]
            atom_position = args[1][1]
            if len(args) > 2:
                atom_charge = args[2][1]
            else:
                atom_charge = 0
            return atom_element, atom_position, atom_charge

        @lark.v_args(inline=True)
        def atom_element(self, *args):
            return ('atom_element', args[0].value)

        @lark.v_args(inline=True)
        def atom_position(self, *args):
            return ('atom_position', int(args[0].value))

        @lark.v_args(inline=True)
        def atom_charge(self, *args):
            return ('atom_charge', int(args[0].value))

    def get_l_bond_atoms(self):
        """ Get the left bond atoms

        Returns:
            :obj:`list` of :obj:`Atom`: left bond atoms

        """
        atoms = []
        for atom in self.xlink_details[1]['l_bond_atoms']:
            tree = self._xlink_atom_parser.parse(atom)
            parse_tree_transformer = self.ParseTreeTransformer()
            element, position, charge = parse_tree_transformer.transform(tree)
            atom = Atom(subunit=self.l_subunit, element=element, position=position,
                        monomer=self.l_monomer, charge=charge, subunit_idx=self.l_subunit_idx)
            atoms.append(atom)
        return atoms

    def get_r_bond_atoms(self):
        """ Get the right bond atoms

        Returns:
            :obj:`list` of :obj:`Atom`: right bond atoms

        """
        atoms = []
        for atom in self.xlink_details[1]['r_bond_atoms']:
            tree = self._xlink_atom_parser.parse(atom)
            parse_tree_transformer = self.ParseTreeTransformer()
            element, position, charge = parse_tree_transformer.transform(tree)
            atom = Atom(subunit=self.r_subunit, element=element, position=position,
                        monomer=self.r_monomer, charge=charge, subunit_idx=self.r_subunit_idx)
            atoms.append(atom)
        return atoms

    def get_l_displaced_atoms(self):
        """ Get the left displaced atoms

        Returns:
            :obj:`list` of :obj:`Atom`: left displaced atoms

        """
        atoms = []
        for atom in self.xlink_details[1]['l_displaced_atoms']:
            tree = self._xlink_atom_parser.parse(atom)
            parse_tree_transformer = self.ParseTreeTransformer()
            element, position, charge = parse_tree_transformer.transform(tree)
            atom = Atom(subunit=self.l_subunit, element=element, position=position,
                        monomer=self.l_monomer, charge=charge, subunit_idx=self.l_subunit_idx)
            atoms.append(atom)
        return atoms

    def get_r_displaced_atoms(self):
        """ Get the right displaced atoms

        Returns:
            :obj:`list` of :obj:`Atom`: right displaced atoms

        """
        atoms = []
        for atom in self.xlink_details[1]['r_displaced_atoms']:
            tree = self._xlink_atom_parser.parse(atom)
            parse_tree_transformer = self.ParseTreeTransformer()
            element, position, charge = parse_tree_transformer.transform(tree)
            atom = Atom(subunit=self.r_subunit, element=element, position=position,
                        monomer=self.r_monomer, charge=charge, subunit_idx=self.r_subunit_idx)
            atoms.append(atom)
        return atoms

    def get_order(self):
        """ Get the order

        Returns:
            :obj:`BondOrder`: order
        """
        return BondOrder[self.xlink_details[1].get('order' , 'single')]

    def get_stereo(self):
        """ Get the stereochemistry

        Returns:
            :obj:`BondStereo`: stereochemistry
        """
        val = self.xlink_details[1].get('stereo', None)
        if val is None:
            return None
        else:
            return BondStereo[val]

    def __str__(self):
        """Generate a string representation

        Returns:
            :obj:`str`: string representation
        """
        s = 'x-link: [ type: {} |'.format(self.type)

        if self.l_subunit_idx is None:
            str_l_subunit_idx = ''
        else:
            str_l_subunit_idx = '({})'.format(self.l_subunit_idx)
        s += ' l: {}{}-{} |'.format(self.l_subunit, str_l_subunit_idx, self.l_monomer)

        if self.r_subunit_idx is None:
            str_r_subunit_idx = ''
        else:
            str_r_subunit_idx = '({})'.format(self.r_subunit_idx)
        s += ' r: {}{}-{} |'.format(self.r_subunit, str_r_subunit_idx, self.r_monomer)

        s = s[:-1]+']'
        return s

    def get_details(self):
        """ Get the full details of the crosslink in a dictionary

        Returns:
            :obj:`dict`: detailed information of the crosslink

        Raises:
            :obj:`KeyError`: Unknown abstracted crosslink type

        """
        xlink_detail_dict = parse_yaml(_xlink_filename)
        for xlink_name, xlink_details in xlink_detail_dict.items():
            if self.type == xlink_name:
                return (xlink_name, xlink_details)
            if self.type in xlink_details['synonyms']:
                return (xlink_name, xlink_details)
            if 'name' in xlink_details and self.type == xlink_details['name']:
                return (xlink_name, xlink_details)

        raise KeyError('Unknown abstracted crosslink type')


class BcForm(object):
    """ A form of a macromolecular complex

    Attributes:
        subunits (:obj:`list` of :obj:`Subunit`): subunit composition of the complex
        crosslinks (:obj:`list` :obj:`Crosslink`): crosslinks in the complex

    """

    def __init__(self, subunits=None, crosslinks=None):
        """

        Args:
            subunits (:obj:`list` of :obj:`Subunit` or :obj:`BcForm`, optional): subunit composition of the complex
            crosslinks (:obj:`list` of :obj:`Crosslink`, optional): crosslinks in the complex

            _parser (:obj:`lark.Lark`): lark grammar parser used in `from_str`
        """
        if subunits is None:
            self.subunits = []
        else:
            self.subunits = subunits

        if crosslinks is None:
            self.crosslinks = []
        else:
            self.crosslinks = crosslinks

    @property
    def subunits(self):
        """ Get the subunits

        Returns:
            :obj:`list` of :obj:`Subunit` or :obj:`BcForm`: subunits

        """
        return self._subunits

    @subunits.setter
    def subunits(self, value):
        """ Set the subunits

        Args:
            value (:obj:`list` of :obj:`Subunit` or :obj`BcForm`): subunits

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`list`

        """
        if not isinstance(value, list):
            raise ValueError('`value` must be an instance of `list`')
        self._subunits = value

    @property
    def crosslinks(self):
        """ Get the crosslinks

        Returns:
            :obj:`list` of :obj:`Crosslink`: crosslinks

        """
        return self._crosslinks

    @crosslinks.setter
    def crosslinks(self, value):
        """ Set the crosslinks

        Args:
            value (:obj:`list` of :obj:`Crosslink`): crosslinks

        Raises:
            :obj:`ValueError`: if :obj:`value` is not an instance of :obj:`list`

        """
        if not isinstance(value, list):
            raise ValueError('`value` must be an instance of `list`')
        self._crosslinks = value

    def __str__(self):
        """ Generate a string representation

        Returns:
            :obj:`str`: string representation of complex
        """
        s = ''

        # subunits
        for subunit in self.subunits:
            s += str(subunit) + ' + '
        s = s[:-3]

        # crosslinks
        for crosslink in self.crosslinks:
            s += ' | ' + str(crosslink)

        # return string representation
        return s

    # read the grammar file
    _grammar_filename = pkg_resources.resource_filename('bcforms', 'grammar.lark')

    with open(_grammar_filename, 'r') as file:
        _parser = lark.Lark(file.read())

    def from_str(self, string):
        """ Set a complex from a string representation

        Args:
            string (:obj:`str`): string representation of a complex

        Returns:
            :obj:`BcForm`: structured BcForm representation of the string
        """

        class ParseTreeTransformer(lark.Transformer):
            # Class that processes the parsetree

            def __init__(self, bc_form):
                super(ParseTreeTransformer, self).__init__()
                self.bc_form = bc_form

            @lark.v_args(inline=True)
            def start(self, *args):
                self.bc_form.subunits = args[0]
                self.bc_form.crosslinks = []
                if len(args) > 2:
                    # exists global attr (crosslink)
                    self.bc_form.crosslinks = list(args[2::2])
                return self.bc_form

            # complex
            @lark.v_args(inline=True)
            def complex(self, *args):
                return [Subunit(id=x['id'], stoichiometry=x['stoichiometry']) for x in args if type(x) == dict]

            @lark.v_args(inline=True)
            def component(self, *args):
                component_dict = {}
                if len(args) < 2:
                    # handle the case where no explicit coefficient
                    component_dict['stoichiometry'] = 1
                    component_dict[args[0][0]] = args[0][1]
                else:
                    # handle the case where optional coefficient is explicitly put
                    component_dict[args[0][0]] = args[0][1]
                    component_dict[args[1][0]] = args[1][1]

                return component_dict

            @lark.v_args(inline=True)
            def coefficient(self, *args):
                return ('stoichiometry', int(args[0].value))

            @lark.v_args(inline=True)
            def subunit(self, *args):
                return ('id', args[0].value)

            # crosslinks
            @lark.v_args(inline=True)
            def global_attr(self, *args):
                return args[0]

            @lark.v_args(inline=True)
            def crosslink(self, *args):
                for arg in args:
                    if isinstance(arg, Crosslink):
                        return arg

            # ontology-defined crosslink
            @lark.v_args(inline=True)
            def onto_crosslink(self, *args):
                for arg in args:
                    if isinstance(arg, lark.tree.Tree):
                        attr = arg.children[0][0]
                        val = arg.children[0][1]
                        if attr == 'type':
                            type = val
                        elif attr == 'l_monomer':
                            l_subunit = val[0]
                            l_subunit_idx = val[1]
                            l_monomer = val[2]
                        elif attr == 'r_monomer':
                            r_subunit = val[0]
                            r_subunit_idx = val[1]
                            r_monomer = val[2]
                bond = OntologyCrosslink(type=type,
                                         l_subunit=l_subunit, l_subunit_idx=l_subunit_idx, l_monomer=l_monomer,
                                         r_subunit=r_subunit, r_subunit_idx=r_subunit_idx, r_monomer=r_monomer)
                return bond

            @lark.v_args(inline=True)
            def onto_crosslink_type(self, *args):
                return ('type', args[1].value)

            @lark.v_args(inline=True)
            def onto_crosslink_monomer(self, *args):
                num_optional_args = 0
                monomer_type = args[0][1]
                subunit = args[2][1]
                if args[3][0] == 'subunit_idx':
                    subunit_idx = int(args[3][1])
                else:
                    subunit_idx = None
                    num_optional_args += 1
                monomer = int(args[4 - num_optional_args][1])
                return (monomer_type, (subunit, subunit_idx, monomer))

            @lark.v_args(inline=True)
            def onto_crosslink_monomer_type(self, *args):
                return ('onto_crosslink_monomer_type', args[0] + '_monomer')

            # inline crosslink
            @lark.v_args(inline=True)
            def inline_crosslink(self, *args):
                bond = InlineCrosslink()
                for arg in args:
                    if isinstance(arg, lark.tree.Tree):
                        attr, val = arg.children[0]
                        if attr in ['order', 'stereo', 'comments']:
                            setattr(bond, attr, val)
                        else:
                            attr_val_list = getattr(bond, attr + "s")
                            attr_val_list.append(val)
                return bond

            @lark.v_args(inline=True)
            def inline_crosslink_atom(self, *args):
                num_optional_args = 0
                atom_type = args[0][1]
                subunit = args[2][1]
                if args[3][0] == 'subunit_idx':
                    subunit_idx = int(args[3][1])
                else:
                    subunit_idx = None
                    num_optional_args += 1
                monomer = int(args[4-num_optional_args][1])
                element = args[5-num_optional_args][1]
                position = int(args[6-num_optional_args][1])
                if len(args) > 7-num_optional_args:
                    if args[7-num_optional_args][0] == 'atom_component_type':
                        atom_component_type = args[7-num_optional_args][1]
                    else:
                        atom_component_type = None
                        num_optional_args += 1
                else:
                    atom_component_type = None
                if len(args) > 8-num_optional_args:
                    if args[8-num_optional_args][0] == 'atom_charge':
                        charge = int(args[8-num_optional_args][1])
                    else:
                        charge = 0
                else:
                    charge = 0

                return (atom_type, Atom(subunit=subunit, subunit_idx=subunit_idx, element=element,
                                        position=position, monomer=monomer, charge=charge, component_type=atom_component_type))

            @lark.v_args(inline=True)
            def inline_crosslink_atom_type(self, *args):
                return ('inline_crosslink_atom_type', args[0].value + '_' + args[1].value + '_atom')

            @lark.v_args(inline=True)
            def inline_crosslink_order(self, *args):
                return ('order', BondOrder[args[-2].value])

            @lark.v_args(inline=True)
            def inline_crosslink_stereo(self, *args):
                return ('stereo', BondStereo[args[-2].value])

            @lark.v_args(inline=True)
            def inline_crosslink_comments(self, *args):
                return ('comments', args[1].value[1:-1])

            @lark.v_args(inline=True)
            def monomer_position(self, *args):
                return ('monomer_position', int(args[0].value))

            @lark.v_args(inline=True)
            def subunit_idx(self, *args):
                return ('subunit_idx', int(args[0].value[1:-1]))

            @lark.v_args(inline=True)
            def atom_element(self, *args):
                return ('atom_element', args[0].value)

            @lark.v_args(inline=True)
            def atom_position(self, *args):
                return ('atom_position', int(args[0].value))

            @lark.v_args(inline=True)
            def atom_charge(self, *args):
                return ('atom_charge', args[0].value)

            @lark.v_args(inline=True)
            def atom_component_type(self, *args):
                return ('atom_component_type', args[0].value)

        tree = self._parser.parse(string)
        # print(tree.pretty())
        parse_tree_transformer = ParseTreeTransformer(self)
        bc_form = parse_tree_transformer.transform(tree)
        bc_form.clean()
        return bc_form

    def from_set(self, subunits):
        """ Set the subunits from a list of subunits

        Note: this method does not support crosslinks

        Args:
            subunits: (:obj:`list`): list representation of a complex. For example::

                [
                    {'id': 'ABC_A', 'stoichiometry': 2},
                    {'id': 'ABC_B', 'stoichiometry': 3},
                ]

        Returns:
            :obj:`BcForm`: this complex

        Raises:
            :obj:`ValueError`: subunit has no 'id' key
            :obj:`ValueError`: subunit has no 'stoichiometry' key
        """
        self.subunits = []
        self.crosslinks = []

        for subunit in subunits:
            new_subunit = {}

            # process id of subunit
            if 'id' in subunit:
                new_subunit['id'] = subunit['id']
            else:
                raise ValueError('`subunit` has no `id`')

            # process stoichiometry of subunit
            if 'stoichiometry' in subunit:
                new_subunit['stoichiometry'] = subunit['stoichiometry']
            else:
                raise ValueError('`subunit` has no `stoichiometry`')

            self.subunits.append(Subunit(id=new_subunit['id'], stoichiometry=new_subunit['stoichiometry']))

        self.clean()

        return self

    def clean(self):
        """ Clean up the subunits and the crosslinks

        For example, convert `1 * a + 1 * a` to `2 * a`

        """
        subunits_cleaned = []
        subunit_unique_ids = []
        for subunit in self.subunits:
            if isinstance(subunit, Subunit):
                id = subunit.id
                if id not in subunit_unique_ids:
                    subunit_unique_ids.append(id)
                    subunits_cleaned.append(subunit)
                else:
                    next(subunit_cleaned for subunit_cleaned in subunits_cleaned if subunit_cleaned.id == id).stoichiometry += subunit.stoichiometry
            elif isinstance(subunit, BcForm):
                subunit.clean()
                subunits_cleaned.append(subunit)

        self.subunits = subunits_cleaned

    def get_formula(self, subunit_formulas=None):
        """ Get the empirical formula

        * If user wants to calculate formula of nested BcForm, where some subunits
          are BcForm objects, then the subunit BcForms must be able to calculate
          its own formula through structure

        Args:
            subunit_formulas (:obj:`dict` or :obj:`None`): dictionary of subunit ids and empirical formulas

        Returns:
            :obj:`EmpiricalFormula`: the empirical formula of the BcForm

        Raises:
            :obj:`ValueError`: subunit formulas does not include all subunits
            :obj:`ValueError`: Not all subunits have defined formula
        """

        formula = EmpiricalFormula()

        # subunits
        if subunit_formulas is None:
            for subunit in self.subunits:
                if subunit.get_formula() is None:
                    raise ValueError('Not all subunits have defined formula')
                formula += subunit.get_formula()
        else:
            for subunit in self.subunits:
                if isinstance(subunit, BcForm):
                    formula += subunit.get_formula()
                else:
                    if subunit.id not in subunit_formulas:
                        raise ValueError('subunit_formulas must include all subunits')
                    else:
                        formula += subunit.get_formula(formula=subunit_formulas[subunit.id])

        # crosslinks
        for crosslink in self.crosslinks:
            for atom in itertools.chain(crosslink.get_l_displaced_atoms(), crosslink.get_r_displaced_atoms()):
                formula[atom.element] -= 1
        return formula

    def get_mol_wt(self, subunit_mol_wts=None):
        """ Get the molecular weight

        * If user wants to calculate molecular weight of nested BcForm, where
          some subunits are BcForm objects, then the subunit BcForms must be able
          to calculate its own molecular weight through structure

        Args:
            subunit_formulas (:obj:`dict` or :obj:`None`): dictionary of subunit ids and molecular weights

        Returns:
            :obj:`float`: the molecular weight of the BcForm

        Raises:
            :obj:`ValueError`: subunit_mol_wts does not include all subunits
            :obj:`ValueError`: Not all subunits have defined molecular weight
        """
        mol_wt = 0.0

        # subunits
        if subunit_mol_wts is None:
            for subunit in self.subunits:
                if subunit.get_mol_wt() is None:
                    raise ValueError('Not all subunits have defined molecular weight')
                mol_wt += subunit.get_mol_wt()
        else:
            for subunit in self.subunits:
                if isinstance(subunit, BcForm):
                    mol_wt += subunit.get_mol_wt()
                else:
                    if subunit.id not in subunit_mol_wts:
                        raise ValueError('subunit_mol_wts must include all subunits')
                    else:
                        mol_wt += subunit.get_mol_wt(mol_wt=subunit_mol_wts[subunit.id])

        # crosslinks
        for crosslink in self.crosslinks:
            for atom in itertools.chain(crosslink.get_l_displaced_atoms(), crosslink.get_r_displaced_atoms()):
                mol_wt -= EmpiricalFormula(atom.element).get_molecular_weight()

        return mol_wt

    def get_charge(self, subunit_charges=None):
        """ Get the total charge

        * If user wants to calculate charge of nested BcForm, where
          some subunits are BcForm objects, then the subunit BcForms must be able
          to calculate its own charge through structure

        Args:
            subunit_formulas (:obj:`dict` or :obj:`None`): dictionary of subunit ids and charges

        Returns:
            :obj:`int`: the total charge of the BcForm

        Raises:
            :obj:`ValueError`: subunit_charges does not include all subunits
            :obj:`ValueError`: Not all subunits have defined charge
        """
        charge = 0

        # subunits
        if subunit_charges is None:
            for subunit in self.subunits:
                if subunit.get_charge() is None:
                    raise ValueError('Not all subunits have defined charge')
                charge += subunit.get_charge()
        else:
            for subunit in self.subunits:
                if isinstance(subunit, BcForm):
                    charge += subunit.get_charge()
                else:
                    if subunit.id not in subunit_charges:
                        raise ValueError('subunit_charges must include all subunits')
                    else:
                        charge += subunit.get_charge(charge=subunit_charges[subunit.id])

        # crosslinks
        for crosslink in self.crosslinks:
            for atom in itertools.chain(crosslink.get_l_displaced_atoms(), crosslink.get_r_displaced_atoms()):
                charge -= atom.charge

        # return the total charge
        return charge

    def validate(self):
        """ Check if the BcForm is valid

        * Check if the crosslinking subunit is in the subunit list and if the `subunit_idx` is valid

        Returns:
            :obj:`list` of :obj:`str`: list of errors, if any

        """
        errors = []

        # crosslinks
        self_subunits_subunits = [subunit for subunit in self.subunits if isinstance(subunit, Subunit)]
        self_subunits_bcforms = [subunit for subunit in self.subunits if isinstance(subunit, BcForm)]

        atom_types = ['l_bond_atoms', 'l_displaced_atoms', 'r_bond_atoms', 'r_displaced_atoms']
        for i_crosslink, crosslink in enumerate(self.crosslinks):
            for atom_type in atom_types:
                for i_atom, atom in enumerate(getattr(crosslink, 'get_'+atom_type)()):
                    # check if subunit is present
                    if atom.subunit not in [subunit.id for subunit in self_subunits_subunits]:
                        errors.append("'{}[{}]' of crosslink {} must belong to a subunit in self.subunits".format(
                            atom_type, i_atom, i_crosslink + 1))
                    # check subunit index
                    elif atom.subunit_idx is None:
                        if next(subunit for subunit in self_subunits_subunits if subunit.id == atom.subunit).stoichiometry > 1:
                            errors.append("crosslink {} contains multiple subunit '{}', so the subunit_idx of atom '{}[{}]' cannot be None".format(
                                i_crosslink + 1, atom.subunit, atom_type, i_atom))
                    elif atom.subunit_idx > next(subunit for subunit in self_subunits_subunits if subunit.id == atom.subunit).stoichiometry:
                        errors.append("'{}[{}]' of crosslink {} must belong to a subunit whose index is "
                                      "valid in terms of the stoichiometry of the subunit".format(
                                          atom_type, i_atom, i_crosslink + 1))

        for self_subunits_bcform in self_subunits_bcforms:
            errors.extend(self_subunits_bcform.validate())

        return errors

    def is_equal(self, other):
        """ Check if two complexes are semantically equal (same subunits and crosslinks)

        Args:
            other (:obj:`BcForm`): another complex

        Returns:
            :obj:`bool`: :obj:`True`, if the complexes are semantically equal

        """

        if self is other:
            return True
        if self.__class__ != other.__class__:
            return False

        # test subunits
        if len(self.subunits) != len(other.subunits):
            return False
        for self_subunit in self.subunits:
            found = False
            for other_subunit in other.subunits:
                if self_subunit.is_equal(other_subunit):
                    found = True
                    break
            if not found:
                return False

        # test crosslinks
        if len(self.crosslinks) != len(other.crosslinks):
            return False
        for self_crosslink in self.crosslinks:
            found = False
            for other_crosslink in other.crosslinks:
                if self_crosslink.is_equal(other_crosslink):
                    found = True
                    break
            if not found:
                return False

        return True

    def get_subunit_attribute(self, subunit_id, attribute):
        """ Set attribute (stoichiometry, structure) of subunit by id

        Args:
            subunit_id (:obj:`str`): id of subunit
            attribute (:obj:`str`): attribute to set

        Returns:
            :obj:`int` for stoichiometry, :obj:`bpforms.BpForm`, :obj:`openbabel.OBMol`, or None for structure

        Raises:
            :obj:`ValueError`: No Subunit with subunit_id
            :obj:`ValueError`: Invalid attribute
        """

        subunit = next((subunit for subunit in self.subunits if isinstance(subunit, Subunit) and subunit.id == subunit_id), None)
        if subunit is None:
            raise ValueError('No Subunit with subunit_id')

        if attribute not in ['stoichiometry', 'structure', 'formula', 'mol_wt', 'charge']:
            raise ValueError('Invalid attribute')

        return getattr(subunit, attribute)

    def set_subunit_attribute(self, subunit_id, attribute, value):
        """ Set attribute (stoichiometry, structure) of subunit by id

        Args:
            subunit_id (:obj:`str`): id of subunit
            attribute (:obj:`str`): attribute to set
            value (:obj:`int` for stoichiometry, :obj:`bpforms.BpForm`, :obj:`openbabel.OBMol`, or None for structure): value

        Raises:
            :obj:`ValueError`: No Subunit with subunit_id
            :obj:`ValueError`: Invalid attribute
        """

        subunit = next((subunit for subunit in self.subunits if isinstance(subunit, Subunit) and subunit.id == subunit_id), None)
        if subunit is None:
            raise ValueError('No Subunit with subunit_id')

        if attribute not in ['stoichiometry', 'structure', 'formula', 'mol_wt', 'charge']:
            raise ValueError('Invalid attribute')

        setattr(subunit, attribute, value)

    def get_structure(self):
        """ Get an Open Babel molecule of the structure

        Returns:
            :obj:`openbabel.OBMol`: Open Babel molecule of the structure
        """
        mol = openbabel.OBMol()

        atom_maps = []
        n_atoms = [0]

        # subunits
        for i_subunit, subunit in enumerate(self.subunits):
            structure, atom_map = subunit.get_structure()
            mol += structure

            n_atoms.append(n_atoms[-1]+structure.NumAtoms())

            for subunit_map in atom_map.values():
                for monomer in subunit_map.values():
                    for atom_type in monomer.values():
                        for i_atom, atom in atom_type.items():
                            atom_type[i_atom] = atom+n_atoms[i_subunit]
            atom_maps.append(atom_map)

        # print(atom_maps)

        for atom_map in atom_maps:
            for subunit_map in atom_map.values():
                for monomer in subunit_map.values():
                    for atom_type in monomer.values():
                        for i_atom, atom in atom_type.items():
                            atom_type[i_atom] = mol.GetAtom(atom)

        # mol.AddHydrogens()

        # print(atom_maps)
        # for i in range(mol.NumAtoms()):
        #     print(mol.GetAtom(i+1), mol.GetAtom(i+1).GetAtomicNum())

        bonding_hydrogens = []
        # crosslinks
        # get the atoms
        crosslinks_atoms = []
        for crosslink in self.crosslinks:
            crosslink_atoms = {}
            crosslinks_atoms.append(crosslink_atoms)
            for atom_type in ['l_bond_atoms', 'r_bond_atoms', 'l_displaced_atoms', 'r_displaced_atoms']:
                crosslink_atoms[atom_type] = []
                for atom_md in getattr(crosslink, 'get_'+atom_type)():
                    i_subunit = [i for i in range(len(self.subunits)) if self.subunits[i].id == atom_md.subunit][0]
                    subunit_idx = 1 if atom_md.subunit_idx is None else atom_md.subunit_idx
                    atom = atom_maps[i_subunit][subunit_idx][atom_md.monomer][atom_md.component_type][atom_md.position]
                    if atom_md.element == 'H' and atom.GetAtomicNum() != 1:
                        atom = get_hydrogen_atom(atom, bonding_hydrogens, (i_subunit, subunit_idx -
                                                                           1, atom_md.monomer-1, atom_md.component_type))
                    crosslink_atoms[atom_type].append((atom, i_subunit, subunit_idx, atom_md.monomer, atom_md.position, atom_md.charge))

        # print(OpenBabelUtils.export(mol, format='smiles', options=[]))

        # make the crosslink bonds
        for crosslink, atoms in zip(self.crosslinks, crosslinks_atoms):

            for atom, i_subunit, subunit_idx, i_monomer, i_position, atom_charge in itertools.chain(atoms['l_displaced_atoms'], atoms['r_displaced_atoms']):
                if atom:
                    atom_2 = atom_maps[i_subunit][subunit_idx][i_monomer]['monomer'].get(i_position, None)
                    if atom_2 and atom_2.GetIdx() == atom.GetIdx():
                        atom_maps[i_subunit][subunit_idx][i_monomer]['monomer'].pop(i_position)
                    assert mol.DeleteAtom(atom, True)

            for (l_atom, _, _, _, _, l_atom_charge), (r_atom, _, _, _, _, r_atom_charge) in zip(atoms['l_bond_atoms'], atoms['r_bond_atoms']):
                bond = openbabel.OBBond()
                bond.SetBegin(l_atom)
                bond.SetEnd(r_atom)
                bond.SetBondOrder(crosslink.get_order().value)
                stereo = crosslink.get_stereo()
                if stereo is None:
                    pass
                elif stereo == BondStereo.wedge:
                    bond.SetWedge()
                elif stereo == BondStereo.hash:
                    bond.SetHash()
                elif stereo == BondStereo.up:
                    bond.SetUp()
                elif stereo == BondStereo.down:
                    bond.SetDown()
                assert mol.AddBond(bond)

                if l_atom_charge:
                    l_atom.SetFormalCharge(l_atom.GetFormalCharge() + l_atom_charge)

                if r_atom_charge:
                    r_atom.SetFormalCharge(r_atom.GetFormalCharge() + r_atom_charge)

        for atom_map in atom_maps:
            for subunit_map in atom_map.values():
                for monomer in subunit_map.values():
                    for atom_type in monomer.values():
                        for i_atom, atom in atom_type.items():
                            if atom is not None:
                                atom_type[i_atom] = atom.GetIdx()

        return mol, atom_maps

    def export(self, format='smiles', options=[]):
        """ Export the structure to string

        Args:
            format (:obj:`str`, optional): export format
            options (:obj:`list`, optional): export options

        Returns:
            :obj:`str`: exported string representation of the structure

        """
        return OpenBabelUtils.export(self.get_structure()[0], format=format, options=options)

    def get_genomic_image(self, seq_features=None, width=1200, cols=2, nt_per_track=80, **kwargs):
        """ Get a genomic visualization of the :obj:`BpForm`

        Args:
            seq_features (:obj:`dict`): list of features each
                represented by a dictionary with three keys

                * label (:obj:`str`): description of the type of feature
                * color (:obj:`str`): color
                * positions (:obj:`list` of :obj:`list` of :obj:`int`): list of position
                  ranges of the type of feature
            width (:obj:`int`, optional): width
            cols (:obj:`int`, optional): number of columns of polymers
            nt_per_track (:obj:`int`, optional): number of nucleotides per track

        The method also accepts the same arguments as 
            :obj:`bpforms.util.gen_genomic_viz`.

        Returns:
            :obj:`str`: SVG image
        """
        polymers = []
        polymer_labels = {}
        polymer_idxs = {}
        i_tot_subunit = 0
        for subunit in self.subunits:
            if isinstance(subunit.structure, bpforms.BpForm):
                for i_repeat in range(subunit.stoichiometry):
                    polymers.append(subunit.structure)
                    if subunit.stoichiometry == 1:
                        polymer_labels[i_tot_subunit] = subunit.id
                    else:
                        polymer_labels[i_tot_subunit] = '{} ({})'.format(subunit.id, i_repeat + 1)
                    polymer_idxs[(subunit.id, i_repeat)] = len(polymer_idxs)
                    i_tot_subunit += 1

        inter_crosslinks = []
        for crosslink in self.crosslinks:
            if len(crosslink.get_l_bond_atoms()) >= 1:
                l = crosslink.get_l_bond_atoms()[0]
                r = crosslink.get_r_bond_atoms()[0]

                l_subunit = polymer_idxs[(l.subunit, l.subunit_idx - 1)]
                r_subunit = polymer_idxs[(r.subunit, r.subunit_idx - 1)]

                if isinstance(crosslink, OntologyCrosslink):
                    tooltip = crosslink.type
                else:
                    tooltip = None

                inter_crosslinks.append(InlineCrosslink(
                    l_bond_atoms=[Atom(str(l_subunit), l.element, l.position, l.monomer)],
                    r_bond_atoms=[Atom(str(r_subunit), r.element, r.position, r.monomer)],
                    comments=tooltip))

        seq_features = seq_features or []
        flat_seq_features = []
        for seq_feature in seq_features:
            flat_seq_feature = {
                'label': seq_feature['label'],
                'color': seq_feature['color'],
                'positions': {},
            }
            flat_seq_features.append(flat_seq_feature)
            for subunit in self.subunits:
                if subunit.id in seq_feature['positions']:
                    for i_repeat in range(subunit.stoichiometry):
                        flat_seq_feature['positions'][polymer_idxs[(subunit.id, i_repeat)]] = \
                            seq_feature['positions'][subunit.id]

        return gen_genomic_viz(polymers, inter_crosslinks=inter_crosslinks,
                               polymer_labels=polymer_labels, seq_features=flat_seq_features,
                               width=width, cols=cols, nt_per_track=nt_per_track,
                               **kwargs)


def get_hydrogen_atom(parent_atom, bonding_hydrogens, i_monomer):
    """ Get a hydrogen atom attached to a parent atom
    Args:
        parent_atom (:obj:`openbabel.OBAtom`): parent atom
        bonding_hydrogens (:obj:`list`): hydrogens that have already been gotten
        i_monomer (:obj:`int`): index of parent monomer in sequence
    Returns:
        :obj:`openbabel.OBAtom`: hydrogen atom
    """
    for other_atom in openbabel.OBAtomAtomIter(parent_atom):
        if other_atom.GetAtomicNum() == 1:
            tmp = (i_monomer, other_atom.GetIdx())
            if tmp not in bonding_hydrogens:  # hydrogen
                bonding_hydrogens.append(tmp)
                return other_atom
    return None


def draw_xlink(xlink_name, include_all_hydrogens=False, remove_hydrogens=True, show_atom_nums=False,
               l_color=0x00ea4e, r_color=0x00adef, bond_color=0xea4200,
               width=300, height=200, atom_label_font_size=0.6,
               image_format='png', include_xml_header=False):
    """ Generate an image of a crosslink

    Args:
        xlink_name (:obj:`str`): name of xlink
        include_all_hydrogens (:obj:`bool`, optional): if :obj:`True`, show all hydrogens
        remove_hydrogens (:obj:`bool`, optional): if :obj:`True`, remove all hydrogens
        show_atom_nums (:obj:`bool`, optional): if :obj:`True`, show atom numbers
        l_color (:obj:`int`, optional): color of left monomer
        r_color (:obj:`int`, optional): color of right monomer
        bond_color (:obj:`int`, optional): color of crosslinking bond
        width (:obj:`int`, optional): width
        height (:obj:`int`, optional): height
        atom_label_font_size (:obj:`float`, optional): relative font size of atom labels
        image_format (:obj:`str`, optional): format of image
        include_xml_header (:obj:`bool`, optional): if :obj:`True`, include XML header for SVG image

    Returns:
        :obj:`object`: image
    Raises:
        :obj:`KeyError`: Unknown crosslink id
        :obj:`ValueError`: Unknown monomer alphabet
    """
    xlink_detail_dict = parse_yaml(_xlink_filename)
    if xlink_name in xlink_detail_dict:
        xlink_details = xlink_detail_dict[xlink_name]
    else:
        raise KeyError('Unknown crosslink id')

    # create the bcform
    form = BcForm()

    l_monomer_alphabet = xlink_details['l_monomer_alphabet']
    if l_monomer_alphabet == 'protein':
        l_monomer = bpforms.ProteinForm().from_str(xlink_details['l_monomer'])
    elif l_monomer_alphabet == 'dna':
        l_monomer = bpforms.DnaForm().from_str(xlink_details['l_monomer'])
    elif l_monomer_alphabet == 'rna':
        l_monomer = bpforms.RnaForm().from_str(xlink_details['l_monomer'])
    else:
        raise ValueError('Unknown monomer alphabet')

    r_monomer_alphabet = xlink_details['r_monomer_alphabet']
    if r_monomer_alphabet == 'protein':
        r_monomer = bpforms.ProteinForm().from_str(xlink_details['r_monomer'])
    elif r_monomer_alphabet == 'dna':
        r_monomer = bpforms.DnaForm().from_str(xlink_details['r_monomer'])
    elif r_monomer_alphabet == 'rna':
        r_monomer = bpforms.RnaForm().from_str(xlink_details['r_monomer'])
    else:
        raise ValueError('Unknown monomer alphabet')

    form.subunits.append(Subunit(id='l', stoichiometry=1, structure=l_monomer))
    form.subunits.append(Subunit(id='r', stoichiometry=1, structure=r_monomer))
    form.crosslinks.append(OntologyCrosslink(type=xlink_name, l_subunit='l', l_monomer=1, r_subunit='r', r_monomer=1))

    structure, atom_maps = form.get_structure()

    el_table = openbabel.OBElementTable()

    atom_labels = []
    for i_atom in atom_maps[0][1][1]['monomer'].values():
        if structure.GetAtom(i_atom).GetAtomicNum() > 1:
            break
    atom_labels.append({
        'position': i_atom,
        'element': el_table.GetSymbol(structure.GetAtom(i_atom).GetAtomicNum()),
        'label': xlink_details['l_monomer'],
        'color': l_color})

    for i_atom in atom_maps[1][1][1]['monomer'].values():
        if structure.GetAtom(i_atom).GetAtomicNum() > 1:
            break
    atom_labels.append({
        'position': i_atom,
        'element': el_table.GetSymbol(structure.GetAtom(i_atom).GetAtomicNum()),
        'label': xlink_details['r_monomer'],
        'color': r_color})

    atom_sets = []
    for monomer_atom_map, color in zip(atom_maps, [l_color, r_color]):
        positions = []
        elements = []
        for i_atom in monomer_atom_map[1][1]['monomer'].values():
            atom = structure.GetAtom(i_atom)
            if atom:
                positions.append(i_atom)
                elements.append(el_table.GetSymbol(structure.GetAtom(i_atom).GetAtomicNum()))
        atom_sets.append({'positions': positions, 'elements': elements, 'color': color})

    i_l_atom = atom_maps[0][1][1]['monomer'][form.crosslinks[0].get_l_bond_atoms()[0].position]
    i_r_atom = atom_maps[1][1][1]['monomer'][form.crosslinks[0].get_r_bond_atoms()[0].position]

    bond_sets = [{
        'positions': [[i_l_atom, i_r_atom]],
        'elements': [[
            el_table.GetSymbol(structure.GetAtom(i_l_atom).GetAtomicNum()),
            el_table.GetSymbol(structure.GetAtom(i_r_atom).GetAtomicNum()),
        ]],
        'color': bond_color,
    }]

    if include_all_hydrogens:
        structure.AddHydrogens()

    if remove_hydrogens:
        atom_refs = {}
        for i_atom in range(1, structure.NumAtoms() + 1):
            atom_refs[i_atom] = structure.GetAtom(i_atom)

        structure.DeleteHydrogens()

        atoms = [atom for atom in openbabel.OBMolAtomIter(structure)]

        for label in atom_labels:
            label['position'] = atom_refs[label['position']].GetIdx()

        for atom_set in atom_sets:
            atom_set['positions'] = [atom_refs[position].GetIdx() for position in atom_set['positions'] if atom_refs[position] in atoms]
            atom_set['elements'] = [el_table.GetSymbol(structure.GetAtom(position).GetAtomicNum()) for position in atom_set['positions']]

        for bond_set in bond_sets:
            bond_set['positions'] = [[atom_refs[position[0]].GetIdx(), atom_refs[position[1]].GetIdx()]
                                     for position in bond_set['positions']]

    cml = OpenBabelUtils.export(structure, 'cml')

    return draw_molecule(cml, 'cml', image_format=image_format,
                         atom_labels=atom_labels, atom_label_font_size=atom_label_font_size,
                         atom_sets=atom_sets, bond_sets=bond_sets,
                         show_atom_nums=show_atom_nums,
                         width=width, height=height, include_xml_header=include_xml_header)
