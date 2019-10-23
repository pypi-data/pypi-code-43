from typing import List, Union
import subprocess, logging
from datetime import datetime, timedelta, timezone
from sysapi.env import read_params

PREPTEST_CMD = "bin/preptest.sh"

def do_prepare_test(resetkey: str, testname: str) -> List[Union[int,str]]:
    params = read_params()
    if params['resetkey']  == resetkey:
        cp = subprocess.run([PREPTEST_CMD, testname], capture_output=True)
        if cp.returncode == 0: return (True,cp.stdout)

    return (False, cp.stderr + b'(' + cp.stdout + b')')