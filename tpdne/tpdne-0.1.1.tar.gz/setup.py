import os
import re
from setuptools import setup, find_packages

regexp = re.compile(r'.*__version__ = [\'\"](.*?)[\'\"]', re.S)

base_package = 'tpdne'
base_path = os.path.dirname(__file__)

init_file = os.path.join(base_path, 'src', 'tpdne', '__init__.py')
with open(init_file, 'r') as f:
    module_content = f.read()

    match = regexp.match(module_content)
    if match:
        version = match.group(1)
    else:
        raise RuntimeError(
            'Cannot find __version__ in {}'.format(init_file))

with open('README.rst', 'r') as f:
    readme = f.read()

def parse_requirements(filename):
    ''' Load requirements from a pip requirements file '''
    with open(filename, 'r') as fd:
        lines = []
        for line in fd:
            line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines

requirements = parse_requirements('requirements.txt')


if __name__ == '__main__':
    setup(
        name='tpdne',
        description='Get a face that does not exist',
        long_description='\n\n'.join([readme]),
        license='MIT license',
        url='https://github.com/carl-mundy/tpdne',
        version=version,
        author='Carl Mundy',
        author_email='',
        maintainer='Carl Mundy',
        maintainer_email='',
        install_requires=requirements,
        keywords=['tpdne'],
        package_dir={'': 'src'},
        packages=find_packages('src'),
        zip_safe=False,
        classifiers=['Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Programming Language :: Python :: 3.6']
    )
