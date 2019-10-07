import contextlib
import io
import os
import sys

from Bio import PDB


def load_pdb_file(pdb_file):
    parser = PDB.PDBParser()
    pdb_name = ''.join(os.path.splitext(os.path.basename(pdb_file))[:-1])
    return parser.get_structure(pdb_name, pdb_file)


@contextlib.contextmanager
def capture():
    """
    Thank you https://stackoverflow.com/a/10743550
    """
    oldout,olderr = sys.stdout, sys.stderr
    try:
        out=[io.StringIO(), io.StringIO()]
        sys.stdout,sys.stderr = out
        yield out
    finally:
        sys.stdout,sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()
