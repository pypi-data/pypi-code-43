from setuptools import setup, find_packages

setup(
    author='Oleg Gaidukov',
    name='ton-client',
    version='0.5.1',
    description='ton client',
    packages=['ton_client'],
    install_requires=[
        "ed25519~=1.5",
        "ujson>=1.35",
        "uvloop",
        "mnemonic",
        "crc16"
    ],
    package_data={
        'ton_client': [
            'distlib/darwin/*',
            'distlib/linux/*',
        ]
    },
    zip_safe=True,
    keywords='ton gram',
    python_requires='>=3.7',
)
