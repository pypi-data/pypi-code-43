import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='pybeecn2',
    version='0.0.2',
    author='Gabriel McBride',
    author_email='gabe.l.mcbride@gmail.com',
    description='Ability to view Portland Demographic Data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/glmcbr06/pybeecn2',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'pybeecn2.subcommands': [
            'vis = pybeecn2.vis.cli'
        ],
        'console_scripts': [
            'pybeecn2=pybeecn2.cli:run'
        ]
    }
)
