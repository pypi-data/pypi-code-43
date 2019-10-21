#!/usr/bin/env python

import setuptools
import sys

from setuptools.command.install import install

def install_win():
    try:
        import winreg
    except ImportError:  
       import _winreg as winreg

    SZ = winreg.REG_SZ
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\Classes\.ipynb") as k:
        winreg.SetValue(k, "", SZ, "Jupyter.nbopen")
        winreg.SetValueEx(k, "Content Type", 0, SZ, "application/x-ipynb+json")
        winreg.SetValueEx(k, "PerceivedType", 0, SZ, "document")
        with winreg.CreateKey(k, "OpenWithProgIds") as openwith:
            winreg.SetValueEx(openwith, "Jupyter.nbopen", 0, winreg.REG_NONE, b'')

    executable = sys.executable
    if executable.endswith("python.exe"):
        executable = executable[:-10] + 'pythonw.exe'
    launch_cmd = '"{}" -m nbopen "%1"'.format(executable)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\Classes\Jupyter.nbopen") as k:
        winreg.SetValue(k, "", SZ, "IPython notebook")
        with winreg.CreateKey(k, "shell\open\command") as launchk:
            winreg.SetValue(launchk, "", SZ, launch_cmd)

    try:
        from win32com.shell import shell, shellcon
        shell.SHChangeNotify(shellcon.SHCNE_ASSOCCHANGED, shellcon.SHCNF_IDLIST, None, None)
    except ImportError:
        print("You may need to restart for association with .ipynb files to work")
        print("  (pywin32 is needed to notify Windows of the change)")


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        if sys.platform == 'win32':
            print('Writing to registry...', end='')
            install_win()
            print('done')
        install.run(self)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="winbopen",
    version="0.7.1",
    author='Lev Maximov',
    author_email='lev.maximov@gmail.com',
    url='https://github.com/axil/winbopen',
    description="Opens ipynb files on click. Reuses existing jupyter instance if possible.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['notebook', 'psutil'],
    packages=['nbopen'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT License",
    zip_safe=False,
    keywords=['jupyter', 'notebook', 'ipynb'],
    cmdclass={
        'install': PostInstallCommand,
    },)
