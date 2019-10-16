from setuptools import setup, find_packages





setup(
    name='Rabboni',
    version=1.61,
    # packages=find_packages(),
    include_package_data=True,
    packages=find_packages(),
    # package_data = {
    #     # 任何包如果包含 *.txt or *.rst 文件都加进去，可以处理多层package目录结构
    #     '': ['*.dll', '*.lic','*.key'],},
    # package_data={'rabboni': ['_pytransform.dll']},
    install_requires=[
        "matplotlib",
        "pygatt",
        "pywinusb"
    ],
    url='https://github.com/SuiiiDe/Rabboni',
    license='GNU General Public License v3.0',
    author='Sui De',
    author_email='vigia22922@gmail.com',
    description='BLE&USB for Rabboni'
)