from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='createFullBOD',
    version='0.0.2',
    description='create full structure of BOD dinamically',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    url='https://github.com/gspagoni/createFullBODWrapper',
    author='Giampaolo Spagoni',
    author_email='giampaolo.spagoni@infor.com',
    license='MIT',
    py_modules=["createFullBOD"],
    package_dir={'': 'src'},
)