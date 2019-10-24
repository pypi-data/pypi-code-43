from setuptools import setup

with open("requirements.txt") as req_file:
    requirements = req_file.readlines()

setup(
    name='oxford_dic',
    version='1.0.4',
    packages=['oxford_dic'],
    author="Michal Polovka",
    author_email="michal.polovka@gmail.com",
    description="CLI interface for Oxford Dictionary",
    url="https://github.com/miskopo/oxford_dic",
    long_description="CLI inteface for Oxford Dictionary using OD API",
    python_requires=">=3.6",
    platforms=["linux"],
    install_requires=requirements,
    license="GPL",
    entry_points={
        'console_scripts': [
            'oxford_dic = oxford_dic.__main__:main'
        ]
    })
