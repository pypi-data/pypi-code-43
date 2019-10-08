import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="batch-run-cmd",
    version="0.0.2",
    author='Guanliang Meng',
    author_email='linzhi2012@gmail.com',
    description="To run commands line by line, and check each exit status",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.5',
    url='https://github.com/linzhi2013/batch-run-cmd',
    packages=setuptools.find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'batch_run_cmd=batch_run_cmd.batch_run_cmd:main',
        ],
    },
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ),
)
