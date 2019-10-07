import difflib
import io

import click

from pdbfairy import utils
from pdbfairy.commands import find_interactions


@click.argument('pdb_file_1')
@click.argument('pdb_file_2')
@click.option('--max-distance', default=find_interactions.MAX_DISTANCE, help=(
    "The distance in Angstroms under which atoms should "
    "be considered to interact (default {})"
    .format(find_interactions.MAX_DISTANCE)))
def compare_interactions(pdb_file_1, pdb_file_2, max_distance):
    """
    Show how find-interactions differs for PDB_FILE_1 and PDB_FILE_2
    """
    structure_1 = utils.load_pdb_file(pdb_file_1)
    structure_2 = utils.load_pdb_file(pdb_file_2)

    with utils.capture() as (interactions_text_1, _):
        find_interactions.print_interactions(structure_1, max_distance)
    with utils.capture() as (interactions_text_2, _):
        find_interactions.print_interactions(structure_2, max_distance)

    differ = difflib.Differ()
    diff = list(differ.compare(
        interactions_text_1.getvalue().splitlines()[5:],
        interactions_text_2.getvalue().splitlines()[5:],
    ))

    print("PDB file name 1\t{}".format(structure_1.id))
    print("PDB file name 2\t{}".format(structure_2.id))
    print("Distance cutoff\t{}".format(max_distance))
    print()
    print()
    print()
    print('File\t{}'.format(diff[0].strip()))

    for line in sorted(diff[1:]):
        marker, rest = line[:2], line[2:]
        if marker == '- ':
            print('{}\t{}'.format(structure_1.id, rest))
        elif marker == '+ ':
            print('{}\t{}'.format(structure_2.id, rest))
        elif marker == '  ':
            print('both\t{}'.format(rest))
        elif marker in ('', '? '):
            pass
        else:
            raise ValueError("This should never happen: {!r}".format(marker))
