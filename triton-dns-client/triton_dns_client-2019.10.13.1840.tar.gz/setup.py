from setuptools import setup, find_packages

setup(
    name='triton_dns_client',  # How you named your package folder (MyLib)
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),  # Chose the same as "name"
    version='2019.10.13.1840',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    long_description='''# Triton DNS client
Triton is a simple DNS client made for better understanding of DNS protocol

# Installation
## From PYPI 

`pip3 install triton-dns-client`

## From this repo

```bash
git clone https://git.best-service.online/yurzs/triton.git  
cd triton 
python3 setup.py install
```

## How to use

Here is an example query for A record of this gitlab instance
```python3
>>> import triton
>>> a = triton.sync_query('8.8.8.8', 'google.com')
>>> print(a.to_json())
{
    "header": {
        "id": 37920,
        "qr": 1,
        "opcode": 0,
        "aa": 0,
        "tc": 0,
        "rd": 1,
        "ra": 1,
        "z": 0,
        "rcode": 0,
        "qdcount": 1,
        "ancount": 6,
        "nscount": 0,
        "arcount": 0
    },
    "question": [
        {
            "name": "google.com",
            "type": 1,
            "class": 1
        }
    ],
    "answer": [
        {
            "name": "google.com",
            "type": "A",
            "class": 1,
            "ttl": 257,
            "rdata": {
                "address": "64.233.165.113"
            }
        },
        {
            "name": "google.com",
            "type": "A",
            "class": 1,
            "ttl": 257,
            "rdata": {
                "address": "64.233.165.102"
            }
        },
        {
            "name": "google.com",
            "type": "A",
            "class": 1,
            "ttl": 257,
            "rdata": {
                "address": "64.233.165.101"
            }
        },
        {
            "name": "google.com",
            "type": "A",
            "class": 1,
            "ttl": 257,
            "rdata": {
                "address": "64.233.165.139"
            }
        },
        {
            "name": "google.com",
            "type": "A",
            "class": 1,
            "ttl": 257,
            "rdata": {
                "address": "64.233.165.100"
            }
        },
        {
            "name": "google.com",
            "type": "A",
            "class": 1,
            "ttl": 257,
            "rdata": {
                "address": "64.233.165.138"
            }
        }
    ],
    "authority": [],
    "additional": []
}
``` 
For demonstration purposes sync function is used.  
Call ```triton.query``` for async version

## Tree resolve
Also there is experimental full DNS tree resolve function

```python3
>>> import triton
>>> a = triton.sync_full_chain('git.best-service.online', 1)
>>> print(a.to_json())
{
    "header": {
        "id": 45902,
        "qr": 1,
        "opcode": 0,
        "aa": 1,
        "tc": 0,
        "rd": 1,
        "ra": 0,
        "z": 0,
        "rcode": 0,
        "qdcount": 1,
        "ancount": 1,
        "nscount": 1,
        "arcount": 1
    },
    "question": [
        {
            "name": "git.best-service.online",
            "type": 1,
            "class": 1
        }
    ],
    "answer": [
        {
            "name": "git.best-service.online",
            "type": "A",
            "class": 1,
            "ttl": 1000,
            "rdata": {
                "address": "80.211.196.34"
            }
        }
    ],
    "authority": [
        {
            "name": "best-service.online",
            "type": "NS",
            "class": 1,
            "ttl": 100,
            "rdata": {
                "nsdname": "dns-core.best-service.online"
            }
        }
    ],
    "additional": [
        {
            "name": "dns-core.best-service.online",
            "type": "A",
            "class": 1,
            "ttl": 1000,
            "rdata": {
                "address": "163.172.161.149"
            }
        }
    ]
}
```
For demonstration purposes sync function is used.  
Call ```triton.full_chain``` for async version
## TODO List
- [ ] Enable EDNS
- [ ] Add DNSSEC Resource Record types

## List of available resource record types
- [x] A
- [x] AAAA
- [X] NS
- [x] TXT
- [x] SOA
- [x] OPT
- [x] RRSIG
- [x] DNSKEY
- [x] DS
- [x] NSEC
- [x] NSEC3
- [x] NSEC3PARAM

## Currently supported DNSSEC algorithms
- [x] RSASHA1
- [x] RSASHA256
- [x] RSASHA512
- [ ] ECCGOST
- [ ] RSA_NSEC3_SHA1
- [ ] DSA
- [ ] DSA_NSEC3_SHA1
- [ ] ECDSAP256SHA256
- [ ] ECDSAP256SHA384
- [ ] ED448
- [ ] ED25519''',
    long_description_content_type='text/markdown',
    description='Async DNS client',  # Give a short description about your library
    author='Yury (Yurzs)',  # Type in your name
    author_email='dev@best-service.online',  # Type in your E-Mail
    url='https://git.best-service.online/yurzs/triton',  # Provide either the link to your github or to your website
    keywords=['triton', 'DNS', 'client'],  # Keywords that define your package best
    install_requires=['bitstring', 'pycryptodomex'],
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