import setuptools

setuptools.setup(
    name='z3-tracker',
    version='0.9.6',
    author='Feneg',
    description='Helper program for Link to the Past randomiser',
    url='https://www.github.com/feneg/z3-tracker',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment',
        'Topic :: Utilities'],
    entry_points={
        'gui_scripts': (
            'z3-tracker = z3tracker.main:main',
            'z3tracker = z3tracker.main:main')}
    )
