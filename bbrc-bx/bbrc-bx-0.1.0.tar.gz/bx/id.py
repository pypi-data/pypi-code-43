import logging as log
from datetime import datetime
import os.path as op
from bx.parse import Command

class IDCommand(Command):
    nargs = 1

    def __init__(self, *args, **kwargs):
        super(IDCommand, self).__init__(*args, **kwargs)

    def parse(self, test=False):
        id = self.args[0]
        df = self.run_id(id, get_id_table, test=test)

        self.to_excel(id, df)


def get_id_table(x, experiments):
    table = []
    from tqdm import tqdm
    columns = ['label', 'subject_label']
    for e in tqdm(experiments):
        exp = x.array.experiments(experiment_id=e['ID'], columns=columns).data[0]
        table.append([exp['ID'], exp['label'], exp['subject_label']])

    import pandas as pd
    columns = ['ID', 'label', 'subject_label']
    df = pd.DataFrame(table, columns=columns).set_index('ID').sort_index()
    return df
