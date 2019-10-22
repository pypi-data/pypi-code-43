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

from collections import deque, namedtuple
from types import MappingProxyType
from typing import Dict, Iterator, List, Mapping

from .typedefs import A


def i_keys(d: Dict[str, A], **kw) -> Iterator[str]:
  return iter(d.keys(**kw))


def i_values(d: Dict[str, A], **kw) -> Iterator[A]:
  return iter(d.values(**kw))


class Dag:
  edge_ = namedtuple('edge', ['src', 'dest'])

  class node_:
    def __init__(self, value: A):
      self.__value = value
      self.__edges = set()

    def get_value(self) -> A:
      return self.__value

    def get_edges(self):
      return frozenset(self.__edges)

    def add_edge(self, node_name: str):
      if node_name not in self.__edges:
        self.__edges.add(node_name)

    def rem_edge(self, node_name: str):
      if node_name in self.__edges:
        self.__edges.remove(node_name)


  def __init__(self, dag_id: str):
    self.__nodes = dict()
    self.dag_id = dag_id

  @property
  def nodes(self) -> Mapping[str, 'node_']:
    return MappingProxyType(self.__nodes)

  def contains(self, key: str) -> bool:
    return self.__nodes.__contains__(key)

  def size(self):
    return len(self.__nodes)

  def add(self, name: str, node: A) -> bool:
    res = node is not None
    if res:
      self.__nodes[name] = Dag.node_(node)
    return res

  def rem(self, name: str):
    if name in self.__nodes:
      self.__nodes.pop(name)
    for node in i_values(self.__nodes):
      node.rem_edge(name)

  def add_edge(self, e: edge_) -> bool:
    exists = e.src in self.__nodes and e.dest in self.__nodes
    if exists:
      self.__nodes[e.src].add_edge(e.dest)
    return exists

  def rem_edge(self, e: edge_) -> bool:
    exists = e.src in self.__nodes and e.dest in self.__nodes
    if exists:
      self.__nodes[e.src].rem_edge(e.dest)
    return exists

  def mv_edge(self, old_edge: edge_, new_edge: edge_) -> bool:
    exists = self.rem_edge(old_edge)
    if exists:
      self.add_edge(new_edge)
    return exists

  def terminals(self) -> List['node_']:
    return [
      n for n in i_values(self.__nodes)
      if len(n.get_edges()) == 0
    ] # yapf: disable

  def parents(self, node_name: str) -> List['node_']:
    return [
      n for n in i_values(self.__nodes)
      if node_name in n.get_edges()
    ] # yapf: disable

  def children(self, node_name: str) -> List['node_']:
    res = []
    if node_name in self.__nodes:
      res = [self.__nodes[n] for n in self.__nodes[node_name].get_edges()]
    return res

  def to_list(self) -> List['node_']:
    return [self.__nodes[n] for n in kahn_topsort(self)]


# from https://algocoding.wordpress.com/2015/04/05/topological-sorting-python/
def kahn_topsort(graph: Dag, reverse: bool = True) -> List[str]:
  in_degree = {u: 0 for u in graph.nodes}

  for u in graph.nodes:
    for v in graph.nodes[u].get_edges():
      in_degree[v] += 1

  Q = deque()

  for u in in_degree:
    if in_degree[u] == 0:
      Q.appendleft(u)

  L = []

  while Q:
    u = Q.pop()
    L.append(u)
    for v in graph.nodes[u].get_edges():
      in_degree[v] -= 1
      if in_degree[v] == 0:
        Q.appendleft(v)
  if reverse:
    L.reverse()

  return L if len(L) == graph.size() else []
