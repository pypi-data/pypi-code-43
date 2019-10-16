"""
   Copyright 2018 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from setuptools import setup

VERSION = __import__('globomap_plugin_zabbix').__version__

setup(
    name='globomap-plugin-zabbix',
    version=VERSION,
    description='Zabbix monitoring plugin on globomap-api',
    author='Storm',
    author_email='storm@corp.globo.com',
    url='https://gitlab.globoi.com/globomap/globomap-plugin-zabbix',
    packages=['globomap_plugin_zabbix'],
    package_data={'globomap_plugin_zabbix': ['*.py']},
)
