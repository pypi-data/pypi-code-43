import os

from Bio import PDB


def load_pdb_file(pdb_file):
    parser = PDB.PDBParser()
    pdb_name = ''.join(os.path.splitext(os.path.basename(pdb_file))[:-1])
    return parser.get_structure(pdb_name, pdb_file)
