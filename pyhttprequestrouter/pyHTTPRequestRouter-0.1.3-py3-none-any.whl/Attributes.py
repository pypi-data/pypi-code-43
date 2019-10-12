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
# Python module:	    pyAttributes for ReST APIs
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
from pyAttributes     import Attribute, AttributeHelperMixin
from pyHTTPInterface  import HTTPMethods


__api__ = [
	'RoutingAttribute',
	'GETRoute',
	'POSTRoute',
	'PUTRoute',
	'DELETERoute'
]
__all__ = __api__


class RoutingAttribute(Attribute):
	_route = None

	def __init__(self, path, httpMethods : HTTPMethods):
		super().__init__()

		from . import Route

		self._route = Route(path, httpMethods, None)

	@property
	def Route(self):
		return self._route

	@property
	def Path(self):
		return self._route._path

	@property
	def HTTPMethods(self):
		return self._route._httpMethods


class GETRoute(RoutingAttribute):
	def __init__(self, path):
		super().__init__(path, HTTPMethods.GET)


class POSTRoute(RoutingAttribute):
	def __init__(self, path):
		super().__init__(path, HTTPMethods.POST)


class PUTRoute(RoutingAttribute):
	def __init__(self, path):
		super().__init__(path, HTTPMethods.PUT)


class DELETERoute(RoutingAttribute):
	def __init__(self, path):
		super().__init__(path, HTTPMethods.DELETE)


class ReSTAPIMixin(AttributeHelperMixin):
	__routes = None

	def __init__(self, **kwargs):
		super().__init__()

		self.__routes = []

		for _, func in RoutingAttribute.GetMethods(self):
			for routeAttribute in RoutingAttribute.GetAttributes(func):
				self.__routes.append(routeAttribute.Route)


	@property
	def Routes(self):
		return self.__routes
