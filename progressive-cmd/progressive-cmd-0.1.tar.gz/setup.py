from setuptools import find_packages, setup

test_requires = [
    'pytest',
    'requests_mock'
]

setup(
    name="progressive-cmd",
    version='0.1',
    packages=find_packages(),
    python_requires='>=3.6',
    url='https://github.com/bustawin/progressive-cmd',
    license='AGPLv3 License',
    author='Xavier Bustamante Talavera',
    author_email='xavier@bustawin.com',
    description='Executes a cmd that outputs completion percentages, interpreting '
                'them and executing callbacks with the increment and total percentage.',
    extras_require={
        'testing': test_requires,
    },
    tests_require=test_requires,
    setup_requires=[
        'pytest-runner'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities'
    ]
)
