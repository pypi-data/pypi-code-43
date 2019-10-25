import os
import sys
import shutil
import argparse
import datetime
from pathlib import Path
from . import run, __version__, __releasedate__


QUIET = False


def log(msg, log_file, ts=False):
    if not QUIET:
        print(msg)
    else:
        with open(log_file, 'a') as log_file_fh:
            ts_formatted = '{:23s}'.format(f'[{datetime.datetime.now().timestamp()}]') if ts else ''
            log_file_fh.write(f"{ts_formatted} {msg}\n")


def verify_outputfolder(outputfolder, inputfiles, output_path):
    if not outputfolder:
        if len(inputfiles) == 1:
            file_name = os.path.splitext(os.path.basename(inputfiles[0]))[0]
        elif len(inputfiles) == 2:
            file_name = '{0}_{1}'.format(os.path.splitext(os.path.basename(inputfiles[0]))[0],
                                        os.path.splitext(os.path.basename(inputfiles[1]))[0])
        else:
            file_name = '{0}_multiple'.format(os.path.splitext(os.path.basename(inputfiles[0]))[0])
        invalid_chars = r'<>\/|:*?"'
        outputfolder_verified = ''.join(c for c in f'{file_name}_out'  if c not in invalid_chars)
        outputfolder_verified = outputfolder_verified.replace(' ','_')
    else:
        outputfolder_verified = outputfolder
    if output_path:
        outputfolder_verified = os.path.join(output_path, outputfolder_verified)
    if not os.path.exists(outputfolder_verified):
        os.makedirs(outputfolder_verified)
    return outputfolder_verified


def check_diamond(diamondfolder, exit_on_fail=True):
    diamond_bin = os.path.join(diamondfolder, 'diamond')
    diamond_version = None
    if not os.path.exists(diamond_bin):
        print(f"ERROR: Missing diamond binary: {diamond_bin}")
        if exit_on_fail:
            exit_with_diamond_fail()
    else:
        diamond_output = '\n'.join(run.run_command([diamond_bin, '--version'], print_output=False))
        if not diamond_output.startswith('diamond version '):
            print(f'ERROR: Could not run: $> {diamond_bin}')
            if diamond_output.startswith('FATAL: kernel too old'):
                print(f'To download and compile the latest version of DIAMOND run: '
                      f'{os.path.join(diamondfolder, "update.sh")}\n'
                      f'Alternatively visit https://github.com/bbuchfink/diamond/releases '
                      f'to download any pre-compiled version and replace your local version in {diamondfolder}')
            if exit_on_fail:
                exit_with_diamond_fail()
        else:
            diamond_version = diamond_output[16:]
    return diamond_version


def check_diamond_db(diamondfolder, databasefolder, exit_on_fail=True):
    diamond_bin = os.path.join(diamondfolder, 'diamond')
    diamond_db = os.path.join(databasefolder, 'database.dmnd')
    diamond_db_details, diamond_binary_build = None, None
    if not os.path.exists(diamond_db):
        print(f"ERROR: Missing DIAMOND database: {diamond_db}")
        if exit_on_fail:
            exit_with_diamond_fail()
    else:
        diamond_db_output_list = run.run_command([diamond_bin, 'dbinfo', '--db', diamond_db], print_output=False)
        if not diamond_db_output_list:
            print(f'ERROR: DIAMOND database corrupted: {diamond_db}')
            if exit_on_fail:
                exit_with_diamond_fail()
        elif not diamond_db_output_list[0].startswith('diamond v'):
            print(f'ERROR: could not retrieve database version: {diamond_db} - details: {";".join(str(i) for i in diamond_db_output_list)}')
            if exit_on_fail:
                exit_with_diamond_fail()
        else:
            _diamond_binary_version, diamond_binary_build = diamond_db_output_list[0][9:].split(' ')[0].rsplit(".", 1)
            diamond_db_details = {}
            for line in diamond_db_output_list[1:]:
                if line.find('=') != -1:
                    key, val = line.split('=')
                    diamond_db_details[key.strip()] = val.strip()
            if 'Diamond build' not in diamond_db_details.keys():
                print(f'ERROR: could not retrieve specific "Diamond build": '
                      f'{diamond_db} - details: {";".join(str(i) for i in diamond_db_output_list)}')
                if exit_on_fail:
                    exit_with_diamond_fail()
    return diamond_db_details, diamond_binary_build


