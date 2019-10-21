import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bybit-ws",
    version="0.1.7",
    author="Simon",
    author_email="simon.zhang@bybit.com",
    description="bybit websocket client",
    url="https://github.com/bybit-exchange/api-connectors/tree/master/official-ws/python",
    packages=setuptools.find_packages(),
    install_requires=[
        'websocket-client==0.53.0',
    ]
)