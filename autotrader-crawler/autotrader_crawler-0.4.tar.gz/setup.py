import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='autotrader_crawler',
    version='0.4',
    author='Mark Slater',
    author_email='mark.slater@mail.com',
    description='A package to assist in crawling Autotrader results',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/autotrader-crawler/autotrader-crawler',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
