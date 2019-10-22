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

from pathlib import Path
from typing import Dict, List, Optional
from urllib import request

import toml
from purl import URL as Url

from .dag import Dag
from .typedefs import _factory_call

FML_KEY = 'fml'
FACTORY_KEY = 'factory'
FACTORY_ID_KEY = 'factory_id'
CALL_KEY = 'call'
CALL_ID_KEY = 'call_id'
CALLABLE_KEY = 'callable'
CALL_ARGS_KEY = 'args'
CALL_KW_ARGS_KEY = 'kwargs'
FILE_SCHEME = 'file'


class Conf:
  def __init__(self, factories: Dict):
    self._factories = factories[FACTORY_KEY]

  def to_dags(self) -> List[Dag]:
    return [self._to_dag(f) for f in self._factories]

  @staticmethod
  def _to_dag(factory: Dict) -> Dag:
    dag_id = factory[FACTORY_ID_KEY]
    dag = Dag(dag_id)

    # add nodes
    for call in factory[CALL_KEY]:
      if isinstance(call, dict):
        args = list(call.get(CALL_ARGS_KEY, {}).values())
        node = _factory_call(
          call[CALL_ID_KEY],
          call[CALLABLE_KEY],
          args[0] if (len(args) != 0) else args,
          call.get(CALL_KW_ARGS_KEY, {}),
        )
        dag.add(node.call_id, node)
    # add edges
    for call in factory[CALL_KEY]:
      if isinstance(call, dict):
        call_id = call[CALL_ID_KEY]
        kwargs = call.get(CALL_KW_ARGS_KEY, {})

        for d in [
          # dependencies are lists with 1 item
          v[0] for k, v in kwargs.items()
          if isinstance(v, list) and len(v) == 1
        ]:
          if dag.contains(d):
            dag.add_edge(Dag.edge_(call_id, d))

    return dag


def configure(url: Url) -> Conf:
  """
  Fetch and parse configuration file
  """
  if url.scheme() == FILE_SCHEME:
    return configure_fml(_load_toml(Path(url.path())))
  with request.urlopen(url.as_string()) as response:
    return configure_fml(response.read().decode('utf-8'))


def configure_fml(fml: str) -> Conf:
  """
  Parse configuration file
  """
  return Conf(toml.loads(fml))


def _load_toml(path: Optional[Path]) -> str:
  """
  Simply loads a toml file into a str
  """
  if not path:
    return str()
  return path.read_text()
