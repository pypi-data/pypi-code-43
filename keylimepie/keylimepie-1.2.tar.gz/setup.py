from setuptools import setup


setup(
    name='keylimepie',
    version='v1.2',
    packages=['keylimepie', 'keylimepie.model', 'keylimepie.analysis'],
    scripts=['scripts/makeheader.py', 'scripts/skeylimepie'],
    package_data={
        'keylimepie': ['_interpolation/*.c', '_aux/*.dat', '_aux/*.tab'],
    },
    url='https://gitlab.com/SmirnGreg/keylimepie',
    license='MIT',
    author='Richard Teague, Grigorii V. Smirnov-Pinchukov',
    author_email='smirnov@mpia.de',
    install_requires=[
        'numpy>=1.10',
        'astropy>=2.0',
        'scipy>=1.0',
        'pdoc3',
        'fire',
    ],
    python_requires='>=3.6',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    description='Python tools to run and analyse LIME models'
)
