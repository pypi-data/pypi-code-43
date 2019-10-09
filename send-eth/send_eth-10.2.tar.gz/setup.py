import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
     name='send_eth',
     version='10.2',
     author="Victor A",
     author_email="viktoray007@gmail.com",
     description="An ethereum mass sending package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/victoray/send_eth/",
     packages=['send_eth'],
     install_requires=[
          'web3',
          'blocksmith',
          'eth_utils'
      ],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )