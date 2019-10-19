from astropy import units as u
from astropy.table import Table, vstack
from astropy.utils.data import get_pkg_data_filename

from ..aij import parse_aij_table

# This is actually tab-separated text, not a native Excel file
AIJ_FILE = get_pkg_data_filename('data/aij-Measurements-sample2.xls')


def test_aij_opens():
    print(AIJ_FILE)
    aij_data = parse_aij_table(AIJ_FILE)
    assert len(aij_data) == 12
    tables = [star._table for star in aij_data]
    foo = vstack(tables)
    assert len(set(foo['star_id'])) == 12
    print('\n'.join(foo.colnames))
    print(foo['RA'])
    assert 0
