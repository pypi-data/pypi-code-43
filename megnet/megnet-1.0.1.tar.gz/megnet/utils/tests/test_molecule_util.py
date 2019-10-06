import os
import unittest
from megnet.utils.molecule import MEGNetMolecule, get_pmg_mol_from_smiles, pb
from megnet.models import MEGNetModel
from pymatgen import Molecule

CWD = os.path.dirname(os.path.abspath(__file__))


class TestMolecule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.molecule = MEGNetMolecule(['C', 'O', 'O'], [[0, 0, 0], [-1, 0, 0], [1, 0, 0]])
        cls.model = MEGNetModel.from_file(os.path.join(CWD, '../../../mvl_models/mp-2019.4.1/formation_energy.hdf5'))

    def test_mol(self):
        pred = self.model.predict_structure(self.molecule)
        self.assertAlmostEqual(float(pred), 0.39973044, 5)

    def test_from_mol(self):
        pmg_mol = Molecule(['C', 'O', 'O'], [[0, 0, 0], [-1, 0, 0], [1, 0, 0]])
        meg_mol = MEGNetMolecule.from_pymatgen(pmg_mol)
        self.assertTrue(meg_mol == self.molecule)

    @unittest.skipIf(pb is None, "Openbabel is not installed")
    def test_get_pmg_mol_from_smiles(self):
        mol = get_pmg_mol_from_smiles('C')
        self.assertTrue(isinstance(mol, Molecule))


if __name__ == "__main__":
    unittest.main()
