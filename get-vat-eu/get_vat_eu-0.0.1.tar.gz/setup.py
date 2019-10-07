#
# setup.py
#
# Copyright (c) 2019 CityCommerce srl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup, find_packages

setup(
    name='get_vat_eu',
    version='0.0.1',
    packages=find_packages(exclude=['*tests*']),
    license='MIT',
    description='A utility that is able to get and parse EU EC VATs.',
    long_description=open('README.rst').read(),
    package_data={
        '': ['*.txt', '*.rst'],
    },
    author='CityCommerce',
    author_email='citycommercedev@gmail.com',
    keywords='vat ec eu',
    url='https://github.com/citycommerce/get-vat-eu',
    python_requires='>=3.5, <4',
    entry_points={
        'console_scripts': [
            'get_vat_eu=get_vat_eu.__main__:main',
        ],
    },
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['zeep==3'],
)

