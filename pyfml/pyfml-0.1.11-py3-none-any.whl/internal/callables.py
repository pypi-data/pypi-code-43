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

from importlib import import_module
from logging import log, ERROR
from typing import Any, Callable, Dict, List, Optional
from .typedefs import A, B


def import_call(mod: str, attr: str) -> Callable[[A], B]:
  module_path = import_module(mod)
  try:
    return getattr(module_path, attr)
  except AttributeError:
    raise ImportError(f'module {module_path} attr {attr}')


def call(
    mod: str,
    call_name: str,
    args: List[Any] = None,
    kwargs: Dict[str, Any] = None
) -> Callable[..., A]:
  call_ = import_call(mod, call_name)

  def _callable_() -> Callable[..., A]:
    if len(kwargs) == 0:
      return call_(args)
    return call_(**kwargs)

  return _callable_


def prototype(
    mod: str, call_name: str, args: List[Any], kwargs: Dict[str, Any]
) -> Callable[..., B]:

  call_ = import_call(mod, call_name)

  def _callable_(*argv, **kwa) -> Callable[..., B]:
    # allow override of params
    kw_args = {**kwargs, **kwa}
    arg_v = argv
    if len(arg_v) == 0:
      arg_v = args
    if len(kw_args) == 0:
      return call_(arg_v)
    else:
      return call_(**kw_args)

  return _callable_


def lazy_prototype(
    mod: str, call_name: str, args: List[Any], kwargs: Dict[str, Any]
) -> Callable[..., B]:
  call_ = import_call(mod, call_name)

  def __invoke_if_lazy(a: Any):
    if isinstance(a, LazyCallable):
      return a()
    return a

  def _callable_(*argv, **kwa) -> Callable[..., B]:
    # allow override of params
    kw_args = {**kwargs, **kwa}
    if len(kw_args) != 0:
      kw_args.update({
        kv[0]: __invoke_if_lazy(kv[1])
        for kv in kw_args.items()
      })

    arg_v = argv
    if len(arg_v) == 0:
      arg_v = args
    if len(kw_args) == 0:
      return call_(arg_v)
    return call_(**kw_args)

  return _callable_


def safe_call(c: Callable[[A], B], kwargs: Dict[str, Any]) -> Optional[B]:
  try:
    return c(**kwargs)
  except Exception as e:
    log(ERROR, f"call failed, err: {e}")
  return None


class LazyCallable:
  def __init__(self, c: Callable[..., B]):
    self._callable = c

  def __call__(self, *args, **kwargs):
    if len(kwargs) == 0:
      return self._callable()
    return self._callable(**kwargs)
