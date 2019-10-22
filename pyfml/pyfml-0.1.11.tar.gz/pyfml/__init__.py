# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

'''
pyfml - a dynamic configuration (TOML) based factory and dependency injector
for python Callables.

factory builds a DAG of factory callables to allow for
lazy instatiation of a callable as follows:

toyota-factory.toml:

[factory]
factory_id = 'camry-factory'
[[factory.call]]
call_id = 'toyota-camry-id'
callable = 'tests.fixtures.objects.Car'
    [factory.call.kwargs]
    brand = ['brand-id']
    engine = ['engine-id']
[[factory.call]]
call_id = 'enginetype-id'
callable = 'tests.fixtures.objects.EngineType'
    [factory.call.kwargs]
    value = 1
[[factory.call]]
call_id = 'engine-id'
callable = 'tests.fixtures.objects.Engine'
    [factory.call.kwargs]
    engine_type = ['enginetype-id']
[[factory.call]]
call_id = 'brand-id'
callable = 'tests.fixtures.objects.Brand'
    [factory.call.kwargs]
    brand_name = 'Toyota'

Usage:

from pathlib import Path
from pyfml.factory import factory

conf: Path = Path.cwd() / Path('toyota-factory.toml')
meta_factory = factory(conf)
camry_factory = meta_factory('camry-factory')
camry = camry_factory('toyota-camry-id')()

'''
