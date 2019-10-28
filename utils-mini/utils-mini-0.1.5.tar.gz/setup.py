from setuptools import setup, find_packages

setup(
    name='utils-mini',
    version='0.1.5',
    description=('python的一些简单的工具方法',
                 'Some simple tools and methods of Python'),
    long_description=open('README.rst', 'rb').read(),
    author='beincy',
    author_email='bianhui0524@sina.com',
    maintainer='卞辉(beincy)',
    maintainer_email='bianhui0524@sina.com',
    license='MIT',
    packages=['utilsMini'],
    platforms=["all"],
    install_requires=[
        'ujson'
    ],
    url='https://github.com/beincy/utils-mini',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)