import time
import imp
import sys
import subprocess
max_try = 5
try_time = 0.5


def urllib_model(host, path):
    for i in range(0, max_try):
        ssh = subprocess.Popen(['ssh', host, 'cat', path],
                               stdout=subprocess.PIPE)
        u = ssh.stdout.read()
        if not u:
            print("urllib remote call fail {} - {}".format(i+1, path))
            if i == max_try -1:
                raise Exception("urllib remote call fail max try")
            time.sleep(try_time)
            continue
        else:
            break

    source = u.decode('utf-8')
    mod = sys.modules.setdefault(path, imp.new_module(path))
    code = compile(source, path, 'exec')
    mod.__file__ = path
    mod.__package__ = ''
    exec(code, mod.__dict__)
    return mod

