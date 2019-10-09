from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

with open('requirements-for-release.txt', 'r') as f:
    install_requires_for_release = f.read().splitlines()

setup(
    name='fermat',
    version='0.1.0',
    python_requires='>=3.5',
    description='library to compute fermat distance',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://bitbucket.org/aristas/fermat',
    license='MIT',
    author='Facundo Sapienza',
    author_email='f.sapienza@aristas.com.ar',
    setup_requires=install_requires,
    install_requires=install_requires_for_release,
    packages=['fermat', 'fermat.path_methods'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
