from setuptools import setup, find_packages

setup(
    name="iotile_support_con_nrf52832_4",
    packages=find_packages(include=["iotile_support_con_nrf52832_4.*", "iotile_support_con_nrf52832_4"]),
    version="4.0.0.dev9",
    install_requires=['iotile_support_lib_controller_4 >= 4.0.0.dev7, == 4.*'],
    entry_points={'iotile.proxy': ['nrf52832_controller = iotile_support_con_nrf52832_4.nrf52832_controller']},
    include_package_data=True,
    author="Arch",
    author_email="info@arch-iot.com"
)