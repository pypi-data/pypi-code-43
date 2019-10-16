from setuptools import setup, find_packages

setup(
    name="iotile_support_lib_controller_4",
    packages=find_packages(include=["iotile_support_lib_controller_4.*", "iotile_support_lib_controller_4"]),
    version="4.0.0",
    install_requires=['pyparsing>=2.2.1,<3', 'typedargs>=1,<2'],
    entry_points={'iotile.proxy': ['reference_controller_proxy = iotile_support_lib_controller_4.reference_controller_proxy'], 'iotile.type_package': ['lib_controller_types = iotile_support_lib_controller_4.lib_controller_types']},
    include_package_data=True,
    author="Arch",
    author_email="info@arch-iot.com"
)