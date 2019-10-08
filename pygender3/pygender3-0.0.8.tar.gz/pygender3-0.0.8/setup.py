from setuptools import setup, Extension, find_packages

module=Extension(
    'pygender3',
    sources=['pygender3.c'],
)

setup(
    name='pygender3',
    version='0.0.8',
    description='Python3 wrapper for gender.c',
    author='eBrandValue',
    author_email='hostmaster@ebrandvalue.com',
    url='https://github.com/eBrandValue/pygender3',
    license='LGPL',
    packages=find_packages(),
    package_data={
        'pygender3': ['nam_dict.txt'],
    },
    include_package_data=True,
    data_files=[
       ('/var/lib/gender', ['nam_dict.txt'])
    ],
    ext_modules=[module]
)
