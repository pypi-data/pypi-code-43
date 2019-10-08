from setuptools import setup, Extension, find_packages

module=Extension(
    'pygender3',
    sources=['pygender3.c'],
)

setup(
    name='pygender3',
    version='0.0.9',
    description='Python3 wrapper for gender.c',
    author='Doğukan ÇELİK',
    author_email='celikd@itu.edu.tr',
    url='https://github.com/dgkncelik/pygender3',
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
