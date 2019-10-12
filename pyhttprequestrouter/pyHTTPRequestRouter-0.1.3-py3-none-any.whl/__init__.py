# EMACS settings: -*-  tab-width: 2; indent-tabs-mode: t -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
#
# =============================================================================
#               _   _ _____ _____ ____  ____                            _   ____             _
#   _ __  _   _| | | |_   _|_   _|  _ \|  _ \ ___  __ _ _   _  ___  ___| |_|  _ \ ___  _   _| |_ ___ _ __
#  | '_ \| | | | |_| | | |   | | | |_) | |_) / _ \/ _` | | | |/ _ \/ __| __| |_) / _ \| | | | __/ _ \ '__|
#  | |_) | |_| |  _  | | |   | | |  __/|  _ <  __/ (_| | |_| |  __/\__ \ |_|  _ < (_) | |_| | ||  __/ |
#  | .__/ \__, |_| |_| |_|   |_| |_|   |_| \_\___|\__, |\__,_|\___||___/\__|_| \_\___/ \__,_|\__\___|_|
#  |_|    |___/                                      |_|
# =============================================================================
# Authors:						Patrick Lehmann
#
# Python module:	    HTTP Request Router.
#
# Description:
# ------------------------------------
#		TODO
#
# License:
# ============================================================================
# Copyright 2017-2019 Patrick Lehmann - Bötzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
#
from typing import List

from pyGenericPath                  import SystemMixIn
from pyHTTPInterface                import HTTPMethods, Request
from pyHTTPRequestRouter.Attributes import RoutingAttribute, GETRoute, POSTRoute, DELETERoute


class Route():
	_path :         str =         None
	_httpMethods :  HTTPMethods = None
	_callable =                   None

	def __init__(self, path, httpMethods, callable):
		self._path =        path
		self._httpMethods = httpMethods
		self._callable =    callable

	def __str__(self):
		return "{method}: {path!s}".format(method=self._httpMethods.to_simple_str(), path=self._path)


class Router(SystemMixIn):
	_api = None
	__routes : List = None

	def __init__(self, api):
		self._api = api

		self.__routes = []

		lst = []
		Router.iterate(lst, api)

		print("  ------")
		for funcname, func in lst:
			print("  ", funcname, " - ", func)

			for routeAttribute in RoutingAttribute.GetAttributes(func):
				route = routeAttribute.Route
				print("    ", route)
				self.__routes.append(route)

		print("  ------")

			#for routeAttribute in RoutingAttribute.GetAttributes(func):
			#	self.__routes.append(routeAttribute.GetRoute)

	@staticmethod
	def iterate(lst : List, node):

		for funcname, func in RoutingAttribute.GetMethods(node):
			lst.append((funcname, func))

		for child in node.ChildNodes:
			Router.iterate(lst, child)

	def Serve(self, request: Request):
		print("serve: ", request._path.Path)
