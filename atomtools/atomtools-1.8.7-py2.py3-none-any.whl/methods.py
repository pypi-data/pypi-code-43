"""




general methods used for GASE


"""

import numpy as np


def __get_atoms_arrays(obj):
    """
    basic transform atoms to arrays
    """
    if isinstance(obj, dict):
        return obj
    obj_type = f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    if obj_type in ['ase.atoms.Atoms', 'gase.aseshell.AtomsShell']:
        arrays = obj.arrays.copy()
        if obj_type == 'ase.atoms.Atoms':
            # set cell & pbc
            arrays['cell'] = obj.cell.array.copy()
            arrays['pbc'] = obj.pbc.copy()
            arrays['cell_disp'] = obj.get_celldisp()
            calc = obj.calc
            if calc is not None:
                if calc.name:
                    arrays['calc_arrays'] = {'name': calc.name}
                if calc.parameters:
                    arrays['calc_arrays'].update(calc.parameters)
                if calc.result:
                    arrays['calc_arrays'].update(calc.results)
    elif obj_type == 'pymatgen.core.structure.Structure':
        raise NotImplementedError("Pymatgen will be supported in the future")
    else:
        raise NotImplementedError(f"{obj_type} is wired!")
    return arrays


def get_atoms_arrays(obj):
    """
    Transform a Atoms like object to arrays(dict/list of dict)
        input:
            obj: dict/list/ase.Atoms/gase.AtomsShell (future: pymatgen.core.structure.Structure)
        output:
            arrays(dict/list of dict)
    """
    obj_type = f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    if isinstance(obj, dict):
        arrays = obj
    elif isinstance(obj, (list, np.ndarray)):
        arrays = [__get_atoms_arrays(x) for x in obj]
    elif obj_type == 'ase.neb.NEB':
        arrays = [__get_atoms_arrays(x) for x in obj.images]
    else:
        arrays = __get_atoms_arrays(obj)
    return arrays
