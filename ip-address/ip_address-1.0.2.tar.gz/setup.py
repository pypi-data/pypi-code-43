import setuptools

with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author="Thomas Dewitte",
    author_email="thomasdewittecontact@gmail.com",

    name='ip_address',
    version='1.0.2',
    license="MIT",
    url='https://github.com/dewittethomas/ip-address',
    python_requires='>= 2.7',
    
    description='Gets your ip',
    long_description=README,
    long_description_content_type="text/markdown",

    package_dir={"ip_address": "ip_address"},
    install_requires=["requests>=2.22.0"],
    
    packages=setuptools.find_packages(),

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)