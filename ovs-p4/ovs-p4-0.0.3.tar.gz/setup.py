import setuptools
import os
import subprocess
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        path = os.path.join(self.build_lib, 'scripts')
        file_path = os.path.join(path, 'install_p4runtime.sh')
        output = subprocess.check_output(['bash', file_path])
        print output
        install.run(self)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ovs-p4",
    version="0.0.3",
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
    include_package_data=True,
)