def update_diamond(diamondfolder, databasefolder, version=None):
    from urllib.request import Request, urlopen, urlretrieve
    from urllib.error import HTTPError, URLError
    import json
    import zipfile

    diamond_binary = os.path.join(diamondfolder, 'diamond')
    diamond_binary_version = None
    if os.path.exists(diamond_binary):
        diamond_binary_version = check_diamond(diamondfolder, exit_on_fail=False)
    if diamond_binary_version:
        print(f"Current version of DIAMOND: {diamond_binary_version}")
    else:
        diamond_binary_version = '_unknown'
    diamond_build_db_version = diamond_binary_version

    if version:
        print(f"Specified version of DIAMOND: {version}")
        diamond_download = version
    else:
        print("Checking latest DIAMOND release...")
        req = Request('https://api.github.com/repos/bbuchfink/diamond/releases/latest')
        try:
            connection_error = False
            response = urlopen(req)
        except HTTPError as e:
            if hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
            connection_error = True
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            connection_error = True
        if connection_error:
            sys.exit(1)
        else:
            response_json = json.loads(response.read().decode("utf-8"))
            diamond_download = response_json['tag_name'][1:]

    if diamond_binary_version == diamond_download:
        if version:
            print("Local DIAMOND is same as specified version!")
        else:
            print("Local DIAMOND is already latest release!")
    else:
        print(f"Downloading DIAMOND v{diamond_download}...")
        diamond_download_archive = os.path.join(diamondfolder, f'v{diamond_download}.zip')
        urlretrieve(
            f'https://github.com/bbuchfink/diamond/archive/v{diamond_download}.zip',
            diamond_download_archive
        )

        if os.path.exists(diamond_binary):
            print(f"Renaming current DIAMOND binary to diamond_v{diamond_binary_version}")
            os.rename(
                diamond_binary,
                os.path.join(diamondfolder, f'diamond_v{diamond_binary_version}')
            )

        print(f"Building DIAMOND {diamond_download}...")
        diamond_src_zip = zipfile.ZipFile(diamond_download_archive)
        diamond_src_zip.extractall(diamondfolder)
        diamond_src_zip.close()
        diamond_unzipped_folder = os.path.join(diamondfolder, f'diamond-{diamond_download}')
        os.chmod(os.path.join(diamond_unzipped_folder, 'build_simple.sh'), 0o755)
        cmd_build = f'cd {diamond_unzipped_folder}; ./build_simple.sh; mv diamond {diamondfolder}/;'
        run.run_command(cmd_build, shell=True)
        shutil.rmtree(diamond_unzipped_folder, ignore_errors=True)
        if os.path.exists(diamond_download_archive):
            os.remove(diamond_download_archive)

        if not os.path.exists(diamond_binary) or not check_diamond(diamondfolder, exit_on_fail=False):
            sys.exit(f"ERROR: DIAMOND build failed.")
        else:
            diamond_build_db_version = diamond_download
            print(f"DIAMOND binary updated: {diamond_binary_version} -> {diamond_download}")

    diamond_db_details, diamond_binary_build = check_diamond_db(diamondfolder, databasefolder, exit_on_fail=False)
    if diamond_db_details and 'Diamond build' in diamond_db_details.keys():
        diamond_db_build = diamond_db_details['Diamond build']
        if diamond_db_build != diamond_binary_build:
            print(f'DIAMOND binary and database not compatible: '
                  f'binary [{diamond_binary_build}] <> database: [{diamond_db_build}]')
            db_name = os.path.basename(os.path.dirname(databasefolder))
            database_file = os.path.join(databasefolder, 'database.dmnd')
            if os.path.exists(database_file):
                print(f"Renaming current {db_name} database to database_v{diamond_binary_version}.dmnd")
                os.rename(
                    database_file,
                    os.path.join(databasefolder, f'database_v{diamond_binary_version}.dmnd')
                )

            create_diamond_db(diamondfolder, databasefolder)

            print(f"DIAMOND database updated: "
                  f"{diamond_binary_version}.{diamond_db_build} -> {diamond_build_db_version}.{diamond_binary_build}")


