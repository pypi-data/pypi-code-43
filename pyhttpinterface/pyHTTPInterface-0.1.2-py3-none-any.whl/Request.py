# EMACS settings: -*-  tab-width: 2; indent-tabs-mode: t -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
#
# =============================================================================
#              _   _ _____ _____ ____ ___       _             __
#  _ __  _   _| | | |_   _|_   _|  _ \_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___
# | '_ \| | | | |_| | | |   | | | |_) | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \
# | |_) | |_| |  _  | | |   | | |  __/| || | | | ||  __/ |  |  _| (_| | (_|  __/
# | .__/ \__, |_| |_| |_|   |_| |_|  |___|_| |_|\__\___|_|  |_|  \__,_|\___\___|
# |_|    |___/
#
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python package:     An interface for HTTP Requests.
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
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
from textwrap import dedent
from typing   import Dict

from pyGenericPath.URL import URL

from . import HTTPMethods, HTTPVersion


class Request():
	_protocolVersion: HTTPVersion = None
	_encrypted:       bool =        None
	_httpMethod:      HTTPMethods = None
	_path:            URL =         None
	_parameters:      Dict =        None
	_headers:         Dict =        None
	_contentKind:     str =         None
	_contentEncoding: str =         None
	_contentType:     str =         None
	_content =                      None

	def __init__(self, httpMethod, path, headers, content):
		self._protocolVersion = HTTPVersion.HTTP_10
		self._httpMethod =      httpMethod
		self._path =            path
		self._headers =         headers
		self._content =         content

	def __repr__(self):
		return dedent("""\
			{method} {path} {protocol}
			{headers}
			""".format(method=self._httpMethod.to_simple_str(), path=self._path, protocol=self._protocolVersion, headers="xyz"))

	@property
	def ProtocolVersion(self):
		return self._protocolVersion

	@property
	def HTTPMethod(self):
		return self._httpMethod

	@property
	def Path(self):
		return self._path

	def Parameter(self, name):
		return self._path.Query[name]

	def Header(self, name):
		return self._headers[name]


class JSONRequest(Request):
	_json = None

	def __init__(self, headers, content):
		super().__init__(headers, content)

		self._ParseJSONContent()


	def _ParseJSONContent(self):
		pass
