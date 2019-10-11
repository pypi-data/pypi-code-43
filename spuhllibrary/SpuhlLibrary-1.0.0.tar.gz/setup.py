from setuptools import setup

setup(
    name='SpuhlLibrary',
    version='1.0.0',
    packages=['tests', 'tests.IoTEdgeMessagePublisher', 'package', 'package.IoTEdgeMessagePublisher'],
    url='https://github.com/sagerpascal/Spuhl_IoT_Solution',
    license='',
    author='Luca Staehli, Pascal Sager',
    author_email='',
    description='Azure IoT Library from Spuhl GmbH',
    test_suite="tests",
    install_requires=['azure-iothub-device-client~=1.4.3']
)
