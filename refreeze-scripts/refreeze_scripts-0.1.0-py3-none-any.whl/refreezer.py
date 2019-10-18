from __future__ import annotations

import os
import sys
import argparse
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
from typing import List

from .parser import parse_simple_launcher
from .launcher import create_windows_launcher


def refreeze(prefix: str, verbose: bool=True, dry: bool=True) -> List[Path]:
    # XXX:
    # Currently only type='cli' is supported while I have no idea
    # how to tell if the simple_launcer exe is for CLI or GUI.
    type = 'cli'
    root = Path(prefix).joinpath('Scripts')
    refreezed = []

    for path in root.iterdir():
        if path.suffix != '.exe' or not path.is_file():
            continue
        sl = parse_simple_launcher(
            path.read_bytes(),
            verbose=verbose,
        )
        if sl.launcher is None or sl.shebang is None:
            # Not simple_launcer
            continue
        # Create a script '-script.py'
        with ZipFile(BytesIO(sl.data)) as z:
            with z.open("__main__.py", "r") as fd:
                data = fd.read()
        script_path = path.with_name(path.stem + '-script').with_suffix('.py')
        if verbose:
            print("write %s" % script_path)
        if not dry:
            script_path.write_bytes(data)
        # Create a wrapper exe
        create_windows_launcher(
            path.stem,
            prefix=prefix,
            type=type,
            verbose=verbose,
            dry=dry,
        )
        if verbose:
            print("%s has refreezed from simple_launcer to launcher" % path.stem)
        refreezed.append(path)

    return refreezed
