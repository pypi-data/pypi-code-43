from setuptools import setup, find_packages

setup(
    name='neptune_dnsoverhttps_protocol',  # How you named your package folder (MyLib)
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),  # Chose the same as "name"
    version='2019.10.14.1809',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    long_description='''# Neptune DNS-over-HTTPS protocol
This is a DNS over HTTPS protocol module for Neptune DNS server
## Installation
```pip3 install neptune_dnsoverhttps_protocol```
''',
    long_description_content_type='text/markdown',
    description='DNS OVER HTTPS PROTOCOL FOR NEPTUNE DNS SERVER',  # Give a short description about your library
    author='Yury (Yurzs)',  # Type in your name
    author_email='dev@best-service.online',  # Type in your E-Mail
    url='https://git.best-service.online/yurzs/neptune-resolver-rest',  # Provide either the link to your github or to your website
    keywords=['NEPTUNE', 'DNS', 'DNSoverHTTPS'],  # Keywords that define your package best
    install_requires=['aiohttp'],
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