def create_diamond_db(diamondfolder, databasefolder):
    diamond_binary = os.path.join(diamondfolder, 'diamond')
    database_file = os.path.join(databasefolder, 'database.dmnd')
    print("Building DIAMOND database...")
    cmd_build_db = f'{diamond_binary} makedb --in {os.path.join(databasefolder, "sequences.fasta")} ' \
                   f'--db {os.path.join(databasefolder, "database")}'
    run.run_command(cmd_build_db, shell=True)
    if not os.path.exists(database_file):
        sys.exit(f"ERROR: DIAMOND database build failed.")
    return database_file


def exit_with_diamond_fail():
    sys.exit(
        '\nUse "-n/--no-check" to skip compatibility checks.\n'
        'Use "-u/--update diamond[:version]" to compile DIAMOND from source and rebuild the database.\n'
    )


def create_reference_database(diamondfolder, mifaser_base, db_name, src_fasta,
                              merge_with_db=None, update_ec_annotations=False):
    """
    The db_base is expected to have:
    sequences.fasta, ec_mapping.tsv and ec_annotation.tsv;
    The input file is expected to be a fasta file, the header should follow the pattern:
    >id|annotation|EC|organism|[source1]|[source2]|...
    The id is expected to be uniprot id.
    """
    from .external import seguid

    db_base = os.path.join(os.path.join(mifaser_base, 'database'), db_name)
    db_fasta = os.path.join(db_base, "sequences.fasta")
    db_ec_annotations = os.path.join(db_base, "ec_annotation.tsv")
    db_ec_mappings = os.path.join(db_base, "ec_mapping.tsv")

    db_annotation = {}
    db_mapping = {}
    seguid2records = {}

    # parse existing database
    if merge_with_db:

        db_merge_base = os.path.join(os.path.join(mifaser_base, 'database'), merge_with_db)
        if not os.path.exists(db_merge_base):
            print(f"ERROR: Database {merge_with_db} [{db_merge_base}] does not exist.")
            return

        # parse ec annotations
        db_merge_annotations = os.path.join(db_merge_base, "ec_annotation.tsv")
        with open(db_merge_annotations, "r") as fhi:
            for line in fhi:
                line = str.strip(line)
                ec, annotation = line.split("\t")
                db_annotation[ec] = annotation

        # parse ec mappings
        db_merge_mappings = os.path.join(db_merge_base, "ec_mapping.tsv")
        with open(db_merge_mappings, "r") as fhi:
            for line in fhi:
                line = str.strip(line)
                m_id, ec = line.split("\t")
                db_mapping[m_id] = ec

        # parse sequences
        db_merge_fasta = os.path.join(db_merge_base, "sequences.fasta")
        for header, sequence in run.parse_fasta(db_merge_fasta).items():
            seguid2records[seguid(sequence)] = (header, sequence)

    # parse sequences, while checking potential merging conflicts
    for header, sequence in run.parse_fasta(src_fasta).items():
        title_list = header.split("|")
        record_id = title_list[0]
        record_annotation = title_list[1]
        record_ec = title_list[2]

        if record_id in db_mapping.keys():
            print(f"WARN: The uniprot id {record_id} already exists in the current database, "
                  f"or was already processed - skipped")
            continue

        seguid = seguid(sequence)

        if seguid in seguid2records.keys():
            print(f"WARN: Identical sequence for {header} already exists in the current database, "
                  f"or was already processed - skipped")
            continue
        if not update_ec_annotations and \
                record_ec in db_annotation.keys() and db_annotation[record_ec] != record_annotation:
            seguid2records[seguid] = (header, sequence)
            db_mapping[record_id] = record_ec
            print(f"WARN: E.C. {record_ec} : new annotation differs from the current database, "
                  f"or from sequences already processed - sequence added ignoring new E.C. annotation")
            # print (db_annotation[record_ec], " <<< --- >>> ", record_annotation)
            continue
        seguid2records[seguid] = (header, sequence)
        db_annotation[record_ec] = record_annotation
        db_mapping[record_id] = record_ec

    if not os.path.exists(db_base):
        os.mkdir(db_base)

    with open(db_fasta, "w") as fho:
        for seguid, record in seguid2records.items():
            fho.write(f">{record[0]}\n{record[1]}\n")

    with open(db_ec_annotations, "w") as fho:
        for record_ec in sorted(db_annotation.keys(), key=run.ec_numbers):
            fho.write(f"{record_ec}\t{db_annotation[record_ec]}\n")

    with open(db_ec_mappings, "w") as fho:
        for record_id in sorted(db_mapping.keys()):
            fho.write(f"{record_id}\t{db_mapping[record_id]}\n")

    create_diamond_db(diamondfolder, db_base)


