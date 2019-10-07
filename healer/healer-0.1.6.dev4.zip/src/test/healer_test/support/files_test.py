
from healer.support.files import *
import uuid


def test_files_lock():
    print()
    system_path = "/tmp"
    lock_one = FilesPathLock(system_path)
    lock_two = FilesPathLock(system_path)
    assert lock_one.aquire() == True
    assert lock_one.aquire() == True
    assert lock_two.aquire() == False
    assert lock_two.aquire() == False
    lock_one.release()
    lock_one.release()
    assert lock_two.aquire() == True
    assert lock_two.aquire() == True
    lock_two.release()
    lock_two.release()


def test_machine_id():
    print()
    machine_id = FilesSupport.machine_id()
    print(f"machine_id: {machine_id}")
    guid = uuid.UUID(machine_id)
    print(f"guid: {guid}")


def test_has_writeable():
    print()
    dir_path = "/tmp"
    assert FilesSupport.has_writable(dir_path)
