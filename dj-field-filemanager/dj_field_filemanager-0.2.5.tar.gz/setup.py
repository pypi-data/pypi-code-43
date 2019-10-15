from distutils.core import setup

from setuptools import find_packages

VERSION = '0.2.5'

CLASSIFIERS = [
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
    'Programming Language :: Python :: 3',
    'Environment :: Web Environment',
    'Development Status :: 4 - Beta',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


def get_install_requires():
    """
    parse requirements.txt, ignore links, exclude comments
    """
    requirements = []
    for line in open('requirements.txt').readlines():
        # skip to next iteration if comment or empty line
        if line.startswith('#') or line == '' or line.startswith('http') or line.startswith('git'):
            continue
        # add line to requirements
        requirements.append(line)
    return requirements


setup(
    name='dj_field_filemanager',
    description='Django: Add file manager to a model',
    version=VERSION,
    author='MICRODISSENY GISCUBE SL',
    author_email='tech@microdisseny.com',
    license='MIT License',
    platforms=['OS Independent'],
    url='https://github.com/Microdisseny/django-field-filemanager',
    packages=find_packages(exclude=['__pycache__']),
    include_package_data=True,
    classifiers=CLASSIFIERS,
    zip_safe=False,
    install_requires=get_install_requires()
)
