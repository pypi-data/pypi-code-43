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

from typing import Callable, Dict, KeysView, Mapping
from purl import URL as Url
from .internal.callables import LazyCallable, lazy_prototype, prototype
from .internal.conf import configure, configure_fml
from .internal.dag import Dag
from .internal.typedefs import A, _factory_call


def factory(*urls: Url) -> Callable[[str], A]:
  """
  A Callable Factory. Given one or more url(s) objects to .toml fml config,
  this function provides a "meta factory" which should be cached by
  the caller. factory builds a DAG of factory callables to allow for
  lazy instatiation of a callable as follows:

    conf = Path.cwd() / Path('tests/fixtures/objects.toml')
    meta_factory = factory(Url(conf.to_uri()))
    concrete_factory = meta_factory('factory_id')
    callable = concrete_factory('call_id')
    result = callable()

  Args:
    confs: (*Url) one or more Url objects to .toml fml config

  Returns:
    Callable[[str], A] that provides access to 1 or more factories
  """
  dags = list()
  for url in urls:
    c = configure(url)
    dags.extend(c.to_dags())
  dag_callables = {dag.dag_id: _to_factory(dag) for dag in dags}
  return lambda fid: dag_callables[fid]


def factory_fml(*fmls: str) -> Callable[[str], A]:
  """
  A Callable Factory. Given one or more TOML strings,
  this function provides a "meta factory" which should be cached by
  the caller. factory builds a DAG of factory callables to allow for
  lazy instatiation of a callable as follows:

    fml = '[[factory]] ...'
    meta_factory = factory_fml(fml)
    concrete_factory = meta_factory('factory_id')
    callable = concrete_factory('call_id')
    result = callable()

  Args:
    fmls: (*str) one or more factory markup language strings

  Returns:
    Callable[[str], A] that provides access to 1 or more factories
  """
  dags = list()
  for fml in fmls:
    c = configure_fml(fml)
    dags.extend(c.to_dags())
  dag_callables = {dag.dag_id: _to_factory(dag) for dag in dags}
  return lambda fid: dag_callables[fid]


def _to_factory(dag: Dag) -> Callable[[str], A]:
  callables = dict()

  # terminal nodes have no dependencies outside of scalar values
  for n in dag.terminals():
    fc = n.get_value()
    callables[fc.call_id] = _to_call(fc)

  # topological sort and add memoized calls
  for n in dag.to_list():
    fc = n.get_value()
    if fc.call_id not in callables:
      callables[fc.call_id] = _to_memoized_call(callables, fc)

  def factory_fn(call_id: str) -> Callable[[str], A]:
    return callables[call_id]

  return Factory(factory_fn, dag)


def _to_call(fc: _factory_call) -> Callable[..., A]:
  mod_name, call_name = _module_and_call_name(fc)
  return prototype(mod_name, call_name, fc.args, fc.kwargs)


def _to_memoized_call(calls: Dict[str, Callable[[str], A]], fc: _factory_call):
  mod_name, call_name = _module_and_call_name(fc)
  keys = calls.keys()
  kwargs = dict()
  for kv in fc.kwargs.items():
    if (_is_callable(kv[1], keys)):
      call_id = kv[1][0]
      k = kv[0]
      kwargs[k] = LazyCallable(calls[call_id])
    else:
      kwargs.update(kv)
  return lazy_prototype(mod_name, call_name, fc.args, kwargs)


def _module_and_call_name(factory_call: _factory_call):
  mod_call = factory_call.callable.rsplit('.', 1)
  # check to see if it is a builtin
  if len(mod_call) == 1 and (mod_call[0] in globals()['__builtins__']):
    return ('builtins', mod_call[0])
  return factory_call.callable.rsplit('.', 1)


def _is_callable(obj: A, kv: KeysView) -> bool:
  return isinstance(obj, list) and len(obj) == 1 and obj[0] in kv


class Factory:
  def __init__(self, call: Callable[[str], A], dag: Dag):
    self._callable = call
    self._dag = dag

  def dag_nodes(self) -> Mapping[str, Dag.node_]:
    return self._dag.nodes

  def __call__(self, *arg):
    return self._callable(*arg)
