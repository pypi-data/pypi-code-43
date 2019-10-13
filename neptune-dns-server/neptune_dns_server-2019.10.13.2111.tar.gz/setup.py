from setuptools import setup, find_packages

setup(
    name='neptune_dns_server',  # How you named your package folder (MyLib)
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),  # Chose the same as "name"
    version='2019.10.13.2111',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    long_description='''# Neptune DNS Server
Neptune is asynchronous modular DNS server made for flexibility and easy modifications
Its based on Triton dns client and uses different modules to extend it to full server
## Installation
### From PYPI
```
pip3 install neptune-dns-server
```
### From this repo

```
git clone https://git.best-service.online/yurzs/neptune
cd neptune
python3 setup.py install
```
## Usage 
Please edit config.py file for your configuration. Basic install uses 1.1.1.1 and 8.8.8.8 as a resolvers with local redis cache  
To start server use a simple command
```
import neptune
neptune.start_server()
```

TODO write more docs''',
    long_description_content_type='text/markdown',
    description='Async DNS server',  # Give a short description about your library
    author='Yury (Yurzs)',  # Type in your name
    author_email='dev@best-service.online',  # Type in your E-Mail
    url='https://git.best-service.online/yurzs/neptune',  # Provide either the link to your github or to your website
    keywords=['triton', 'DNS', 'client'],  # Keywords that define your package best
    install_requires=['neptune-cache-redis', 'neptune-dnsoverhttps-protocol', 'neptune-resolver-default', 'neptune-resolver-rest', 'triton-dns-client'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.7',
    ],
)