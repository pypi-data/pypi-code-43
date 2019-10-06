from setuptools import setup, find_packages

setup(
    name='kernunos',
    version='19.10.0-dev',
    packages=find_packages(),
    install_requires=['argparse'],
    author='Andre Guerra',
    author_email='agu3rra@gmail.com',
    description='kernunos: automated wep app security reconnaissance.',
    long_description='kernunos: automated wep app security reconnaissance.',
    url='https://gitlab.com/agu3rra/kernunos',
    license='MIT',
    keywords='web application reconnaissance automation'
)