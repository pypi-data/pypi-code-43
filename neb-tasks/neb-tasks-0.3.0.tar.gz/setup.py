from setuptools import setup, find_packages
from pathlib import Path

def parse_requirements(req_file):
    """Parse a requirements.txt file to a list of requirements"""
    with open(req_file, 'r') as fb:
        reqs = [
            req for req in fb.readlines()
            if req.strip() and not req.startswith('#')
        ]
    return list(reqs)

version_file = open(Path(__file__).parent.resolve() / "VERSION")
version = version_file.read().strip()

install_requires = parse_requirements('requirements/install.txt')
tests_require = parse_requirements('requirements/test.txt')

setup(
    name='neb-tasks',
    author='tomjw64',
    version=version,
    author_email='tomjw64@gmail.com',
    url="https://github.com/openstax/neb-tasks",
    license='AGPL, See also LICENSE.txt',
    description='Content task addons to neb',
    install_requires=install_requires,
    extras_require={
        'test': tests_require,
    },
    tests_require=tests_require,
    entry_points={
        'neb.extension': 'tasks=nebtasks:load_modules',
    },
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3',
)