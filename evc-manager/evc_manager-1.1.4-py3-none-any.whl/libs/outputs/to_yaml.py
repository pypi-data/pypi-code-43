""" YAML module. Used to read and write in YAML format """

from datetime import datetime
from yaml import dump
import yaml
from ..core.cli import CliOptions


class MyDumper(yaml.Dumper):  # pylint: disable=R0901
    """ Ignore aliases when printing dictionaries using YAML """
    def ignore_aliases(self, _data):  # pylint: disable=W0221
        return True


def print_yaml(ctks):
    """ Exported function to print in YAML """
    print("Number of Circuits: %s " % len(ctks))

    evcs = dict()
    evcs['evcs'] = ctks
    evcs['version'] = '1.0'

    now = datetime.now()
    now.strftime("%Y/%m/%d %H:%M:%S")
    evcs['date'] = now

    with open(CliOptions().destination_file, 'w') as yaml_file:
        dump(evcs, yaml_file, default_flow_style=False, Dumper=MyDumper)
        print("List of circuits saved on file: %s " %
              CliOptions().destination_file)
