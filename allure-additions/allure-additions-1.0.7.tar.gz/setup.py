from setuptools import setup

setup(
    name='allure-additions',
    description='pytest plugin for adding additional information into allure report',
    version='1.0.7',
    author='Nikita Kuznetsov',
    packages=[
        'allure_additions',
    ],
    package_dir={'allure_additions': 'allure_additions'},
    install_requires=[
        'pytest>=2',
        'pytest-allure-adaptor>=1.7.10'
    ],
    zip_safe=False,
    include_package_data=True,
    entry_points={'pytest11': ['allure-additions = allure_additions.conftest']},
)
