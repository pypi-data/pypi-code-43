"""
Part of the keylimepie package.

Run (multiple) LIME models in a tidy way.
"""

import os
import time, datetime
import glob
import subprocess
import tempfile

from keylimepie.model import makemodelfile as make
from keylimepie.model import combinefiles as comb
from keylimepie.model import limeclass as lime


def run_model(headerfile, moldatfile, in_system_tmp=False, **kwargs):
    """ Run a LIME Model. Check readme for possible kwargs and defaults."""

    # Start the clock to time the running of models.

    print('\n')
    t0 = time.time()
    if in_system_tmp:
        folder_name = make_unique_folder()
    else:
        folder_name = make_unique_folder(path='.')
    os.chdir(folder_name)

    # Generate a LIME Model class instance.

    model = lime.Model(headerfile, moldatfile, **kwargs)

    print()
    print('Working directory: ', os.getcwd())
    print('\nInput is in %dD-%s coordinates.' % (model.ndim, model.coordsys))
    print('Assuming a value of minScale = %.2f au.' % model.minScale)
    print('Assuming a value of radius = %.2f au.' % model.radius)

    # For each iteration, run a Model with a pause of waittime seconds.

    print('\n')
    for m in range(model.nmodels):
        print('Running Model %d of %d.' % (m + 1, model.nmodels))
        make.makeFile(m, model)
        print('Compilation... ', end='')
        try:
            compproc = subprocess.run(['keylime', '-l %d' % m, 'model_%d.c' % m], stdout=subprocess.PIPE)
        except FileNotFoundError as err:
            print("You must put keylime executable to lime folder. It is a modified lime script that divides compilation and run.")
            raise FileNotFoundError(str(err))
        print('Done!')
        cmd = compproc.stdout.decode("utf-8", "strict") + "\n"
        cmd = cmd + model.cmdprefix + ' lime_%d.x > out_%d.txt && rm lime_%d.x' % (m, m, m) + model.cmdsuffix
        if model.niceness:
            cmd = 'nice -n %d ' % model.niceness + cmd
        print("Running command:")
        print("_________________________________________________")
        print(cmd)
        print("_________________________________________________")
        os.system(cmd)
        # time.sleep(Model.waittime)
        runlist = glob.glob("./*.x")
        print("Running instances: ", len(runlist), sorted(runlist))
    time.sleep(10)
    # time.sleep(Model.waittime)

    # Make sure all the models have run.
    # Check the number of *.x files to guess how many are running.
    # If nohup_X.out contains segmentation fault, then quit.

    remaining = -1
    print('\n')
    print(glob.glob("./*.x"))
    while len(glob.glob("./*.x")) > 0:
        # print(glob.glob("./*.x"))
        nremaining = len(glob.glob("./*.x"))
        if nremaining != remaining:
            print(datetime.datetime.now(), ': Waiting on %d Model(s) to run.' % nremaining)
            remaining = nremaining
        time.sleep(10.)

        # Check for segmentation faults.
        # If the number of nohup_X.out files with 'core dumped' in them
        # equals the number of lime_$$.x files left, assumped all have quit.

        nohups = [fn for fn in os.listdir('./') if fn.startswith('nohup')]
        coresdumped = 0
        for nh in nohups:
            if 'core dumped' in open(nh).read():
                coresdumped += 1
        if coresdumped == nremaining:
            print('Found %d segmentation faults.' % coresdumped)
            break

    models_run = len([fn for fn in os.listdir('./') if fn.endswith('.fits')])
    if models_run < model.nmodels:
        print('Not all models were successfully run.')
        print('Aborting without clean-up.\n')
        return
    else:
        print('All instances complete.\n')

    # Combine the Model ensemble. Here we remove all the output grids. As they
    # all have the same name, they will just be overwritten.

    if model.oversample > 1 or model.hanning:
        comb.downsampleModels(model)
    comb.averageModels(model)
    comb.moveFiles(model, suffix='.fits')
    comb.moveGrids(model)

    # Clean up.
    os.chdir('../')
    if model.cleanup:
        print('Cleaning up temporary folders.')
        os.system('rm -rf %s' % folder_name)

    # Print the total time.
    print('Finished in %s.\n\n' % seconds2hms(time.time() - t0))

    return


def make_unique_folder(fname='lime_', path=None, temp=True):
    """Make a folder with a unique name. Use tempfile.mkdtemp by default"""
    if temp:
        return tempfile.mkdtemp(prefix=fname, dir=path)
    if path is None:
        path = '.'
    folder_template = os.path.join(path, fname)
    if not os.path.isdir(folder_template):
        os.makedirs(folder_template)
    else:
        suffix = 1
        while os.path.isdir(os.path.join(folder_template + '%d' % suffix)):
            suffix += 1
        os.makedirs(folder_template + '%d' % suffix)
    return fname


def seconds2hms(seconds):
    """Convert seconds to hours, minutes, seconds."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '%d:%02d:%02d' % (h, m, s)
