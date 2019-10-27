from setuptools import setup
#from distutils.core import setup

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name='qtpi_test_kernel',
    version='0.1.4',
    packages=['qtpi_test_kernel'],
    description='Simple example of qtpi test kernel python wrapper for Jupyter to enable Qtpi quantum language',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='Jupyter Development Team',
    author_email='jupyter@googlegroups.com',
    url='https://github.com/miroslav14/qtpi_test_kernel.git',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel'
    ],
   
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
)
