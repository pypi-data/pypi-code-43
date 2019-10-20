# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib

import alpy.qemu


@contextlib.contextmanager
def qemu_with_skeleton(*, qemu_args, skeleton, timeout):
    try:
        skeleton.create_tap_interfaces()
        with alpy.qemu.run(qemu_args, timeout) as qmp:
            skeleton.create()
            alpy.qemu.read_events(qmp)
            yield qmp
    finally:
        skeleton.close()
