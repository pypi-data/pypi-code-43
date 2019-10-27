from setuptools import setup, find_packages

setup(
    name='saturn_proxy_server',  # How you named your package folder (MyLib)
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),  # Chose the same as "name"
    version='0.6',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    long_description='''# Socks5 async proxy server
Saturn is a SOCKS5 server based on asyncio protocols
## Installation
### From [pypi.org](https://pypi.org/project/saturn-proxy-server/)
```bash
pip install saturn-proxy-server
```
### From this repo
```bash
git clone https://git.best-service.online/yurzs/saturn.git
cd saturn
python3 ./setup.py install
```
## Usage
Please edit `config.py` file before starting your server.  
By default proxying allowed to all hosts (`ALLOWED_DESTINATIONS =  ["0.0.0.0/0"]`).  You can specify single IP addresses 
(both IPv4 and IPv6) and subnets. 
```python3
import saturn
saturn.config.ALLOWED_DESTINATIONS = ["192.168.1.0/24"]
saturn.config.AUTHENTICATION_METHODS = ["saturn.auth.none"]
saturn.start_server("127.0.0.1", 8080) 
```
This config will allow passwordless connections with allowed proxying for `192.168.1.0-192.169.1.255` IP range.
You can use multiple auth methods at once like `["saturn.auth.none", saturn.auth.dict"]`
## Authentication methods
Current SOCKS5 standart supports
- [x] None ["saturn.auth.none"]
- [ ] GSSAPI ["saturn.auth.gssapi"]
- [x] Login/Password (dict format) ["saturn.auth.dict"]
### Custom authentication methods
You can implement your own authentication method (Login/Password)  
All you need to do is to implement `Authenticator` class with `async def authenticate(self, data)` method which will return `bool`
authentication result. Then just import your module and use it in config  
`saturn.config.AUTHENTICATION_METHODS = ["your_auth_method"]`
You can see examples in `saturn.auth`

### TODO list
- [ ] Logging
- [ ] Max socket limit
- [ ] More tests''',
    long_description_content_type='text/markdown',
    description='Socks5 async proxy server',  # Give a short description about your library
    author='Yury (Yurzs)',  # Type in your name
    author_email='dev@best-service.online',  # Type in your E-Mail
    url='https://git.best-service.online/yurzs/saturn',  # Provide either the link to your github or to your website
    keywords=['Saturn', 'Socks5', 'proxy'],  # Keywords that define your package best
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