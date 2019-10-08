from setuptools import setup, find_packages

setup(
    name='list_based_flavorpack',
    version='2.0.7',
    packages=find_packages(),
    include_package_data=True,
    url='https://gitlab.com/serial-lab/list_based_flavorpack',
    license='GPLv3',
    author='SerialLab Corp',
    author_email='slab@serial-lab.com',
    description='Generic List-Based Flavorpack Plugin for SerialBox',
    keywords=('seriallab, quartet, list-based, list, serialbox, '
             'level-4 quartet'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
