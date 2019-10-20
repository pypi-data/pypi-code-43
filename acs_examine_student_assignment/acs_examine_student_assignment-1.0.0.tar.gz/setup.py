from setuptools import setup


setup(
    name='acs_examine_student_assignment',
    version='1.0.0',
    url='https://github.com/petarmaric/acs_examine_student_assignment',
    license='BSD',
    author='Petar Maric',
    author_email='petarmaric@uns.ac.rs',
    description='Console app and Python API for automated assignment '\
                'examination of our ACS students',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
        'Topic :: Utilities',
    ],
    py_modules=[
        'acs_examine_student_assignment',
    ],
    entry_points={
        'console_scripts': [
            'acs_examine_student_assignment=acs_examine_student_assignment:main',
        ],
    },
    install_requires=[
        'smoke_test~=1.0',
    ],
    extras_require={
        'dev': [
            'pylint~=1.9',
        ],
    },
)
