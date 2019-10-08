from setuptools import setup

setup(name='brail',
    version='0.2',
    description='Command-line tool for managing releases',
    url='http://github.com/Portchain/brail',
    author='Sergei Patiakin',
    author_email='sergei.patiakin@gmail.com',
    license='MIT',
    packages=['brail'],
    scripts=['bin/brail'],
    zip_safe=False,
)