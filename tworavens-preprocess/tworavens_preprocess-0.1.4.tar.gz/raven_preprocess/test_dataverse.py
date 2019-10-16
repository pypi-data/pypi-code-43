import csv
import glob
import json
import pycountry
import subprocess
import sys
import time

import dictdiffer
import matplotlib.pyplot as plt
import pandas as pd

from os.path import abspath, basename, dirname, getsize, isdir, isfile, join, splitext

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(CURRENT_DIR)), 'test_data')
sys.path.append(dirname(CURRENT_DIR))

from raven_preprocess.preprocess_runner import PreprocessRunner

def get_path(filename, where='python'):
    return f'{TEST_DATA_DIR}/dataverse/{where}/{filename}'

replace = dict(
    binary = 'defaultBinary',
    cdfPlotType = 'cdfplottype',
    cdfPlotX = 'cdfplotx',
    cdfPlotY = 'cdfploty',
    description = 'labl',
    fewestFreq = 'freqfewest',
    fewestValues = 'fewest',
    herfindahlIndex = 'herfindahl',
    interval = 'defaultInterval',
    invalidCount = 'invalid',
    max = 'max',
    mean = 'mean',
    median = 'median',
    midpoint = 'mid',
    midpointFreq = 'freqmid',
    min = 'min',
    mode = 'mode',
    modeFreq = 'freqmode',
    nature = 'defaultNature',
    numchar = 'defaultNumchar',
    pdfPlotType = 'plottype',
    pdfPlotX = 'plotx',
    pdfPlotY = 'ploty',
    stdDev = 'sd',
    time = 'defaultTime',
    validCount = 'valid',
    variableName = 'varnamesSumStat',
    uniqueCount = 'uniques'
)

ignore = 'cdfPlotType pdfPlotType plotValues'.split()
ignore += 'cdfPlotX cdfPlotY pdfPlotX pdfPlotY'.split()
ignore += ['interval', 'min', 'max', 'nature', 'numchar', 'variableName']  # differ in R being wrong
ignore += ['fewestFreq', 'fewestValues', 'midpoint', 'midpointFreq', 'mode', 'modeFreq'] # differ in how calulated and num of results
ignore += ['binary', 'invalidCount', 'validCount', 'uniqueCount', 'herfindahlIndex'] # differ in missingness
ignore += ['mean', 'median', 'stdDev'] # differ in rounding

def diff(filename, py_path, R_path):
    try:
        py_obj = json.load(open(py_path))
        for var in py_obj.get('variables', []):
            for k in ignore:
                try:
                    del py_obj['variables'][var][k]
                except:
                    pass
    except:
        py_obj = {}

    try:
        R_obj = json.load(open(R_path))
    except:
        R_obj = {}

    R_obj1 = dict(variables={})
    for var in R_obj.get('variables', []):
        R_obj1['variables'][var] = {}
        for (k, k1) in replace.items():
            val = R_obj['variables'][var].get(k1)
            if val == 0.0 and k == 'modeFreq' or val =='NULL':
                val = None

            try:
                val = float(val)
            except:
                pass

            if k not in ignore:
                R_obj1['variables'][var][k] = val

        continue

        fig, (ax, ax1, ax2, ax3) = plt.subplots(4, 1)

        df = pd.DataFrame()
        df['x'] = pd.Series(R_obj1['variables'][var]['pdfPlotX'])
        df['y'] = pd.Series(R_obj1['variables'][var]['pdfPlotY'])
        if df['x'].any() and df['y'].any():
            df.plot(x='x', y='y', ax=ax)

        df1 = pd.DataFrame()
        df1['x'] = pd.Series(py_obj['variables'][var]['pdfPlotX'])
        df1['y'] = pd.Series(py_obj['variables'][var]['pdfPlotY'])
        if df1['x'].any() and df1['y'].any():
            df1.plot(x='x', y='y', ax=ax1)

        df2 = pd.DataFrame()
        df2['x'] = pd.Series(py_obj['variables'][var]['cdfPlotX'])
        df2['y'] = pd.Series(py_obj['variables'][var]['cdfPlotY'])
        if df2['x'].any() and df2['y'].any():
            df2.plot(x='x', y='y', ax=ax2)

        df3 = pd.DataFrame()
        df3['x'] = pd.Series(py_obj['variables'][var]['cdfPlotX'])
        df3['y'] = pd.Series(py_obj['variables'][var]['cdfPlotY'])
        if df3['x'].any() and df3['y'].any():
            df3.plot(x='x', y='y', ax=ax3)

        plt.savefig(f'{TEST_DATA_DIR}/dataverse/plots/{filename.split(".")[0]}_{var}.png')
        plt.close(fig)

    changes = []
    for change in list(dictdiffer.diff(R_obj1, py_obj, ignore='self dataset variableDisplay'.split(), tolerance=0.01)):
        if change[0] == 'change' and change[2] not in [('yes', True), ('no', False), ('no', 'unknown')]:
            if not (change[2][0] == 'NA' and not isinstance(change[2][1], list) and pd.isna(change[2][1])):
                changes.append(change)

    if changes:
        with open(get_path(filename, 'changes'), 'w') as f:
            json.dump(changes, f, indent=2)


def run_test_dv():
    assert len(sys.argv) >= 2, 'Not enough command line arguments'

    results, date_results = [], []
    for file in glob.glob(f'{TEST_DATA_DIR}/dataverse/data/*'):
        filename = file.split('/')[-1]
        py_path = get_path(filename)
        R_path = get_path(filename, 'R')

        if sys.argv[1] == 'diff':
            diff(filename, py_path, R_path)
            continue

        if sys.argv[1] == 'py':
            if len(sys.argv) == 3 and file != sys.argv[2]:
                continue

            start = time.time()
            runner = PreprocessRunner.load_from_file(file)
            ok = runner.success 
            if ok:
                obj = runner.result_obj
                df = obj.data_frame
            rows, cols = df.shape if ok else (0, 0)
            results.append([filename, getsize(file) / 1000000, rows, cols, time.time() - start, '' if ok else runner.err_msg])
            if not ok:
                continue

            for var, val in obj.variable_info.items():
                dtype = df[var].dtype
                vars = list(df[var][:10])
                #if val.time_val is True:
                    #date_results.append([str(x) for x in [val.time_val, dtype, var] + vars])

                if dtype == 'object':
                    result = []
                    for var in vars:
                        val = str(var).strip().lower()
                        place = ''
                        if len(val) >= 2 and val != 'yes':
                            try:
                                place = pycountry.subdivisions.lookup(val).type
                            except:
                                try:
                                    place = pycountry.countries.lookup(val) and 'Country'
                                except:
                                    pass
                        result.append((var, place))

                    date_results.append(result)

            jstring = obj.get_final_json(indent=4)
            open(py_path, 'w').write(jstring)
            continue

        cmd = f'Rscript ../../rscripts/runPreprocess.R "{file}" ../../rscripts/'
        result = subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE)
        obj = json.loads(result.stdout.decode('utf8').split('---START-PREPROCESS-JSON---')[1].split('---END-PREPROCESS-JSON---')[0])

        with open(R_path, 'w') as f:
            json.dump(obj, f)

    with open(get_path('results.csv'), 'w') as f:
        w = csv.writer(f)
        w.writerow('file size rows cols time error'.split())
        w.writerows(results)

    with open(get_path('date_results.csv'), 'w') as f:
        w = csv.writer(f)
        w.writerows(date_results)

if __name__ == '__main__':
    run_test_dv()
