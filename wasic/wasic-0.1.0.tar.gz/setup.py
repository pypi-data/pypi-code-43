from setuptools import setup

setup(
    name='wasic',
    version='0.1.0',
    packages=['wasic'],
    entry_points={'console_scripts': [
        'wasiar = wasic.wasiar:run',
        'wasic = wasic.wasic:run',
        'wasicc = wasic.wasicc:run',
        'wasic++ = wasic.wasicc:run',
        'wasiconfigure = wasic.wasicc:run',
        'wasild = wasic.wasild:run',
        'wasimake = wasic.wasimake:run',
        'wasinm = wasic.wasinm:run',
        'wasiranlib = wasic.wasiranlib:run',
    ]},
)
