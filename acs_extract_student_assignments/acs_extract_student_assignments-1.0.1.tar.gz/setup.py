from setuptools import setup


setup(
    name='acs_extract_student_assignments',
    version='1.0.1',
    url='https://github.com/petarmaric/acs_extract_student_assignments',
    license='BSD',
    author='Petar Maric',
    author_email='petarmaric@uns.ac.rs',
    description='Console app and Python API for extracting assignments from '\
                'exam archives of our ACS students',
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
        'acs_extract_student_assignments',
    ],
    entry_points={
        'console_scripts': [
            'acs_extract_student_assignments=acs_extract_student_assignments:main',
        ],
    },
    extras_require={
        'dev': [
            'pylint~=1.9',
        ],
    },
)
