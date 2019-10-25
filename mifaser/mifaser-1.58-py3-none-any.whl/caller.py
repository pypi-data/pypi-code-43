import os
import subprocess
import shutil
import multiprocessing
import time
from . import alignment
from .annotation import analysis, annotate, mapping
from .translate import peptideBreak2


def log(msg, quiet, msgstack=list()):
    if not quiet:
        print(msg)
    else:
        msgstack.append(('{:23s}'.format(f'[{time.time()}]'), msg))


def main(inputfile, outputfolder, databasefolder, diamondfolder, read_mapping=False,
         cpu_limit=None, multithreading=0, threadid=None, threadlock=None, quiet=False):
    """Runs mifaser pipeline; is called by mifaser.py"""

    msgstack = []
    err_msgs = []

    quiet_flag = quiet
    if multithreading > 1:
        quiet = True

    if not quiet:
        log(f"  * Starting {threadid} ({os.path.basename(inputfile)})", quiet, msgstack)

    cpu_available = multiprocessing.cpu_count()
    if cpu_limit:
        cpu_count = min(cpu_limit, cpu_available)
    else:
        cpu_count = cpu_available

    if multithreading:
        cpu_count = min(cpu_count, int(cpu_count/multithreading))
    if not cpu_count:
        cpu_count = 1

    log(f"   - [{threadid}] running on [{cpu_count:d}/{cpu_available:d}] CPUs", quiet, msgstack)

    read_file = os.path.splitext(os.path.basename(inputfile))[0]

    # paths
    path_to_peptide_file = os.path.join(outputfolder, "peptide/")
    path_to_diamond_result = os.path.join(outputfolder, "diamond/")
    path_to_parse_result = os.path.join(outputfolder, "parsed/")
    path_to_analyze_result = os.path.join(outputfolder, "analyzed/")
    path_to_readmap_dir = os.path.join(path_to_analyze_result, 'read_map')
    path_to_database_ec_file = os.path.join(databasefolder, "ec_mapping.tsv")
    path_to_database_ec_annotation_file = os.path.join(databasefolder, "ec_annotation.tsv")
    diamond_binary = os.path.join(diamondfolder, 'diamond')
    database_file = os.path.join(databasefolder, "database.dmnd")
    err_log = os.path.join(path_to_analyze_result, 'mifaser.err')
    msg_log = os.path.join(path_to_analyze_result, 'mifaser.log')

    log("     Creating output directories...", quiet, msgstack)
    if not os.path.exists(outputfolder):
        os.mkdir(outputfolder)
    if not os.path.exists(path_to_peptide_file):
        os.mkdir(path_to_peptide_file)
    if not os.path.exists(path_to_diamond_result):
        os.mkdir(path_to_diamond_result)
    if not os.path.exists(path_to_parse_result):
        os.mkdir(path_to_parse_result)
    if os.path.exists(path_to_analyze_result):
        shutil.rmtree(path_to_analyze_result)
    os.mkdir(path_to_analyze_result)

    # processing flags
    abort = False

    # translate reads
    do_translate = True
    if do_translate:
        log("     Translating reads...", quiet, msgstack)
        try:
            peptideBreak2.main(read_file, inputfile, path_to_peptide_file)
        except Exception as err:
            log('     ERROR#0 - Translation failed. Error: %s' % err, quiet, err_msgs)
            abort = True

    # assert successfull translation
    prd_file = '%s%s.prd' % (path_to_peptide_file, read_file)
    if not os.path.exists(prd_file):
        abort = True
        log('     ERROR#1 - No translated peptide file found. Aborting.', quiet, err_msgs)
    else:
        with open(prd_file) as peptide_file:
            first = peptide_file.read(1)
            if not first:
                abort = True
                log('     ERROR#2 - Translated peptide file is empty. Aborting.', quiet, err_msgs)

    if not abort:
        # run DIAMOND with the tranlslated peptide file
        log("     Running DIAMOND...", quiet, msgstack)
        cmd_list = [
                    diamond_binary, "blastp",
                    "-p", str(cpu_count),
                    "-q", f"{path_to_peptide_file}{read_file}.prd",
                    "-d", database_file,
                    "-k", "1000000",
                    "--min-score", "10",
                    "--freq-sd", "200",
                    "-a", f"{path_to_diamond_result}{read_file}",
                    "--quiet"
        ]
        sp = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _out, err = sp.communicate()
        if err:
            log("     ERROR#3 - [DIAMOND] %s" % err.rstrip().decode('utf8'), quiet, err_msgs)
            abort = True

    if not abort:
        # convert DIAMOND result from .daa to .tab
        log("     Converting DIAMOND...", quiet, msgstack)
        cmd_list = [
                    diamond_binary, "view",
                    "-p", str(cpu_count),
                    "-a", f"{path_to_diamond_result}{read_file}.daa",
                    "-o", f"{path_to_diamond_result}{read_file}.out",
                    "-f", "tab",
                    "--quiet"
        ]
        sp = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _out, err = sp.communicate()
        if err:
                log("     ERROR#4 - [DIAMOND]  %s" % err.rstrip().decode('utf8'), quiet, err_msgs)
                abort = True

    if not abort:
        # parse the DIAMOND result
        log("     Parsing DIAMOND...", quiet, msgstack)
        try:

            alignment.main(read_file, path_to_diamond_result, path_to_parse_result)
        except Exception as err:
            log("     ERROR#5 - [DIAMOND] %s" % repr(err).rstrip(), quiet, err_msgs)
            abort = True

    if not abort:
        # Annotate parsed result with ECs.
        log("     Annotating...", quiet, msgstack)
        try:
            annotate.main(read_file, path_to_parse_result, path_to_database_ec_file, path_to_analyze_result)
        except Exception as err:
                log("     ERROR#6 - [Annotate] %s" % repr(err).rstrip(), quiet, err_msgs)
                abort = True
    else:
        open(os.path.join(path_to_analyze_result, 'ec_count.tsv'), 'a').close()

    if not abort:
        # Analysis the data, exclude multiEC and get final EC, read_count table.
        log("     Analyzing...", quiet, msgstack)
        try:
            analysis.main(read_file, path_to_analyze_result, path_to_database_ec_annotation_file)
        except Exception as err:
                log("     ERROR#7 - [Analysis] %s" % repr(err).rstrip(), quiet, err_msgs)
                abort = True
    else:
        with open(os.path.join(path_to_analyze_result, 'analysis.tsv'), 'w') as analysis_out:
            analysis_out.write('0\t0\n')
        open(os.path.join(path_to_analyze_result, 'multi_ec.tsv'), 'a').close()

    if read_mapping:
        if not abort:
            # Generate a multi-fasta file of reads that are mapped to the ECs
            log("     Create read mapping...", quiet, msgstack)
            try:
                mapping.main(path_to_analyze_result, inputfile)
            except Exception as err:
                    log("     ERROR#8 - [Readmap] %s" % repr(err).rstrip(), quiet, err_msgs)
                    abort = True
        else:
            os.mkdir(path_to_readmap_dir)

    if abort:
        with open(err_log, "w") as mifaser_err:
            if quiet:
                mifaser_err.writelines(f"{t} [{threadid}] {l}\n" for t, l in err_msgs)
            else:
                mifaser_err.writelines(f"[{threadid}] {l}\n" for t, l in err_msgs)
        log(f" >>> [{threadid}] ERROR. logs: %s" % err_log, quiet, msgstack)
    else:
        log(f"   - [{threadid}] finished", quiet, msgstack)

    if quiet and quiet_flag:
        with open(msg_log, "w") as mifaser_log:
            if quiet:
                mifaser_log.writelines(f"{t}      [{threadid}] {l}\n" for t, l in msgstack)
            else:
                mifaser_log.writelines(f"     [{threadid}] {l}\n" for t, l in msgstack)
    else:
        if multithreading:
            threadlock.acquire()
        if msgstack:
            print('\n'.join(f"{l}" for t, l in msgstack))
        if multithreading:
            threadlock.release()
