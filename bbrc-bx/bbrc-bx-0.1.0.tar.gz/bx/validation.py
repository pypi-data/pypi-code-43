import logging as log
import os.path as op
from datetime import datetime
from tqdm import tqdm

def collect_reports(xnat_instance, experiments,
        validator_name='ArchivingValidator', version=['toto']):
    import json
    url = '/data/experiments/%s/resources/BBRC_VALIDATOR/files/%s'
    reports = {}

    for e in tqdm(experiments):
        columns = ['ID', 'label', 'xsiType']
        exp = xnat_instance.array.experiments(experiment_id=e,
                                              columns=columns).data
        assert(len(exp)==1)
        uri = url%(exp[0]['ID'], '%s_%s.json'%(validator_name, exp[0]['label']))
        r = xnat_instance.select.experiment(e).resource('BBRC_VALIDATOR')
        if not r.exists(): continue
        f = r.file('%s_%s.json'%(validator_name, exp[0]['label']))
        if not f.exists(): continue

        j = json.loads(xnat_instance.get(f._uri).text)
        if 'version' not in j.keys():
            log.warning('Version not found in report %s'%j.keys())
            continue
        if j['version'] not in version: continue
        fields = list(j.keys())
        try:
            for each in ['version', 'generated', 'experiment_id']:
                fields.remove(each)
        except ValueError:
            msg = 'No valid report found (%s).'%e
            log.error(msg)
            raise Exception(msg)
        if j['version'] not in  version: continue
        reports[e] = j

    return reports

def validation_scores(x, validator, version,  id, test=False):
    from bx import parse
    t = parse.check_xnat_item(id, x)

    experiments = []
    if t == 1:
        experiments = [id]

    elif t == 0:
        max_rows = 1 if test else None
        experiments = []
        for e in x.array.experiments(project_id=id,
                columns=['label']).data[:max_rows]:
            experiments.append(e['ID'])

    res = []
    fields = []
    log.info('Looking for experiments with %s report with versions %s.'\
                %(validator, version))
    reports = dict(list(collect_reports(x, validator_name=validator,
        experiments=experiments, version=version).items())[:max_rows])
    print(reports)
    log.info('Now initiating download for %s experiment(s).'\
            %len(reports.items()))

    for e, report in tqdm(reports.items()):
        fields = list(report.keys())
        for each in ['version', 'generated', 'experiment_id']:
            fields.remove(each)
        row = [e]
        row.extend([report[f]['has_passed'] for f in fields])
        res.append(row)

    import pandas as pd
    fields.insert(0, 'ID')
    df = pd.DataFrame(res, columns=fields).set_index('ID')
    return df


def subcommand_tests(parser, validator, version, test=False):
    subcommand = parser.args[0]
    id = parser.args[1]

    from bx.validation import validation_scores
    df = validation_scores(parser.xnat, validator=validator,
        id=id, version=version, test=test)

    dt = datetime.today().strftime('%Y%m%d_%H%M%S')
    fn = 'bx_%s_%s_%s_%s.xlsx'%(parser.command, subcommand, id, dt)
    fp = op.join(parser.destdir, fn)
    log.info('Saving it in %s'%fp)
    df.to_excel(fp)
