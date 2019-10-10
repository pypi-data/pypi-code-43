# Copyright 2018 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
import sys
import os


description = ""
if os.path.exists('readme.md'):
    description = open('readme.md', 'r').read()

setup(
    name="c7n_azure",
    version='0.6.1.pre1',
    description="Cloud Custodian - Azure Support",
    long_description=description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Distributed Computing"
    ],
    url="https://github.com/cloud-custodian/cloud-custodian",
    license="Apache-2.0",
    packages=find_packages(),
    entry_points={
        "custodian.resources": [
            'azure = c7n_azure.entry:initialize_azure']
    },
    python_requires=">=3.6",
    install_requires=[
        "PyJWT==1.7.1",
        "PyYAML==5.1.2",
        "adal==1.2.2",
        "applicationinsights==0.11.9",
        "apscheduler==3.6.1",
        "argcomplete==1.10.0",
        "asn1crypto==1.0.1",
        "attrs==19.2.0",
        "azure-cli-core==2.0.74",
        "azure-cli-nspkg==3.0.4",
        "azure-cli-telemetry==1.0.3",
        "azure-common==1.1.23",
        "azure-cosmos==3.1.1",
        "azure-cosmosdb-nspkg==2.0.2",
        "azure-cosmosdb-table==1.0.5",
        "azure-functions==1.0.4",
        "azure-graphrbac==0.61.1",
        "azure-keyvault==1.1.0",
        "azure-mgmt-apimanagement==0.1.0",
        "azure-mgmt-applicationinsights==0.2.0",
        "azure-mgmt-authorization==0.60.0",
        "azure-mgmt-batch==7.0.0",
        "azure-mgmt-cdn==3.1.0",
        "azure-mgmt-cognitiveservices==5.0.0",
        "azure-mgmt-compute==8.0.0",
        "azure-mgmt-containerinstance==1.5.0",
        "azure-mgmt-containerregistry==2.8.0",
        "azure-mgmt-containerservice==7.0.0",
        "azure-mgmt-cosmosdb==0.8.0",
        "azure-mgmt-costmanagement==0.1.0",
        "azure-mgmt-databricks==0.1.0",
        "azure-mgmt-datafactory==0.8.0",
        "azure-mgmt-datalake-nspkg==3.0.1",
        "azure-mgmt-datalake-store==0.5.0",
        "azure-mgmt-dns==3.0.0",
        "azure-mgmt-eventgrid==2.2.0",
        "azure-mgmt-eventhub==3.0.0",
        "azure-mgmt-hdinsight==1.2.0",
        "azure-mgmt-iothub==0.9.0",
        "azure-mgmt-keyvault==2.0.0",
        "azure-mgmt-logic==3.0.0",
        "azure-mgmt-managementgroups==0.2.0",
        "azure-mgmt-monitor==0.7.0",
        "azure-mgmt-network==6.0.0",
        "azure-mgmt-nspkg==3.0.2",
        "azure-mgmt-policyinsights==0.3.1",
        "azure-mgmt-rdbms==1.9.0",
        "azure-mgmt-redis==6.0.0",
        "azure-mgmt-resource==2.1.0",
        "azure-mgmt-sql==0.14.0",
        "azure-mgmt-storage==4.2.0",
        "azure-mgmt-subscription==0.5.0",
        "azure-mgmt-web==0.43.0",
        "azure-nspkg==3.0.2",
        "azure-storage-blob==2.1.0",
        "azure-storage-common==2.1.0",
        "azure-storage-file==2.1.0",
        "azure-storage-queue==2.1.0",
        "backports.functools_lru_cache==1.5",
        "bcrypt==3.1.7",
        "boto3==1.9.247",
        "botocore==1.12.247",
        "c7n>=0.8.45.0",
        "certifi==2019.9.11",
        "cffi==1.12.3",
        "chardet==3.0.4",
        "colorama==0.4.1",
        "cryptography==2.7",
        "distlib==0.2.9.post0",
        "docutils==0.15.2",
        "futures==3.1.1",
        "humanfriendly==4.18",
        "idna==2.8",
        "importlib-metadata==0.23",
        "isodate==0.6.0",
        "jmespath==0.9.4",
        "jsonpatch==1.24",
        "jsonpickle==1.2",
        "jsonpointer==2.0",
        "jsonschema==3.1.1",
        "knack==0.6.3",
        "more-itertools==7.2.0",
        "msrest==0.6.10",
        "msrestazure==0.6.2",
        "netaddr==0.7.19",
        "oauthlib==3.1.0",
        "paramiko==2.6.0",
        "portalocker==1.5.1",
        "pycparser==2.19",
        "pygments==2.4.2",
        "pynacl==1.3.0",
        "pyopenssl==19.0.0",
        "pyrsistent==0.15.4",
        "python-dateutil==2.8.0",
        "pytz==2019.3",
        "pyyaml==5.1.2",
        "requests==2.22.0",
        "requests-oauthlib==1.2.0",
        "s3transfer==0.2.1",
        "setuptools==41.4.0",
        "six==1.12.0",
        "tabulate==0.8.5",
        "tzlocal==2.0.0",
        "urllib3==1.25.6",
        "wheel==0.30.0",
        "zipp==0.6.0",
    ]
)
