from setuptools import setup, find_packages

setup(
    name='SONYC_CAPSTONE_VIS',
    version='0.1', # version只能是数字，还有其他字符则会报错
    keywords=['SONYC', 'visualization'],
    description='SONYC Capstone Visualization Pacakge',
    long_description='',
    license='MIT',
    install_requires=["matplotlib", "numpy", "pandas"],
    author='Biao',
    author_email='biaoh66@gmail.com',
    packages=find_packages(), # 项目内所有自己编写的库
    platforms='any',
    url='https://github.com/Distancs/SONYC_CAPSTONE_VIS'
)
