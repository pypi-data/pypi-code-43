from setuptools import setup

with open('README.md', 'r') as f:
    README = f.read()

setup(
    name="aio_ormsql",
    version="0.0.1",
    author="TheDevFromKer",
    license="GNU 3.0",
    description="Simple asynchronous MySQL ORM class.",
    url="https://github.com/TheDevFromKer/aio_ormsql",
    packages=[str('aio_ormsql')],
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=['python mysql', 'async mysql python', 'mysql python'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=["asyncio", "aiomysql"]
)
