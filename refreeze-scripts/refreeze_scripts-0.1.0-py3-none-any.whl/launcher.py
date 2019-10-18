from __future__ import annotations

import sys
from pathlib import Path
from typing_extensions import Literal
from setuptools.command.easy_install import get_win_launcher, is_64bit, load_launcher_manifest


def create_windows_launcher(name: str,
                            prefix: str=sys.prefix,
                            type: Literal['cli', 'gui']='cli',
                            verbose: bool=True,
                            dry: bool=True) -> None:
    """
    Create Windows launcher in Scripts directory of python path

    Most of code has forked from easy_install.py in pypa/setuptools
    """
    # Copyright (C) 2016 Jason R Coombs <jaraco@jaraco.com>
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy of
    # this software and associated documentation files (the "Software"), to deal in
    # the Software without restriction, including without limitation the rights to
    # use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
    # of the Software, and to permit persons to whom the Software is furnished to do
    # so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in all
    # copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    # SOFTWARE.
    #
    # https://github.com/pypa/setuptools/blob/1362c8c37355f74b5aa9a8afb749aa9464bb58fb/setuptools/command/easy_install.py#L2216-L2244
    base = Path(prefix).joinpath('Scripts', name)
    exepath = base.with_suffix('.exe')
    content = get_win_launcher(type)
    if verbose:
        print("write %s" % exepath)
    if not dry:
        exepath.write_bytes(content)
    if not is_64bit():
        # install a manifest for the launcher to prevent Windows
        # from detecting it as an installer (which it will for
        #  launchers like easy_install.exe). Consider only
        #  adding a manifest for launchers detected as installers.
        #  See Distribute #143 for details.
        manpath = base.with_suffix('.exe.manifest')
        manifest = load_launcher_manifest(name)
        if verbose:
            print("write %s" % manpath)
        if not dry:
            manpath.write_text(manifest)
