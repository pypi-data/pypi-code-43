import builtins
import collections
import functools
import math
import sys

import click
import memoized
from numpy import linalg
import numpy

from pdbfairy import utils

MAX_DISTANCE = 4


@click.argument('pdb_file')
@click.option('--max-distance', default=MAX_DISTANCE, help=(
    "The distance in Angstroms under which atoms should "
    "be considered to interact (default {})".format(MAX_DISTANCE)))
def find_interactions(pdb_file, max_distance):
    """
    Find all intermolecular pairs of residues in PDB_FILE that interact

    The output will be tab-separated values, something you can
    paste into a spreadsheet (Google Spreadsheets, etc., Excel).
    """
    structure = utils.load_pdb_file(pdb_file)
    print_interactions(structure, max_distance)


def print_interactions(structure, max_distance):
    res_pairs = find_residue_pairs(structure, max_distance)

    print("PDB file name\t{}".format(structure.id))
    print("Distance cutoff\t{}".format(max_distance))
    print()
    print()
    print()
    print("Chain\tResidue number\tChain\tResidue number")

    lines = []

    def get_line(res_1, res_2):
        return (get_res_chain(res_1), get_res_number(res_1),
                get_res_chain(res_2), get_res_number(res_2))

    for res_1, res_2 in res_pairs:
        lines.append(get_line(res_1, res_2))
        lines.append(get_line(res_2, res_1))
    lines.sort()
    for line in lines:
        print('{}\t{}\t{}\t{}'.format(*line))


def find_residue_pairs(structure, max_distance):
    atom_pairs = find_pairs(structure, max_distance)
    res_pairs = set()
    for atom_1, atom_2 in atom_pairs:
        res_pairs.add((atom_1.parent, atom_2.parent))
    return res_pairs


def find_pairs(structure, max_distance):
    atoms = list(structure.get_atoms())
    atom_store = AtomStore(atoms, max_distance=max_distance)
    for atom in atoms:
        yield from atom_store.find_neighbors(atom)
        atom_store.remove(atom)


class AtomStore(object):
    def __init__(self, atoms, max_distance):
        # max distance for two atoms to be considered "neighbors"
        self.max_distance = max_distance
        self._atoms_by_cube = collections.defaultdict(set)
        self._atoms_by_chain = collections.defaultdict(set)
        for atom in atoms:
            self.add(atom)

    def add(self, atom):
        self._atoms_by_cube[tuple(self._get_cube(atom))].add(atom)
        self._atoms_by_chain[self._get_chain(atom)].add(atom)

    def remove(self, atom):
        self._atoms_by_cube[tuple(self._get_cube(atom))].remove(atom)
        self._atoms_by_chain[self._get_chain(atom)].remove(atom)

    def find_neighbors(self, atom):
        cube = self._get_cube(atom)
        atoms_in_chain = self._atoms_by_chain[self._get_chain(atom)]
        yield from (
            (atom, a)
            for offset in self._offsets
            for a in self._atoms_by_cube[tuple(cube + offset)] - atoms_in_chain
            if dist(a, atom) <= self.max_distance
        )

    @memoized.memoized
    def _get_cube(self, atom):
        return numpy.floor(atom.coord / self.max_distance)

    @memoized.memoized
    def _get_chain(self, atom):
        return atom.parent.parent

    _offsets = [
        numpy.array([i, j, k])
        for i in [-1, 0, 1]
        for j in [-1, 0, 1]
        for k in [-1, 0, 1]
    ]


def dist(atom_1, atom_2):
    return linalg.norm(atom_1.coord - atom_2.coord)


def get_res_chain(res):
    return res.parent.id


def get_res_number(res):
    return res.id[1]
