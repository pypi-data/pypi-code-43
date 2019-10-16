from setuptools import setup, find_packages

setup(
    name="iotile_support_lib_controller_3",
    packages=find_packages(include=["iotile_support_lib_controller_3.*", "iotile_support_lib_controller_3"]),
    version="3.8.1",
    install_requires=['pyparsing>=2.2.1,<3', 'typedargs>=1,<2'],
    entry_points={'iotile.type_package': ['lib_controller_types = iotile_support_lib_controller_3.lib_controller_types'], 'iotile.proxy': ['reference_controller_proxy = iotile_support_lib_controller_3.reference_controller_proxy']},
    include_package_data=True,
    author="Arch",
    author_email="info@arch-iot.com"
)