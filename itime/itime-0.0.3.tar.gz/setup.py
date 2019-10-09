from setuptools import setup

setup(
    name='itime',
    description='Awesome time format converter',
    version='0.0.3',
    author='Shelwin Xiao',
    author_email='shliangxiao@gmail.com',
    url='https://github.com/slxiao/itime',
    license='Public Domain',
    keywords=['time', 'format', 'converter'],
    install_requires=['pytz>=2018.7'],
    package_dir={'':'src'},
    py_modules=['itime'],
    setup_requires=['pytz>=2018.7'],
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent'
    ],
)