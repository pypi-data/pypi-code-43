from setuptools import find_packages, setup

try:
    with open('README.md') as f:
        long_description = f.read()
except Exception:
    long_description = ''
    print('Failed to load README.md as long_description')

setup(
    name='conda_mirror_ng',
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="Eric Dill",
    packages=find_packages(),
    description='Mirror an upstream conda channel to a local directory',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/xhochy/conda-mirror-ng',
    platforms=['Linux', 'Mac OSX', 'Windows'],
    license='BSD 3-Clause',
    install_requires=[
        'requests',
        'pyyaml',
    ],
    entry_points={
        "console_scripts": [
            'conda-mirror-ng = conda_mirror_ng.conda_mirror:cli'
        ]
    }
)
