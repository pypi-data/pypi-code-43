import os
import sys
import shutil
import gzip
import csv
import threading
import time
import re
import subprocess
from . import caller
from .external import fastq_convert_fasta
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict

# threading
THREADLOCK = threading.Lock()
THREADPOOL = None

FLAGS = []
QUIET = False
ERROR_STATE = False
VALID_FILETYPES = ["fasta", "fa", "fna", "fastq", "fq"]
VALID_ARCHIVETYPES = ["zip", "bzip2", "xz", "tar", "tar.gz", "gz", "bz2"]
VALID_URLS = ("http://", "https://", "ftp://", "ftps://")


class Error(Exception):
    """Base class for other exceptions"""
    pass


class InputError(Error):
    """Raised when the input file is not valid"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


def log(msg, quiet, msgstack=list()):
    if not quiet:
        print(msg)
    else:
        ts = '{:23s}'.format(f'[{time.time()}]')
        msgstack.append(f'{ts} {msg}')


def file_len(fname):
    i = -1
    with open(fname) as f_:
        for i, _ in enumerate(f_):
            pass
    return i + 1


def is_int(x):
    try:
        int(x)
        return True
    except ValueError:
        return False


def fasta_header_count(fname):
    header_count = 0

    is_fasta, _ = check_filetype(fname, [
        "fasta", "fa", "fna",
        "fasta.gz", "fa.gz", "fna.gz",
        "fasta.tar.gz", "fa.tar.gz", "fna.tar.gz"
    ])
    is_fastq, _ = check_filetype(fname, [
        "fastq", "fq",
        "fastq.gz", "fq.gz",
        "fastq.tar.gz", "fq.tar.gz"
    ])

    if is_fasta:
        if fname.endswith('.gz'):
            zgrep = which("zgrep")
            if zgrep:
                cmd = f'{zgrep} -c -e "^>" {fname}'
                zgrep_count = run_command(cmd, shell=True, print_output=False)
                if zgrep_count:
                    zgrep_count_val = zgrep_count[0]
                    if is_int(zgrep_count_val):
                        return int(zgrep_count_val)
        else:
            with open(fname) as f_:
                for l in f_:
                    if l and l[0] == '>':
                        header_count += 1
                        next(f_, None)
    elif is_fastq:
        if fname.endswith('.gz'):
            cat = which("zcat")
        else:
            cat = which("cat")

        wc = which("wc")
        if cat and wc:
            cmd = f'{cat} {fname} | {wc} -l'
            cat_count = run_command(cmd, shell=True, print_output=False)
            if cat_count:
                cat_count_val = cat_count[0]
                if is_int(cat_count_val):
                    return int(cat_count_val)/4

    return header_count


def rgb(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    if minimum == maximum:
        maximum = minimum + 1
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b = int(max(0, 255 * (1 - ratio)))
    r = int(max(0, 255 * (ratio - 1)))
    g = 255 - b - r
    return r, g, b


def get_color_coding(ec_readcount_list):
    readcounts = ec_readcount_list.values()
    if readcounts:
        minimum = min(readcounts)
        maximum = max(readcounts)
    else:
        minimum = 0
        maximum = 0
    colors = {}

    for ec, readcount in ec_readcount_list.items():
        color = rgb(minimum, maximum, readcount)
        colors[ec] = color
    return colors


def run_command(command, shell=False, print_output=True, env_exports={}):
    current_env = os.environ.copy()
    merged_env = {**current_env, **env_exports}
    process = subprocess.Popen(command, shell=shell, env=merged_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = []
    for line in iter(process.stdout.readline, b''):
        line = line.rstrip().decode('utf8')
        if print_output:
            print(">>>", line)
        output.append(line)
    return output


def which(program):
    def is_exe(file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def runningInDocker():
    cgroup = '/proc/self/cgroup'
    if os.path.exists(cgroup):
        with open(cgroup, 'r') as procfile:
            for line in procfile:
                fields = line.strip().split('/')
                if fields[1] == 'docker':
                    return True
    return False


def create_markdown(src_files, other_files=['files/css/stylesheet.css'], out_file=None, src="markdown", to="pdf", api_url="http://c.docverter.com/convert"):
    if not isinstance(src_files, (list, tuple)):
        src_files = [src_files]
    cmd = [
        'curl', '--form', f'from={src}', '--form',
        f'to={to}', '--form', 'css=stylesheet.css'
    ]
    cmd += [f'--form input_files[]=@{f}' for f in src_files]
    cmd += [f'--form other_files[]=@{f}' for f in other_files]
    if not out_file:
        out_file = f'out.{to}'
    cmd += ['--output', out_file]
    cmd += [api_url]
    run_command(cmd)
    return out_file


def parse_fasta(fasta_in):
    records = {}
    with open(fasta_in, 'r') as fin:
        header, sequence = None,  ''
        for line in fin:
            line = line.strip()
            if line:
                if line[0] == '>':
                    if sequence:
                        records[header] = sequence
                        sequence = ''
                    header = line[1:]
                else:
                    sequence += line

            if sequence:
                next_line = next(fin, None)
                if next_line is None:
                    records[header] = sequence
                else:
                    next_line = next_line.strip()
                    if next_line:
                        if next_line[0] == '>':
                            records[header] = sequence
                            sequence = ''
                            header = next_line[1:]
                        else:
                            sequence += next_line
    return records


def split_by_length(fastafile, outfolder, splitlength, diamondfolder, databasefolder, read_mapping,
                    cpu_limit, max_threads, method, threadpool=None):
    default_separator = '_'
    prefix = ''
    separator = ''

    split_idx = 1
    out_files = []
    total_splitted = 0
    input_file = open(fastafile, 'r')
    split_out_base = outfolder
    if prefix:
        split_out_base = os.path.join(split_out_base, prefix)
    else:
        split_out_base = os.path.join(split_out_base, os.path.splitext(os.path.basename(fastafile))[0])
    if separator:
        split_out_base += separator
    else:
        split_out_base += default_separator

    reading = True
    skip = False
    while reading:
        first = True
        split_out_filename = "%s%s.fasta" % (split_out_base, split_idx)
        with open(split_out_filename, 'w') as output_file:
            out_files.append(split_out_filename)
            current_splitted = 0
            while current_splitted < splitlength:
                line = input_file.readline()
                while not line.strip():
                    line = input_file.readline()
                    if len(line) == 0:
                        break
                header = line
                current_splitted += 1
                sequence = input_file.readline().rstrip()
                if not header.rstrip() and not sequence:
                    reading = False
                    if first:
                        os.remove(split_out_filename)
                        split_idx -= 1
                        out_files.pop(-1)
                        skip = True
                    break
                last_pos = input_file.tell()
                line = input_file.readline().rstrip()
                while line and line[0] != '>':
                    sequence += line
                    last_pos = input_file.tell()
                    line = input_file.readline().rstrip()
                if line and line[0] == '>':
                    input_file.seek(last_pos)
                output_file.write(header + sequence + "\n")
                total_splitted += 1
                first = False
        if not skip:
            if not threadpool:
                THREADPOOL.submit(method, split_out_filename, split_idx, max_threads, cpu_limit,
                                  outfolder, diamondfolder, databasefolder, read_mapping)
            else:
                threadpool.submit(method.process_split_server, split_out_filename, (len(out_files), total_splitted), last=False)
        split_idx += 1
    if threadpool:
        threadpool.submit(method.process_split_server, None, (len(out_files), total_splitted), last=True)
    return out_files, total_splitted


def split_by_size(fastafile, outfolder, split_size_mb, read_count, diamondfolder, databasefolder, read_mapping,
                  cpu_limit, max_threads, method, threadpool=None):
    default_separator = '_'
    separator = ''
    prefix = ''
    suffix = '.fasta'
    suffix_id_len = 4

    if prefix:
        split_out_prefix = prefix
    else:
        split_out_prefix = os.path.splitext(os.path.basename(fastafile))[0]
    if separator:
        split_out_prefix += separator
    else:
        split_out_prefix += default_separator
    split_out_base = os.path.join(outfolder, split_out_prefix)

    split_cmd = which("split")
    if not split_cmd:
        sys.exit("ERROR - Command not found: split (GNU Coreutils)")
    cmd = f'{split_cmd} -d -C {split_size_mb}M -a {suffix_id_len} --additional-suffix "{suffix}" ' \
          f'{fastafile} {split_out_base}'
    run_command(cmd, shell=True)
    all_splits = find_in_dir_pattern(outfolder, f'{split_out_prefix}[0-9]+{re.escape(suffix)}$')
    out_files = []
    for split_id in range(len(all_splits)):
        out_files.append(f'{split_out_base}{split_id:0>{suffix_id_len}}.fasta')
    # trim splits
    total = len(out_files)
    for current in range(total):
        current_split = out_files[current]
        following = current + 1
        if following != total:
            following_split = out_files[following]
            trim = []
            with open(following_split, 'r+') as f:
                start = f.tell()
                for line in iter(f.readline, ''):
                    if line == "":
                        break
                    if line[0] == ">":
                        f.seek(start)
                        break
                    else:
                        trim.append(line)
                    start = f.tell()
                data = f.read()
                f.seek(0)
                f.write(data)
                f.truncate()
            with open(current_split, 'a') as f:
                f.writelines(trim)
            current += 1
        # add to threadpool
        if not threadpool:
            THREADPOOL.submit(method, current_split, current, max_threads, cpu_limit,
                              outfolder, diamondfolder, databasefolder, read_mapping)
        else:
            threadpool.submit(method.process_split_server, current_split, (len(out_files), read_count), last=False)

    if threadpool:
        threadpool.submit(method.process_split_server, None, (len(out_files), read_count), last=True)

    return out_files


def find_in_dir_pattern(root_dir, pattern):
    p = re.compile(pattern)
    found_files = []
    for root, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename[0] == '.':
                continue
            if re.search(p, filename):
                found_files.append(os.path.join(root, filename))
    return found_files


def find_in_dir(root_dir, extensions=None, correct=False):
    found_files = []
    for root, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename[0] == '.':
                continue
            file = os.path.join(root, filename)
            valid, filename_corrected = check_filetype(filename, extensions, correct)
            if valid:
                if filename_corrected:
                    file_old = file
                    file = os.path.join(root, filename_corrected)
                    os.rename(file_old, file)
                found_files.append(file)
    return found_files


def check_filetype(filename, extensions=None, correct=False):
    valid = False
    filename_corrected = None
    if not extensions:
        valid = True
    else:
        for ext in extensions:
            if filename.endswith(f'.{ext}'):
                valid = True
                return valid, filename_corrected
        if correct:
            for ext in extensions:
                if ext in filename:
                    filename_corrected = f'{filename}.corrected.{ext}'
                    valid = True
                    return valid, filename_corrected
    return valid, filename_corrected


def check_valid_input(file_name):
    for file_type in VALID_FILETYPES:
        if file_name.endswith(file_type):
            return True
    for archive_type in VALID_ARCHIVETYPES:
        if file_name.endswith(archive_type):
            return True
    return False


def ec_numbers(ec):
    return [int(_.replace('n', '')) for _ in ec[0].split(".")]


def is_download(inputfiles):
    if inputfiles:
        for inputfile in inputfiles:
            if inputfile.startswith(VALID_URLS) or inputfile.startswith("sra:"):
                return True
    return False


def download_url(url, file_name=None, out_folder=None):
    import ssl
    import http
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    if not file_name:
        file_name = url.rsplit('/', 1)[-1]
        if not check_valid_input(file_name):
            return None

    if out_folder:
        if not os.path.exists(out_folder):
            os.makedirs(out_folder, exist_ok=True)
        file_name_path = os.path.join(out_folder, file_name)
    else:
        file_name_path = file_name
    try:
        connection_error = False
        print(f'[ urllib ] Retrieving {file_name}...', end='', flush=True)
        with urlopen(url, context=ctx) as u, open(file_name_path, 'wb') as f:
            f.write(u.read())
        print(' done')
    except http.client.IncompleteRead as e:
        print(' canceled')
        print(f"ERROR: Potential incomplete read ({len(e.partial)} bytes read) from url: {url}")
        connection_error = True
    except HTTPError as e:
        print(' canceled')
        if hasattr(e, 'code'):
            print(f'ERROR: The server could not fulfill the request; Error code: {e.code}')
        connection_error = True
    except URLError as e:
        print(' canceled')
        if hasattr(e, 'reason'):
            print(f'ERROR: We failed to reach the server; Reason: {e.reason}')
        connection_error = True
    
    if connection_error:
        return None

    return file_name_path


def sras_info(sra_file, out_file=None):
    sra_details = {}
    with open(sra_file) as fin:
        for line in fin.readlines():
            sra_acc = line.strip()
            sra_details[sra_acc] = sra_info(sra_acc)
    if out_file:
        with open(out_file, "w") as fout:
            fout.write("sra_acc,lane_number,size_mb\n")
            for sra_acc, details in sra_details.items():
                print(details)
                fout.write(f'{sra_acc},{details["lane_number"]},{details["size_mb"]}\n')
    return sra_details


def sra_info(sra_acc):
    from xml.dom.minidom import parseString
    from xml.parsers.expat import ExpatError
    
    sra_stat = which("sra-stat")
    if not sra_stat:
        print("ERROR - Command not found: sra-stat (NCBI SRA Toolkit)")
        return {"lane_number": None, "size_mb": None}

    arg_list = [sra_stat, "-xse2", sra_acc]
    print(f'[ SRA Toolkit ] Retrieving stats for {sra_acc}...', end='', flush=True)
    cmd_out = run_command(' '.join(arg_list), shell=True, print_output=False)
    print(' done')

    try:
        dom = parseString(''.join(cmd_out))
        collection = dom.documentElement
        size_bytes = collection.getElementsByTagName("Size")[0].getAttribute("value")
        try: 
            size_mb = int(size_bytes)/(1024*1024)
            if (size_mb / 1024) > 1:
                size_mb_str = f"{(size_mb / 1024):.2f}GB"
            else:
                size_mb_str = f"{size_mb:.2f}MB"
        except ValueError:
            size_mb = None
            size_mb_str = "NA"
        statistics = collection.getElementsByTagName("Statistics")
        nreads_list = []
        for statistic in statistics:
            if statistic.getAttribute("nreads") != "":
                nreads_list.append(statistic.getAttribute("nreads"))
                count_list = []
                reads = statistic.getElementsByTagName("Read")
                for read in reads:
                    count_list.append(read.getAttribute("count"))
        dom.unlink()
    except ExpatError as err:
        nreads_list = []
        size_mb = 0
        size_mb_str = 0
        print(f'[ SRA Toolkit ] Error parsing stats for {sra_acc}: {err}')

    # lane_number: 0 = error, 1 = single, 2 = paired
    if len(nreads_list) != 1:
        print("WARNING - Unexpected output of sra-stat (multiple nreads output)")

    lane_number = 0
    if nreads_list:
        if nreads_list[0] == "1":
            lane_number = 1
        elif nreads_list[0] == "2":
            if len(count_list) != 2:
                print("WARNING - Unexpected output from sra-stat (single read index for nreads = 2)")
            if count_list == ["0","1"] or count_list == ["1", "0"]:
                lane_number = 1
            elif count_list == ["1","1"]:
                lane_number = 2
            else:
                print("WARNING - Unexpected output from sra-stat (unexpected count in read index)")
    print(f'[ SRA Toolkit ] SRA {sra_acc}: lanes={lane_number}, size={size_mb_str}')
    return {"lane_number": lane_number, "size_mb": size_mb}


def sra_downloader(sra_acc, download_folder, env_exports={}):
    fasterq_dump = which("fasterq-dump")
    if runningInDocker():
        sys.exit("""
            The NCBI SRA Toolkit required to retrieve sra read files is not available in the bromberglab/mifaser docker image.
            Please use the bromberglab/sra-toolkit or ncbi/sra-toolkit image to dowload sra files and provide those as input
            for mi-faser.
            """)
    elif not fasterq_dump:
        sys.exit("ERROR - command not found: fasterq-dump (NCBI SRA Toolkit)")
    target_file = os.path.join(download_folder, f'{sra_acc}.fastq')
    target_file_R1 = os.path.join(download_folder, f'{sra_acc}_1.fastq')
    target_file_R2 = os.path.join(download_folder, f'{sra_acc}_2.fastq')
    target_file_R1_2 = os.path.join(download_folder, f'{sra_acc}_2.fastq')
    target_file_R2_4 = os.path.join(download_folder, f'{sra_acc}_4.fastq')
    for f_ in [target_file, target_file_R1, target_file_R2, target_file_R1_2, target_file_R2_4]:
        if os.path.exists(f_):
            os.remove(f_)
    cmd = f'{fasterq_dump} --split-files -O "{download_folder}" -o "{sra_acc}.fastq" {sra_acc}'
    print(f'[ SRA Toolkit ] Retrieving {sra_acc}...')
    cmd_out = run_command(cmd, shell=True, print_output=False, env_exports=env_exports)
    for l in cmd_out:
        if l:
            print(f'[ SRA Toolkit ] {l}')
    if os.path.exists(target_file):
        return [target_file]
    elif os.path.exists(target_file_R1) and os.path.exists(target_file_R2):
        return [target_file_R1, target_file_R2]
    elif os.path.exists(target_file_R1_2) and os.path.exists(target_file_R2_4):
        return [target_file_R1_2, target_file_R2_4]
    elif os.path.exists(target_file_R1):
        return [target_file_R1]
    elif os.path.exists(target_file_R1_2):
        return [target_file_R1_2]
    else:
        sys.exit(f"ERROR - Could not download SRA: {sra_acc}")


def parse_inputfiles(inputfile, lanes):
    inputfiles = []
    if inputfile:
        inputfiles = [inputfile]
    elif lanes:
        inputfiles = lanes[0]
    return inputfiles


def download_inputfiles(inputfiles, download_folder=None, env_exports={}):
    inputfiles_downloaded = []
    has_download_folder = True if download_folder else False
    if not has_download_folder:
        download_folder = os.getcwd()
    if inputfiles and len(inputfiles) == 1:
        inputfile = inputfiles[0]
        if inputfile.startswith(VALID_URLS):
            url = inputfile
            download_file_name = None
            url_in = inputfile.split(",")
            if len(url_in) == 2:
                url = url_in[0]
                download_file_name = url_in[1]
            downloaded_file = download_url(url, file_name=download_file_name, out_folder=download_folder)
            if not downloaded_file:
                sys.exit(f"ERROR - Could not download file from url: {inputfile}")
            else:
                inputfiles_downloaded = [os.path.abspath(downloaded_file)]
        elif inputfile.startswith("sra:"):
            sra_acc = inputfile[4:]
            sra_downloaded = sra_downloader(sra_acc, os.path.abspath(download_folder), env_exports)
            if len(sra_downloaded) == 1:
                inputfiles_downloaded = [os.path.abspath(sra_downloaded[0])]
            else:
                print(f"Got SRA with 2-lane format: {sra_acc}")
                for sra_ in sra_downloaded:
                    inputfiles_downloaded+=[os.path.abspath(sra_)]
        for inputfile_ in inputfiles_downloaded:
            if not os.path.exists(inputfile_):
                found = False
                if has_download_folder:
                    inputfile_at_download_folder = os.path.join(download_folder, os.path.basename(inputfile_))
                    if os.path.exists(inputfile_at_download_folder):
                        inputfile_ = inputfile_at_download_folder
                        found = True
                if not found:
                    sys.exit(f"ERROR - Could not read input file: {inputfile_}")
    elif inputfiles:
        if len(inputfiles) != 2:
            sys.exit(f"ERROR - Could not identify 2-lane input files: {inputfiles}")
        lanes_checked = []
        for lane_file in inputfiles:
            if lane_file.startswith(VALID_URLS):
                url = lane_file
                download_file_name = None
                url_in = lane_file.split(",")
                if len(url_in) == 2:
                    url = url_in[0]
                    download_file_name = url_in[1]
                downloaded_file = download_url(url, file_name=download_file_name, out_folder=download_folder)
                if not downloaded_file:
                    sys.exit(f"ERROR - Could not download file from url: {lane_file}")
                else:
                    lanes_checked.append(downloaded_file)
            elif lane_file.startswith("sra:"):
                sra_acc = lane_file[4:]
                sra_downloaded = sra_downloader(sra_acc, os.path.abspath(download_folder))

                if len(sra_downloaded) == 1:
                    lanes_checked.extend(sra_downloaded)
                else:
                    sys.exit(f"ERROR - Got SRA with 2-lane format ({sra_acc}) while processing 2-lane input: {inputfiles}")
            else:
                lanes_checked.append(lane_file)
        r1_ = os.path.abspath(lanes_checked[0])
        r2_ = os.path.abspath(lanes_checked[1])
        if not os.path.exists(r1_) or not os.path.exists(r2_):
            found_r1, found_r2 = (False, False)
            if has_download_folder:
                r1_at_download_folder = os.path.join(download_folder, os.path.basename(r1_))
                if os.path.exists(r1_at_download_folder):
                    r1_ = r1_at_download_folder
                    found_r1 = True
                r2_at_download_folder = os.path.join(download_folder, os.path.basename(r2_))
                if os.path.exists(r2_at_download_folder):
                    r2_ = r2_at_download_folder
                    found_r2 = True
            if not (found_r1 and found_r2):
                sys.exit(f"ERROR - Could not read all input file: {r1_},{r2_}")
        inputfiles_downloaded = [r1_, r2_]

    return inputfiles_downloaded


def preprocess_input(files, split, outdir, splits, diamondfolder, databasefolder, read_mapping, cpu_limit, max_threads, method,
                     threadpool=None, quiet=False):
    """Preprocessing: split input files"""

    global QUIET
    QUIET = quiet
    global ERROR_STATE
    msgstack = []
    err_msgs = []
    msg_log = os.path.join(outdir, 'mifaser.log')
    err_log = os.path.join(outdir, 'mifaser.err')

    skip = False
    try:
        for file in files:
            input_file_name = os.path.basename(file)
            input_file_base = os.path.splitext(input_file_name)[0]

            # check if file is compressed
            skip = False
            is_compressed = True
            input_file_tmp_extract_dir = os.path.join(outdir, input_file_name)
            if input_file_name.endswith('.zip'):
                log("     Extracting %s [zip]... " % input_file_name, quiet, msgstack)
                os.mkdir(input_file_tmp_extract_dir)
                shutil.unpack_archive(file, input_file_tmp_extract_dir, 'zip')
            elif input_file_name.endswith('.bzip2'):
                log("     Extracting %s [bzip2]... " % input_file_name, quiet, msgstack)
                os.mkdir(input_file_tmp_extract_dir)
                shutil.unpack_archive(file, input_file_tmp_extract_dir, 'bztar')
            elif input_file_name.endswith('.xz'):
                log("     Extracting %s [xz]... " % input_file_name, quiet, msgstack)
                os.mkdir(input_file_tmp_extract_dir)
                shutil.unpack_archive(file, input_file_tmp_extract_dir, 'xztar')
            elif input_file_name.endswith('.tar'):
                log("     Extracting %s [tar]... " % input_file_name, quiet, msgstack)
                os.mkdir(input_file_tmp_extract_dir)
                shutil.unpack_archive(file, input_file_tmp_extract_dir, 'tar')
            elif input_file_name.endswith('.tar.gz'):
                log("     Extracting %s [tar.gz]... " % input_file_name, quiet, msgstack)
                os.mkdir(input_file_tmp_extract_dir)
                shutil.unpack_archive(file, input_file_tmp_extract_dir, 'gztar')
            elif input_file_name.endswith('.gz') or input_file_name.endswith('.gzip'):
                log("     Extracting %s [gz/gzip]... " % input_file_name, quiet, msgstack)
                os.mkdir(input_file_tmp_extract_dir)
                input_file_name = input_file_name.rsplit('.', 1)[0]
                with gzip.open(file, 'rb') as f_in, \
                        open(os.path.join(input_file_tmp_extract_dir, input_file_name), 'wb') as f_out:
                    f_out.writelines(f_in)
            elif input_file_name.endswith('.bz2') or input_file_name.endswith('.bzip2'):
                log("     Extracting %s [bz2/bzip2]... " % input_file_name, quiet, msgstack)
                from bz2 import BZ2File
                os.mkdir(input_file_tmp_extract_dir)
                input_file_name = input_file_name.rsplit('.', 1)[0]
                with BZ2File(file, 'rb') as f_in, \
                        open(os.path.join(input_file_tmp_extract_dir, input_file_name), 'wb') as f_out:
                    f_out.writelines(f_in)
            else:
                is_compressed = False

            if is_compressed:
                extracted_fasta_files = find_in_dir(
                    input_file_tmp_extract_dir, extensions=VALID_FILETYPES, correct=True
                )
                if len(extracted_fasta_files) == 0:
                    raise InputError("No valid file found")
                else:
                    log(" *** Extracted %i files. Processing all and merging results." % len(extracted_fasta_files),
                        quiet, msgstack)
                    for extracted_file in extracted_fasta_files:
                        preprocess_input([extracted_file], split, outdir, splits,
                                         diamondfolder, databasefolder, read_mapping,
                                         cpu_limit, max_threads, method, threadpool, quiet)
                    skip = True
            else:
                valid, filename_corrected = check_filetype(input_file_name, extensions=VALID_FILETYPES, correct=True)
                if valid:
                    if filename_corrected:
                        input_file_name_old = input_file_name
                        input_file_name = filename_corrected
                        file_old = file
                        file = os.path.join(os.path.dirname(file), input_file_name)
                        os.rename(file_old, file)
                        log("     Renamed file %s -> %s" % (input_file_name_old, input_file_name), quiet, msgstack)
                    log(" *** Input: Uncompressed file %s" % input_file_name, quiet, msgstack)
                else:
                    raise InputError("Not a valid input file: %s" % file)

            if not skip:
                input_format = 'fasta'
                if input_file_name.endswith('.fq') or input_file_name.endswith('.fastq'):
                    input_format = 'fastq'

                if input_format == 'fastq':
                    log("     Converting %s from fastq to fasta format... " % input_file_name,
                        quiet, msgstack)
                    input_file_converted = os.path.join(outdir, '%s.fasta' % input_file_base)
                    with open(file, 'r') as fastq_in, open(input_file_converted, 'w') as fasta_out:
                        fastq_convert_fasta(fastq_in, fasta_out)
                    file = input_file_converted

                log("     Getting input file statistics... ", quiet, msgstack)
                file_size_mb = os.path.getsize(file) / 1000000
                log("     Input file size: %iMB" % file_size_mb, quiet, msgstack)
                read_count = fasta_header_count(file)
                log("     Input file reads: %i" % read_count, quiet, msgstack)

                if threadpool:
                    method.threadlock.acquire()
                    method.file_size_mb = file_size_mb if not method.file_size_mb else method.file_size_mb+file_size_mb
                    method.threadlock.release()

                if split > 0:
                    if not threadpool:
                        if "split_mb" in FLAGS:
                            infile_list = split_by_size(
                                file, outdir, split, read_count,
                                diamondfolder, databasefolder, read_mapping, cpu_limit, max_threads, method, threadpool
                            )
                        else:
                            infile_list, read_count = split_by_length(
                                file, outdir, split,
                                diamondfolder, databasefolder, read_mapping, cpu_limit, max_threads, method, threadpool
                            )
                    else:
                        infile_list = split_by_size(
                            file, outdir, split, read_count,
                            diamondfolder, databasefolder, read_mapping, cpu_limit, max_threads, method, threadpool
                        )
                else:
                    infile_list = [file]

                    if not threadpool:
                        THREADPOOL.submit(method, file, 1, max_threads, cpu_limit,
                                          outdir, diamondfolder, databasefolder, read_mapping)
                    else:
                        threadpool.submit(method.process_split_server, file, (1, 0), last=True)

                splits.extend(infile_list)
    except ImportError as err:
        log(" !>> ERROR. Could not import a required module: %s" % err, quiet, err_msgs)
        ERROR_STATE = True
    except ValueError as err:
        log(" !>> ERROR. %s" % err, quiet, err_msgs)
        ERROR_STATE = True
    except InputError as err:
        log(" !>> ERROR. %s" % err, quiet, err_msgs)
        ERROR_STATE = True
    finally:
        if ERROR_STATE and not skip:
            log(f" !>> ERROR. logs: %s" % err_log, quiet, msgstack)
        if threadpool or quiet:
            # threadlock.acquire()
            if err_msgs:
                with open(err_log, "a") as mifaser_err:
                    mifaser_err.writelines(f"{l}\n" for l in err_msgs)
            if msgstack:
                with open(msg_log, "a") as mifaser_log:
                    mifaser_log.writelines(f"{l}\n" for l in msgstack)
                # threadlock.release()


def postprocess_results(splits, splits_out, outdir, prefix='analyzed', service=False, quiet=False):
    """Merge results into one single file"""

    if service:
        quiet = True
    success = True
    msgstack = []
    msg_log = os.path.join(outdir, 'mifaser%s.log' % ('_postprocessing' if service else ''))
    err_log = os.path.join(outdir, 'mifaser%s.err' % ('_postprocessing' if service else ''))

    total_jobcount = len(splits)

    resultfolders_list = []
    for file in splits:
        file_name = os.path.splitext(os.path.basename(file))[0]
        job_folder_path = os.path.join(os.path.abspath(splits_out), file_name)
        if os.path.isdir(job_folder_path):
            resultfolders_list.append(job_folder_path)
        else:
            log(" WARNING: result folder %s not found" % job_folder_path, quiet, msgstack)
            success = False

    if total_jobcount != len(resultfolders_list):
        log(" WARNING: found %i result folders for %i jobs" % (len(resultfolders_list), total_jobcount),
            quiet, msgstack)

    merged_result = {}
    merged_ec_count = []
    merged_multi_ec = {}
    merged_stats = {'ec_annotated_total': 0, 'ec_annotated_multiple': 0}
    merged_logs = {}
    merged_errs = {}
    merged_service_out = {}
    merged_service_err = {}

    missing_analysis_list = []
    missing_joblist = []
    missing_eccount_list = []
    missing_multiec_list = []

    # retrieve preprocessing logs
    preprocessing_log_file = os.path.join(splits_out, 'mifaser.log')
    preprocessing_err_file = os.path.join(splits_out, 'mifaser.err')
    if os.path.exists(preprocessing_log_file):
        with open(preprocessing_log_file, 'r') as log_fh:
            merged_logs['preprocessing'] = [line for line in log_fh.readlines() if line.strip()]
        if not merged_logs['preprocessing']:
            merged_logs.pop('preprocessing', None)
    if os.path.exists(preprocessing_err_file):
        with open(preprocessing_err_file, 'r') as err_fh:
            merged_errs['preprocessing'] = [line for line in err_fh.readlines() if line.strip()]
        if not merged_errs['preprocessing']:
            merged_errs.pop('preprocessing', None)

    # process split folders
    merge = len(resultfolders_list) > 1
    if merge:
        log("  *  Merging %i splits..." % len(resultfolders_list), quiet, msgstack)
    for output_folder in resultfolders_list:
        log_file = os.path.join(output_folder, os.path.join(prefix, 'mifaser.log'))
        err_file = os.path.join(output_folder, os.path.join(prefix, 'mifaser.err'))
        analysis_file = os.path.join(output_folder, os.path.join(prefix, 'analysis.tsv'))
        eccount_file = os.path.join(output_folder, os.path.join(prefix, 'ec_count.tsv'))
        multiec_file = os.path.join(output_folder, os.path.join(prefix, 'multi_ec.tsv'))
        service_out_file = os.path.join(output_folder, os.path.join(prefix, 'clubber.out'))
        service_err_file = os.path.join(output_folder, os.path.join(prefix, 'clubber.err'))

        # log and err merge
        split_id = os.path.basename(output_folder)

        if os.path.exists(log_file):
            with open(log_file, 'r') as log_fh:
                merged_logs[split_id] = [line for line in log_fh.readlines() if line.strip()]
            if not merged_logs[split_id]:
                merged_logs.pop(split_id, None)
        if os.path.exists(err_file):
            with open(err_file, 'r') as err_fh:
                merged_errs[split_id] = [line for line in err_fh.readlines() if line.strip()]
            if not merged_errs[split_id]:
                merged_errs.pop(split_id, None)

        # analysis merge
        if not os.path.exists(analysis_file):
            missing_analysis_list.append(output_folder)
            missing_job_full_id = os.path.basename(os.path.abspath(output_folder))
            if service:
                missing_job_jobid = int(missing_job_full_id.split('.')[0])
                missing_job_arrayidx = int(missing_job_full_id.split('.')[1])
                missing_joblist.append((missing_job_jobid, missing_job_arrayidx))
            else:
                missing_joblist.append(missing_job_full_id)
            log(" WARNING: Missing analysis file: %s" % analysis_file, quiet, msgstack)
            success = False
        else:
            with open(analysis_file, 'r') as tsv_in:
                tsv_in = csv.reader(tsv_in, delimiter='\t')
                header_stats = next(tsv_in)
                merged_stats['ec_annotated_total'] = merged_stats['ec_annotated_total'] + int(header_stats[0])
                merged_stats['ec_annotated_multiple'] = merged_stats['ec_annotated_multiple'] + int(header_stats[1])

                for row in tsv_in:
                    _ec = row[0]
                    _readcount = int(row[1])
                    # description = row[2]

                    if _ec not in merged_result.keys():
                        merged_result[_ec] = _readcount
                    else:
                        merged_result[_ec] = merged_result[_ec] + _readcount

        # ec_count merge
        if not os.path.exists(eccount_file):
            log(" WARNING: Missing eccount file: %s" % eccount_file, quiet, msgstack)
            success = False
            missing_eccount_list.append(output_folder)
        else:
            with open(eccount_file, 'r') as tsv_in:
                tsv_in = csv.reader(tsv_in, delimiter='\t')
                for row in tsv_in:
                    merged_ec_count.append(row)

        # multiec merge
        if not os.path.exists(multiec_file):
            log(" WARNING: Missing multiec file: %s" % multiec_file, quiet, msgstack)
            success = False
            missing_multiec_list.append(output_folder)
        else:
            with open(multiec_file, 'r') as tsv_in:
                tsv_in = csv.reader(tsv_in, delimiter='\t')
                for row in tsv_in:
                    _ecs = row[0]
                    _readcounts = int(row[1])
                    if _ecs not in merged_multi_ec.keys():
                        merged_multi_ec[_ecs] = _readcounts
                    else:
                        merged_multi_ec[_ecs] = merged_multi_ec[_ecs] + _readcounts

        # service
        if service and merge:
            if os.path.exists(service_out_file):
                with open(service_out_file, 'r') as service_out_fh:
                    merged_service_out[split_id] = [line for line in service_out_fh.readlines() if line.strip()]
                if not merged_service_out[split_id]:
                    merged_service_out.pop(split_id, None)
            if os.path.exists(service_err_file):
                with open(service_err_file, 'r') as service_err_fh:
                    merged_service_err[split_id] = [line for line in service_err_fh.readlines() if line.strip()]
                if not merged_service_err[split_id]:
                    merged_service_err.pop(split_id, None)

    # sort analysis by ec number
    merged_result = OrderedDict(sorted(merged_result.items(), key=ec_numbers))
    result_file = os.path.join(outdir, 'analysis.tsv')
    with open(result_file, 'w') as tsv_out:
        tsv_writer = csv.writer(tsv_out, delimiter='\t')
        tsv_writer.writerow([merged_stats['ec_annotated_total'], merged_stats['ec_annotated_multiple']])
        for ec, readcount in merged_result.items():
            tsv_writer.writerow([ec, readcount])

    merged_ec_mapping_dir = os.path.join(outdir, 'read_map')
    merged_log_out = os.path.join(outdir, 'mifaser.log')
    merged_err_out = os.path.join(outdir, 'mifaser.err')
    merged_result_eccount = os.path.join(outdir, 'ec_count.tsv')
    merged_result_multiec = os.path.join(outdir, 'multi_ec.tsv')
    merged_service_out_file = os.path.join(outdir, 'clubber.out')
    merged_service_err_file = os.path.join(outdir, 'clubber.err')
    if merge:
        # ec read mapping merge
        has_read_mapping = False
        if not os.path.exists(merged_ec_mapping_dir):
            os.mkdir(merged_ec_mapping_dir)
        for ec in merged_result.keys():
            merged_ec_mapping_file = os.path.join(merged_ec_mapping_dir, "%s.fasta" % ec)
            with open(merged_ec_mapping_file, 'w') as outfile:
                for output_folder in resultfolders_list:
                    ec_mapping_dir = os.path.join(output_folder, os.path.join(prefix, 'read_map'))
                    ec_mapping_file = os.path.join(ec_mapping_dir, "%s.fasta" % ec)
                    if os.path.exists(ec_mapping_file):
                        has_read_mapping = True
                        with open(ec_mapping_file, 'r') as infile:
                            outfile.write(infile.read())
        if not has_read_mapping:
            shutil.rmtree(merged_ec_mapping_dir)

        # writing files
        with open(merged_log_out, 'a') as log_fho:
            for split_id, logs in merged_logs.items():
                if logs:
                    log_fho.writelines("%s\n" % l.rstrip() for l in logs)

        with open(merged_err_out, 'a') as err_fho:
            for split_id, errs in merged_errs.items():
                if errs:
                    err_fho.write('#%s\n' % split_id)
                    err_fho.writelines("%s\n" % e.rstrip() for e in errs)

        with open(merged_result_eccount, 'w') as tsv_out:
            tsv_writer = csv.writer(tsv_out, delimiter='\t')
            for row in merged_ec_count:
                tsv_writer.writerow(row)

        with open(merged_result_multiec, 'w') as tsv_out:
            tsv_writer = csv.writer(tsv_out, delimiter='\t')
            for ecs, count in merged_multi_ec.items():
                tsv_writer.writerow([ecs, count])

        if service:
            with open(merged_service_out_file, 'a') as service_out_fho:
                for _, s_out in merged_service_out.items():
                    if s_out:
                        service_out_fho.writelines("%s\n" % l.rstrip() for l in s_out)
            with open(merged_service_err_file, 'a') as service_err_fho:
                for _, s_err in merged_service_err.items():
                    if s_err:
                        service_err_fho.writelines("%s\n" % l.rstrip() for l in s_err)

    elif len(resultfolders_list) == 1:
        output_folder = resultfolders_list[0]
        ec_mapping_dir = os.path.join(output_folder, os.path.join(prefix, 'read_map'))
        analysis_file = os.path.join(output_folder, os.path.join(prefix, 'analysis.tsv'))
        eccount_file = os.path.join(output_folder, os.path.join(prefix, 'ec_count.tsv'))
        multiec_file = os.path.join(output_folder, os.path.join(prefix, 'multi_ec.tsv'))
        service_out_file = os.path.join(output_folder, os.path.join(prefix, 'clubber.out'))
        service_err_file = os.path.join(output_folder, os.path.join(prefix, 'clubber.err'))
        if os.path.exists(merged_ec_mapping_dir):
            shutil.rmtree(merged_ec_mapping_dir)
        if os.path.exists(ec_mapping_dir):
            os.rename(ec_mapping_dir, merged_ec_mapping_dir)
        if merged_logs:
            if 'preprocessing' in merged_logs.keys():
                with open(merged_log_out, 'a') as fout:
                    fout.writelines("%s\n" % l.rstrip() for l in merged_logs['preprocessing'])
            for split in merged_logs.keys():
                if split == 'preprocessing':
                    continue
                with open(merged_log_out, 'a') as fout:
                    fout.writelines("%s\n" % l.rstrip() for l in merged_logs[split])
        if merged_errs:
            if 'preprocessing' in merged_errs.keys():
                with open(merged_err_out, 'a') as fout:
                    fout.writelines("%s\n" % l.rstrip() for l in merged_errs['preprocessing'])
            for split in merged_errs.keys():
                if split == 'preprocessing':
                    continue
                with open(merged_err_out, 'a') as fout:
                    fout.writelines("%s\n" % l.rstrip() for l in merged_errs[split])
        os.remove(analysis_file)
        os.rename(eccount_file, merged_result_eccount)
        os.rename(multiec_file, merged_result_multiec)
        if service:
            if os.path.exists(service_out_file):
                os.rename(service_out_file, merged_service_out_file)
            if os.path.exists(service_err_file):
                os.rename(service_err_file, merged_service_err_file)

    if len(missing_analysis_list) or len(missing_eccount_list) or len(missing_multiec_list) \
            or (total_jobcount != len(resultfolders_list)):
        msg = f"analysis:{len(missing_analysis_list):d} " \
              f"eccount:{len(missing_eccount_list):d} " \
              f"multiec:{len(missing_multiec_list):d} " \
              f"(resultfolder count:{len(resultfolders_list):d}/{total_jobcount:d})"
        log(" WARNING: Missing result files: " + msg, quiet, msgstack)
        success = False

    if not success or merged_errs:
        log(f" *** ERROR. logs: %s" % err_log, quiet, msgstack)
    if quiet:
        if msgstack:
            with open(msg_log, "a") as mifaser_log:
                mifaser_log.writelines(f"{l}\n" for l in msgstack)

    if not success or merged_errs:
        return False, merged_result, merged_stats, missing_joblist
    else:
        return success, merged_result, merged_stats, missing_joblist


def process_split_standalone(split, threadid, max_threads, cpu_limit, splits_folder, diamondfolder, databasefolder, read_mapping):
    threadid = f"Thread #{threadid}"
    file_name = os.path.splitext(os.path.basename(split))[0]
    caller.main(os.path.abspath(split),
                os.path.join(os.path.abspath(splits_folder), file_name),
                os.path.abspath(databasefolder),
                os.path.abspath(diamondfolder),
                read_mapping,
                cpu_limit,
                max_threads,
                threadid,
                THREADLOCK,
                QUIET)


def run_standalone(inputfiles, splitsize, splits_folder,
                   diamondfolder, databasefolder, read_mapping,
                   cpu_limit, max_threads, quiet, wait=True):
    global THREADPOOL
    global ERROR_STATE
    THREADPOOL = ThreadPoolExecutor(max_workers=max_threads)

    if os.path.exists(splits_folder):
        shutil.rmtree(splits_folder)
    os.mkdir(splits_folder)

    splits = []
    preprocess_input(inputfiles, splitsize, splits_folder, splits, diamondfolder, databasefolder, read_mapping,
                     cpu_limit, max_threads, process_split_standalone, quiet=quiet)

    THREADPOOL.shutdown(wait=wait)
    return splits, ERROR_STATE


def run_service(mifaser_service):
    global ERROR_STATE
    preprocess_input(mifaser_service.inputfiles, mifaser_service.splitsize, mifaser_service.scratch_job_in,
                     list(), None, None, mifaser_service.read_mapping, None, None, mifaser_service,
                     threadpool=mifaser_service.threadpool, quiet=True)
    return ERROR_STATE
