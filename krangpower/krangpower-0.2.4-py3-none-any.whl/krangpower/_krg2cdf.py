from . import gv
from ._config_loader import _THISDIR
import json
from os import path
from pandas import Series

with open(path.join(_THISDIR, 'defaults/cdf_scheme.json'), 'r') as scheme_file:
    SCHEME_DICT = json.load(scheme_file)


def krg2cdf(krg):
    krg.command('makeposseq')
    # krg.command('calcvoltagebases')
    krg.solve()

    # stuff for the bus table
    vlt_dic = gv.BusVoltageView(krg).get_node_dict('V')
    bsv_dic = gv.BaseVoltageView(krg).get_node_dict('V')

    cp = krg.Capacitors
    cp_buses = cp['bus1'].values
    ld = krg.Loads
    ld_buses = ld['bus1'].values
    gn = krg.Generators
    gn_buses = gn['bus1'].values

    # stuff for the branch table

    lines = krg.Lines
    xfrms = krg.Transformers