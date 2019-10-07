from setuptools import setup

setup(
    name="krypto",
    version='9.3.0',
    description="encrypt files and data",
    long_description="encrypt files and data using a secure AES256 key",
    author="krish",
    author_email="krishgarg19@gmail.com",
    url="https://github.com/techiekrish",
    license=" ",
    py_modules=['krypto'],
    install_requires=[
        'Pillow==6.1.0',
        'cryptography==2.7',
        'licensing==0.10',
        'pycryptodome==3.9.0'
    ],
    entry_points='''
        [console_scripts]
        krypto=krypto:main
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7'
    ]
)