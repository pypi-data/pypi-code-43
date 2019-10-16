from setuptools import setup
from setuptools import find_packages


requires = ["requests>=2.14.2"]


setup(
    name='naughty_parrot',
    version='0.0.4',
    description='a simple image preprocess tool',
    url='https://github.com/uyuutosa/naughty_parrot',
    author='uyuutosa',
    author_email='sayu819@gmail.com',
    license='MIT',
    keywords='preprocess',
    packages=find_packages(),
    #packages=[
    #        "naughty_parrot",
    #],
    install_requires=["pillow"],
    classifiers=[
            'Programming Language :: Python :: 3.6',
        ],
)
