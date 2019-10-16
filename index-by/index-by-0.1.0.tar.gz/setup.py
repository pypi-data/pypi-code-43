from setuptools import setup


setup(
    name='index-by',
    version='0.1.0',
    url='https://github.com/twiebe/py-index-by',
    license='BSD',
    author='Thomas Wiebe',
    author_email='code@heimblick.net',
    description='Index objects in a sequence easily',
    long_description='Index objects in a sequence easily',
    package_dir={'': 'src'},
    packages=['index_by', 'index_by.modifiers'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    test_suite='tests',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
