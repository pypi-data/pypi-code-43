"""

A tool to deliver matching files and context about search strings

"""
import subprocess, string, re


def os_run(cmd, arg=None):
    """os_run('git grep -c', "match with space")"""
    cmd = cmd if isinstance(cmd, list) else cmd.split()
    if arg:
        cmd.append(arg)
    # we are processing user input, don't allow shell True!!
    process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        raise Exception('Failed', cmd, err.decode('utf-8'))
    return out.decode('utf-8').strip()


def search_repo(match, repo_dir, max_files=5):
    """The tool wants to be fast and is called at any match => we don't verify
    if the cur_dir is right every time. We assume we are in base dir
    Also we don't verify if the repo has changes we would not see.
    """
    assert isinstance(match, str)
    # we don't just list the top counts but want to weigh, i.e. prefer one
    # occurrance in a
    # files = os_run('git grep --count', match).splitlines()
    # files = [l.rsplit(':', 1) for l in files]
    # m = dict([(v, k) for k, v in files])
    # breakpoint()
    # -I: No binary files
    # -p : Shows us the enclosing function or class
    files = os_run('git grep --line-number -I --break --heading -pn', match)
    res = []
    for block in files.split('\n\n'):
        m = {}
        lines = block.splitlines()
        m['fn'] = lines.pop(0)
        m['lines'] = l = []
        while lines:
            ml = {}
            line = lines.pop(0)
            line, txt = re.split(r'[:=]+', line, 1)
            ml['line'] = int(line)
            ml['txt'] = txt
            l.append(ml)
        res.append(m)
    res = {'match': match, 'matches': res}
    return res


def format_md(res):
    """builds a markdown table from res"""
