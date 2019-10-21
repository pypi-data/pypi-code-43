import os
from easilyb.commands import get_command_output, run_command, run_command_ex1

import logging

logger = logging.getLogger(__name__)

_PS_TO_INT = ['PID', 'PPID', 'RSS']


def meminfo():
    total, free = 0, 0
    with open('/proc/meminfo') as fin:
        for line in fin.readlines():
            sline = line.split()
            if str(sline[0]) == 'MemTotal:':
                total = int(sline[1])
            elif str(sline[0]) == 'MemFree:':
                free = int(sline[1])
    return total, free


def get_processes():
    output, err = get_command_output(['ps', '-Ao', 'pid,ppid,uname,rss,comm=PROG,command=CMDLINE'])
    lines = output.split('\n')
    header = lines[0].split()
    processes = [line.split(None, len(header) - 1) for line in lines[1:] if len(line) > 0]
    processes2 = list()
    for processe in processes:
        processes2.append(
            {header[j]: (int(processe[j]) if header[j] in _PS_TO_INT else processe[j]) for j in range(len(header))})
    return processes2


def get_process(pid, processes=None):
    if processes is None: processes = get_processes()
    for process in processes:
        if process['PID'] == pid:
            return process
    return None


def get_process_children(pid=None, recursive=False, processes=None):
    childs = list()
    if pid is None:
        pid = os.getpid()
    if processes is None: processes = get_processes()
    for p in processes:
        if int(p['PPID']) == pid:
            childs.append(p)
            if recursive:
                childs.extend(get_process_children(pid=p['PPID'], recursive=False, processes=processes))
    return childs


def get_open_ports():
    return_code, output = run_command(["netstat", "-lnt"])
    ret = list()
    if return_code != 0:
        logger.error("netstat returned a non zero code: %d", return_code)
    else:
        lines = output.split('\n')
        for line in lines:
            if 'LISTEN' in line and not 'tcp6' in line:
                try:
                    parts = line.split()
                    host, port = parts[3].split(':')
                    port = int(port)
                    if not port in ret:
                        ret.append(port)
                except Exception as e:
                    logger.warning("exception parsing a line in netstat output: %s (line=%s)" % (str(e), line),
                                   exc_info=True)
    return ret


def memfree():
    try:
        return_code, output = run_command_ex1(["free", "-b"])
        if return_code != 0:
            raise Exception("Non-Zero return code: %d" % return_code)
        splits = output.decode(errors="ignore").split('\n')[1].split()
        total, available = int(splits[1]), int(splits[6])
        used = total - available
        return total, used, available
    except:
        logging.error("Error while running free command", exc_info=True)
        raise


def disk_usage(disk="/"):
    try:
        return_code, output = run_command_ex1(["df", "-B1", disk])
        if return_code != 0:
            raise Exception("Non-Zero return code: %d" % return_code)
        total, used, available = output.decode(errors="ignore").split('\n')[1].split()[1:4]
        total, available = int(total), int(available)
        used = total - available
        return total, used, available
    except:
        logging.error("Error while running df command on drive:%s", disk, exc_info=True)
        raise


def directory_usage(dir="./"):
    try:
        return_code, output = run_command_ex1(["du", "-b", "-d0", dir])
        if return_code != 0 and return_code != 1:
            raise Exception("Non-Zero return code: %d" % return_code)
        usage = int(output.decode(errors="ignore").split("\n")[-2].split()[0])
        return usage
    except:
        logging.error("Error while running du command on directory:%s", dir, exc_info=True)
        raise


def convert_bytes_to_human(b, dec=1):
    if dec > 10: dec = 10
    if dec == 0:
        if b < 1024:
            return str(b)
        elif b < 1048576:
            return str(b // 1204) + "K"
        elif b < 1073741824:
            return str(b // 1048576) + "M"
        elif b < 1099511627776:
            return str(b // 1073741824) + "G"
        else:
            return str(b // 1099511627776) + "T"
    if b < 1024:
        return str(b)
    elif b < 1048576:
        return str(int(b / 1204 * pow(10, dec)) / pow(10, dec)) + "K"
    elif b < 1073741824:
        return str(int(b / 1048576 * pow(10, dec)) / pow(10, dec)) + "M"
    elif b < 1099511627776:
        return str(int(b / 1073741824 * pow(10, dec)) / pow(10, dec)) + "G"
    else:
        return str(int(b / 1099511627776 * pow(10, dec)) / pow(10, dec)) + "T"


MULTIPLIER = {"b":1, "k": 1024, "m": 1048576, "g": 1073741824, "t": 1099511627776}


def convert_bytes_from_human(h):
    try:
        return float(h)
    except:
        dec, mult = float(h[0:-1]), h[-1]
        return int(dec * MULTIPLIER[mult.lower()])
