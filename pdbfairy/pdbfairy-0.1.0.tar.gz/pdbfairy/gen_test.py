import json
import os
import sys

from pdbfairy.main import MAX_DISTANCE, dist
import tests.loader
import tests.test_find_pairs


def main(structure, max_distance, output_file):
    with open(output_file, 'w') as f:
        json.dump(tests.test_find_pairs.run_find_pairs_algorithm(
            find_pairs_brute_force, structure, max_distance), f)


def find_pairs_brute_force(structure, max_distance):
    chains = list(structure.get_chains())
    for c, chain_1 in enumerate(chains):
        for chain_2 in chains[c + 1:]:
            for atom_1 in chain_1.get_atoms():
                for atom_2 in chain_2.get_atoms():
                    if dist(atom_1, atom_2) <= max_distance:
                        yield (atom_1, atom_2)


if __name__ == '__main__':
    pdb_name = sys.argv[1]  # not including .pdb suffix
    try:
        max_distance = float(sys.argv[2])
    except IndexError:
        max_distance = MAX_DISTANCE
    loader = tests.loader.Loader(pdb_name)
    main(loader.get_structure(), max_distance, output_file=loader.output_file)
