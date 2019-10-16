import setuptools

setuptools.setup(
    name="local_lambda_kinesis",
    version="0.0.5",
    author="Koby Bass",
    description="Tool for testing lambda kinesis handlers locally using real data",
    url="https://github.com/kobybum/local-lambda-kinesis",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    scripts=["bin/lambda_kinesis"],
    install_requires=["boto3>=1.9.236"],
)
