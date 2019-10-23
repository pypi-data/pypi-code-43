from setuptools import setup, find_packages

setup(
    name="iotile_support_lib_controller_3",
    packages=find_packages(include=["iotile_support_lib_controller_3.*", "iotile_support_lib_controller_3"]),
    version="3.8.2",
    install_requires=['pyparsing>=2.2.1,<3', 'typedargs>=1,<2'],
    entry_points={'iotile.type_package': ['lib_controller_types = iotile_support_lib_controller_3.lib_controller_types'], 'iotile.proxy_plugin': ['sensorgraph = iotile_support_lib_controller_3.sensorgraph', 'configmanager = iotile_support_lib_controller_3.configmanager', 'controllertest = iotile_support_lib_controller_3.controllertest', 'tilemanager = iotile_support_lib_controller_3.tilemanager', 'remotebridge = iotile_support_lib_controller_3.remotebridge']},
    include_package_data=True,
    author="Arch",
    author_email="info@arch-iot.com"
)