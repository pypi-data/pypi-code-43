""" Generic printing function. Current choices: JSON and YAML (default) """


from ..core.cli import CliOptions
from ..core.log import info
from .to_json import print_json
from .to_yaml import print_yaml
from .to_table import print_evcs_table
from .to_stats import print_stats_per_nni


def print_evcs(ctks):
    """ Uses CliOptions() to understand the current output format. """

    if not ctks:
        info("No EVCs found.")
        return

    if CliOptions().output_format == 'json':
        print_json(ctks)
    elif CliOptions().output_format == 'table':
        print_evcs_table(ctks)
    elif CliOptions().output_format == 'stats':
        print_stats_per_nni(ctks)
    elif CliOptions().output_format == 'zabbix':
        print_json(ctks)
    else:
        print_yaml(ctks)