def bionode_run():
    raise NotImplementedError()


def bionode_run_file(input_path, output_path, id):
    args = parse_arguments()
    inputfiles_lookup = [ Path(input_path) / "in_1.fasta", Path(input_path) / "in_2.fasta" ]
    inputfiles = [ str(f) for f in inputfiles_lookup if f.exists() ]
    main(inputfiles, output_path, args.databasefolder, args.diamondfolder, args.mapping,
         args.split, args.splitmb, args.threads, args.cpu, args.preserve, args.no_check, args.quiet)
    return f"processed {id} -> {inputfiles}"


def main(inputfiles, outputfolder, databasefolder, diamondfolder, read_mapping,
         splitsize, split_mb, max_threads, cpu_max, preserve, no_check, quiet):
    global QUIET
    QUIET = quiet

    if split_mb:
        splitsize = split_mb
        run.FLAGS.append("split_mb")

    input_path = os.environ.get("INPUT_PATH")    
    output_path = os.environ.get("OUTPUT_PATH")

    outputfolder = verify_outputfolder(outputfolder, inputfiles, output_path)

    if run.is_download(inputfiles):
        inputfiles = run.download_inputfiles(inputfiles, outputfolder)
    elif input_path:
        inputfiles = [os.path.join(input_path, in_) for in_ in inputfiles]

    log_file = os.path.join(outputfolder, 'mifaser.log')
    if os.path.exists(log_file):
        os.remove(log_file)
    err_logs = os.path.join(outputfolder, 'mifaser.err')
    if os.path.exists(err_logs):
        os.remove(err_logs)

    log(f"\n --- mi-faser {__version__} ({__releasedate__}) ---", log_file)

    diamond_binary_version = check_diamond(diamondfolder)
    log(f"   - [ DIAMOND v{diamond_binary_version} ] -", log_file)
    if not no_check:
        diamond_db_details, diamond_binary_build = check_diamond_db(diamondfolder, databasefolder)
        diamond_db_build = diamond_db_details['Diamond build']
        if diamond_db_build != diamond_binary_build:
            sys.exit(
                f'ERROR: DIAMOND binary and database not compatible: '
                f'binary [{diamond_binary_build}] <> database: [{diamond_db_build}]'
            )
        db_name = os.path.basename(os.path.dirname(databasefolder))
        db_seqcount = diamond_db_details['Sequences']
        log(f"   - [ Database:{db_name} build:{diamond_db_build} Sequences:{db_seqcount} ] -", log_file)
    log("", log_file)

    start = datetime.datetime.now()

    if cpu_max and cpu_max < 1:
        cpu_limit = 1
    else:
        cpu_limit = cpu_max

    splits_folder = os.path.join(outputfolder, 'splits')

    log(f" *** Running mifaser with up to {max_threads} parallel thread(s)", log_file, ts=True)
    splits, has_error = run.run_standalone(inputfiles, splitsize, splits_folder,
                                            diamondfolder, databasefolder, read_mapping,
                                            cpu_limit, max_threads, quiet, wait=True)

    if has_error:
        log(f" !>> ERROR: Attempting post-processing of any valid results", log_file, ts=True)
    else:
        log(f" *** Post-processing...", log_file, ts=True)
    post_success, _merged_result, _merged_stats, _missing_joblist = run.postprocess_results(
        splits, splits_folder, outputfolder, quiet=quiet)
    log(f" *** Results saved to: {os.path.abspath(outputfolder)}", log_file, ts=True)
    if not post_success or has_error:
        end = datetime.datetime.now()
        delta = end - start
        log(f"\n --- exited with errors after {str(delta)} --- \n", log_file)
        sys.exit(1)

    if not preserve and os.path.exists(splits_folder):
        log(f" *** Removing intermediate files", log_file, ts=True)
        shutil.rmtree(splits_folder)

    end = datetime.datetime.now()
    delta = end - start
    log(f"\n --- finished in {str(delta)} --- \n", log_file)


