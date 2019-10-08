import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

INSTALL_REQUIRES = [
    'numpy',
    'pandas',
    'pysam',
    'parasail==1.1.17'
]

setuptools.setup(
    name='fixalign',
    version='0.2.2',
    author='Zhen Liu',
    author_email='liuzhen2018@sibs.ac.cn',
    description='find and fix missed small exons',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/zhenLiuExplr/fixalign-project',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3',
    entry_points={
        'console_scripts': ['fixalign=fixalign.run_fixalign:main']
    },
    include_package_data=True
)
