import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()
# 
# with open('requirements.txt') as f:
#     required = f.read().splitlines()
 

setuptools.setup(
    name='featurize-package',
    description='Official packages for featurize.',
    version='0.0.3',
    packages=setuptools.find_packages(),
    url="https://github.com/louis-she/featurize-package",
    author='louis',
    author_email='chenglu.she@gmail.com',
    keywords='pytorch minecraft',
    include_package_data=True,
    # install_requires=required,
    # entry_points={
    #     'console_scripts': ['minetorch=minetorch.cli:cli'],
    # }
)
