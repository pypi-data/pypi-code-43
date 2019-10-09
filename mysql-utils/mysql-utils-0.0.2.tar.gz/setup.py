from setuptools import setup

setup(
    name='mysql-utils',
    description='A simple MySQL library including a set of utility APIs for Python database programming',
    version='0.0.2',
    author='Shelwin Xiao',
    author_email='shliangxiao@gmail.com',
    url='https://github.com/slxiao/mysql-utils',
    license='Public Domain',
    keywords=['mysql', 'API', 'utility'],
    install_requires=['mysql-connector>=2.2.9'],
    package_dir={'':'src'},
    py_modules=['mysql_utils'],
    setup_requires=['mysql-connector>=2.2.9'],
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