def parse_arguments():
    platform_ = 'na'
    if sys.platform == "linux" or sys.platform == "linux2":
        platform_ = 'linux'
    elif sys.platform == "darwin":
        platform_ = 'osx'
    elif sys.platform == "win32" or sys.platform == "win64":
        platform_ = 'win'

    mifaser_base = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser(
        prog="mifaser",
        description="mi-faser, microbiome - functional annotation of sequencing reads\n \n" \
            + "a super-fast ( < 10min/10GB of reads ) and accurate ( > 90% precision ) method\n" \
            + "for annotation of molecular functionality encoded in sequencing read data\n" \
            + "without the need for assembly or gene finding.\n \n"
            + "Public web service: https://services.bromberglab.org/mifaser\n \n" \
            + "Version: %s [%s]\n" % (__version__, __releasedate__),
        epilog="If you use *mi-faser* in published research, please cite:\n \n" \
            + "Zhu, C., Miller, M., ... Bromberg, Y. (2017).\n" \
            + "Functional sequencing read annotation for high precision microbiome analysis.\n" \
            + "Nucleic Acids Res. [doi:10.1093/nar/gkx1209]\n" \
            + "(https://academic.oup.com/nar/advance-article/doi/10.1093/nar/gkx1209/4670955)\n \n" \
            + "mi-faser is developed by Chengsheng Zhu and Maximilian Miller.\n" \
            + "Feel free to contact us for support at services@bromberglab.org.\n \n" \
        "This project is licensed under [NPOSL-3.0](http://opensource.org/licenses/NPOSL-3.0)\n \n" \
            + "Test: mifaser -f mifaser/files/test/artificial_mg.fasta -o mifaser/files/test/out\n \n",
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    parser.add_argument('-f', '--inputfile',
                        help="input DNA reads file, http[s]/ftp[s] url or SRA accession id (sra:<id>)")
    parser.add_argument('-l', '--lanes', action='append', nargs=2,
                        metavar=('R1', 'R2'), help="2-Lane format (R1/R2) files, http[s]/ftp[s] url or "
                                                   "SRA accession ids (sra:<id_1> sra:<id_2>)")
    parser.add_argument('-o', '--outputfolder',
                        help="path to base output folder; default: INPUTFILE_out")
    parser.add_argument('-d', '--databasefolder', default='GS',
                        help="name of database located in database/ directory "
                             "OR absolute path to folder containing database files")
    parser.add_argument('-i', '--diamondfolder', default=os.path.join(
                                                            mifaser_base, os.path.join('diamond', platform_)
                                                        ),
                        help="path to folder containing diamond binary")
    parser.add_argument('-m', '--mapping', action='store_true',
                        help="if flag is set all reads mappings will be generated (reads{n=*} -> EC{n=1}, fasta)")
    parser.add_argument('-s', '--split', default=100000, type=int,
                        help="split by X sequences; default: 100k; 0 forces no split")
    parser.add_argument('-S', '--splitmb', nargs='?', const=25, type=int,
                        help="split by X MB; default: 25;  (requires split from GNU Coreutils)")
    parser.add_argument('-t', '--threads', default=1, type=int,
                        help="number of threads; default: 1")
    parser.add_argument('-c', '--cpu', type=int,
                        help="max cpus per thread; default: all available")
    parser.add_argument('-p', '--preserve', action='store_true',
                        help="if flag is set intermediate results are kept")
    parser.add_argument('-n', '--no-check', action='store_true',
                        help="if flag is set check for compatibility between diamond database and binary is omitted")
    parser.add_argument('-u', '--update', type=str,
                        help="valid update commands: { diamond[:version] }")
    parser.add_argument('-D', '--createdb', type=str, nargs="*", metavar="arg",
                        help="create new reference database: <db_name> <db_sequences.fasta> "
                             "[merge_db=<name of db to merge with>] [update_ec_annotations=<1|0>; default: 0]")
    parser.add_argument('-v', '--version', action='store_true',
                        help="print mi-faser version")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="if flag is set console output is logged to file")

    args = parser.parse_args()
    args.databasefolder = os.path.join(os.path.join(mifaser_base, 'database'), args.databasefolder)
    args.diamondfolder = os.path.abspath(args.diamondfolder)
    return args


