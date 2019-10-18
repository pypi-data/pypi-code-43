import setuptools


setuptools.setup(
    name="avro_codec",
    version="2.0.0",
    author="Data and Analytics",
    author_email="data@gc.com",
    description="An avro codec which exposes an API similar to the standard library's marshal, pickle and json modules",
    license="MIT",
    keywords="avro encode decode codec",
    url="http://github.com/gamechanger/avro_codec",
    packages=["avro_codec"],
    long_description="",
    install_requires=['avro==1.7.7', 'fastavro==0.22.5'],
    tests_require=['nose']
)
