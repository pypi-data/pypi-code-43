import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cloudcms',
    version='1.0.6',
    author='Michael Whitman',
    author_email='michael.whitman@cloudcms.com',
    description='Cloud CMS Python Driver',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gitana/cloudcms-python-driver',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'oauthlib>=3.0.0',
        'requests>=2.0.0',
        'requests-oauthlib>=1.0.0'
    ]
)