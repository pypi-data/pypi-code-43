import os


def pidlock(lock_path):
    lock_held = False
    if os.path.exists(lock_path):
        try:
            with open(lock_path) as fin:
                pid = fin.readline().strip()
                if os.path.exists("/proc/%s" % pid):
                    lock_held = True
                else:
                    os.unlink(lock_path)
        except:
            os.unlink(lock_path)
    if lock_held:
        raise LockHeld()

    with open(lock_path, 'w') as fou:
        fou.write("%d" % os.getpid())


def release_lock(lock_path):
    os.unlink(lock_path)


class LockHeld(Exception):
    pass