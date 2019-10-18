import setuptools

setuptools.setup(
    name="anduschain",
    version="1.0.0",
    license='MIT',
    author="andus",
    author_email="kmha@andusdeb.com",
    description="anduschain-python SDK ( web3.py wrapped )",
    long_description=open('README.md').read(),
    url="https://github.com/anduschain/anduschain-python",
    packages=setuptools.find_packages(),
    classifiers=[
        # 패키지에 대한 태그
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
