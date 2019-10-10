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
# Authors:						Patrick Lehmann
#
# Python package:	    An interface for HTTP Requests and Responses.
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
from flags import Flags, unique_bits

__api__ = [
	"HTTPVersion",
	"HTTPMethods",
	"ContentKinds",
	"ReturnCodes",
	"Request",
	"Response",
	"HTTPRequestHandler"
]
__all__ = __api__


@unique_bits
class HTTPVersion(Flags):
	HTTP_09 = 1
	HTTP_10 = 2
	HTTP_11 = 4
	HTTP_20 = 8
	HTTP_30 = 16

@unique_bits
class HTTPMethods(Flags):
	"""A list of supported HTTP methods."""
	GET =      1
	POST =     2
	PUT =      4
	PATCH =    8
	DELETE =  16
	HEAD =    32
	OPTIONS = 64


@unique_bits
class ContentKinds(Flags):
	Binary = 1
	Text = 2


class ReturnCodes(Flags):
	OK = 1


from .Request   import Request
from .Response  import Response
from .HTTPRequestHandler   import HTTPRequestHandler
