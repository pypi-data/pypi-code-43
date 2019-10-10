from setuptools import setup, find_packages

setup(
    name='Snail-JueweiPotSchedule',
    version='0.0.2',
    description='Juewei Pot Schedule',
    keywords=('snail', 'juewei', 'schedule'),

    author='Snail',
    author_email='snail_email@163.com',

    packages=find_packages(),

    # 需要安装的依赖
    install_requires=[
        'ortools>=7.3.7083',
        'openpyxl>=2.6.3',
        'flask>=1.1.1',
        'flask_restful>=0.3.7'
    ]
)

