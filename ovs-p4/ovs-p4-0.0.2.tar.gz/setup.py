import setuptools
import os, sys
import subprocess
# from distutils.command.install import install
from setuptools.command.install import install
from subprocess import check_call


# def _post_install(dir):
#     from subprocess import call
#     path = os.path.join(dir, 'scripts')
#     file_path = os.path.join(path, 'install_p4runtime.sh')
#     print file_path
#     call('./' + file_path)
#
#
# class _install(install):
#     def run(self):
#         install.run(self)
#         self.execute(_post_install, (self.build_lib,),
#                      msg="Running post install task")


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        path = os.path.join(self.build_lib, 'scripts')
        file_path = os.path.join(path, 'install_p4runtime.sh')
        # subprocess.call('./' + file_path)
        cmd = "bash " + file_path
        # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # p.wait()
        # stdout, stderr = p.communicate()
        subprocess.check_output(['bash', file_path])
        install.run(self)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ovs-p4",
    version="0.0.2",
    author="Tomasz Osinski, Mateusz Kossakowski",
    author_email="osinstom@gmail.com, mateusz.kossakowski.10@gmail.com",
    description="The package contains a P4Runtime server for P4 capable ovs switch and a ovs-p4ctl command line tool for monitoring and administering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
    install_requires=[
        "ZODB>=5.1",
    ],
    entry_points={
        'console_scripts': ['ovs-p4ctl=p4_ctl.p4_ctl:main',
                            'ovs-p4srv=ovs_p4.ovs_p4:main'],
    },
    cmdclass={'install': PostInstallCommand},
    # data_files=[('', ['scripts/install_p4runtime.sh'])],
    # package_data={'scripts': ['install_p4runtime.sh']},
    include_package_data=True,
)