def init():
    args = parse_arguments()
    mifaser_base = os.path.dirname(os.path.realpath(__file__))

    if args.version:
        print(f'mi-faser {__version__} ({__releasedate__})')
        sys.exit(0)

    if args.update:
        update_detail = args.update.split(":")
        update_action = update_detail[0]
        update_version = update_detail[1] if len(update_detail) == 2 else None
        if update_action.startswith('diamond'):
            update_diamond(args.diamondfolder, args.databasefolder, update_version)
        sys.exit(0)

    if args.createdb:
        nargs = len(args.createdb)
        if nargs < 2:
            print('Too few arguments: name for new database and path to fasta file containing sequences required.')
            sys.exit(2)
        db_name_ = None
        src_fasta_ = None
        merge_with_db_ = None
        update_ec_annotations_ = False
        if nargs >= 2:
            db_name_ = args.createdb[0]
            src_fasta_ = args.createdb[1]
        if nargs > 2:
            params = {}
            for arg in args.createdb[2:]:
                p, v = arg.split("=")
                params[p] = v
            if "merge_db" in params.keys():
                merge_with_db_ = params["merge_db"]
            if "update_ec_annotations" in params.keys():
                update_ec_annotations_ = True if int(params["update_ec_annotations"]) else False

        print('Creating new reference database...')
        create_reference_database(
            args.diamondfolder, mifaser_base, db_name_, src_fasta_, merge_with_db_, update_ec_annotations_
        )
        print(f'\nRun mi-faser with argument: "-d {db_name_}" to use this reference database.')
        sys.exit(0)

    if not args.inputfile and not args.lanes:
        try:
            user_input = input("Enter DNA reads file or two lane read files seperated by ',':")
            user_input_ = user_input.split(",") if user_input else []
            if len(user_input_) == 1:
                args.inputfile = user_input_[0]
            elif len(user_input_) == 2:
                args.lanes = [user_input_[0], user_input_[1]]
            else:
                sys.exit("\nAborted: Wrong format.")
        except KeyboardInterrupt:
            sys.exit("\nAborted.")
        print(f'\nRunning mi-faser with default arguments on {user_input_}')
    
    inputfiles_ = run.parse_inputfiles(args.inputfile, args.lanes)
    
    main(inputfiles_, args.outputfolder, args.databasefolder, args.diamondfolder, args.mapping,
         args.split, args.splitmb, args.threads, args.cpu, args.preserve, args.no_check, args.quiet)


if __name__ == "__main__":
    init()
