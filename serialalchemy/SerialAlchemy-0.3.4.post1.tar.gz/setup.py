from setuptools import setup, find_packages

with open('README.rst') as f:
    long_desc = f.read()

setup(
    name='SerialAlchemy',
    version='0.3.4-1',
    description='Simple object serialization for SQLAlchemy',
    long_description=long_desc,
    # long_description_content_type='text/x-rst',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'SQLAlchemy',
        ],
    url='https://gitlab.com/sloat/SerialAlchemy',
    author='Matt Schmidt',
    author_email='matt@mattptr.net',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.6',
    )

