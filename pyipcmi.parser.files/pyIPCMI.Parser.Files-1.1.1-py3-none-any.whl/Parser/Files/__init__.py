# EMACS settings: -*- tab-width: 2; indent-tabs-mode: t -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
# =============================================================================
#               ___ ____   ____ __  __ ___   ____                          _____ _ _
#   _ __  _   _|_ _|  _ \ / ___|  \/  |_ _| |  _ \ __ _ _ __ ___  ___ _ __|  ___(_) | ___  ___
#  | '_ \| | | || || |_) | |   | |\/| || |  | |_) / _` | '__/ __|/ _ \ '__| |_  | | |/ _ \/ __|
#  | |_) | |_| || ||  __/| |___| |  | || | _|  __/ (_| | |  \__ \  __/ |_ |  _| | | |  __/\__ \
#  | .__/ \__, |___|_|    \____|_|  |_|___(_)_|   \__,_|_|  |___/\___|_(_)|_|   |_|_|\___||___/
#  |_|    |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python package:	    A parser for *.files files used in pyIPCMI.
#
# Description:
# ------------------------------------
#		TODO
#
# License:
# ============================================================================
# Copyright 2017-2019 Patrick Lehmann - Bötzingen, Germany
# Copyright 2007-2016 Technische Universität Dresden - Germany
#                     Chair of VLSI-Design, Diagnostics and Architecture
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
from typing import List


class Base():
	DELIMITER = "/"

	_parent = None #

	def __init__(self, parent):
		self._parent = parent


class RootMixIn(Base):

	def __init__(self):
		super().__init__(None)


class ElementMixIn(Base):
	_elementName: str = None

	def __init__(self, parent, elementName):
		super().__init__(parent)
		self._elementName = elementName

	def __str__(self):
		return self._elementName

class SystemMixIn():
	pass


class PathMixIn():
	ELEMENT_DELIMITER = "/"
	ROOT_DELIMITER =    "/"

	_isAbsolute: bool = None
	_elements:   List = None

	def __init__(self, elements, isAbsolute):
		self._isAbsolute = isAbsolute
		self._elements =   elements

	def __len__(self):
		return len(self._elements)

	def __str__(self):
		result = self.ROOT_DELIMITER if self._isAbsolute else ""

		if (len(self._elements) > 0):
			result = result + str(self._elements[0])

			for element in self._elements[1:]:
				result = result + self.ELEMENT_DELIMITER + str(element)

		return result

	@classmethod
	def Parse(cls, path: str, root, pathCls, elementCls):
		parent = root

		if path.startswith(cls.ROOT_DELIMITER):
			isAbsolute = True
			path = path[len(cls.ELEMENT_DELIMITER):]
		else:
			isAbsolute = False

		parts = path.split(cls.ELEMENT_DELIMITER)
		elements = []
		for part in parts:
			element = elementCls(parent, part)
			parent =  element
			elements.append(element)

		return pathCls(elements, isAbsolute)
