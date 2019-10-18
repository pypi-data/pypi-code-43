from setuptools import setup, find_packages

setup(
    name='comagic-wrapper',
    version='0.0.4.2',
    packages=find_packages(),
    install_requires = [
        'requests>=2.18.2'
    ],
    description='Comagic wrapper',
    author='bzdvdn',
    author_email='bzdv.dn@gmail.com',
    url='https://github.com/bzdvdn/comagic-dataapi-wrapper.git',
    license='MIT',
    python_requires=">=3.6",
)
