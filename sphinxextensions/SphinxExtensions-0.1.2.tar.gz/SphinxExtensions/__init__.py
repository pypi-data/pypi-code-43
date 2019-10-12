# EMACS settings: -*-	tab-width: 2; indent-tabs-mode: t; python-indent-offset: 2 -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
#
# =============================================================================
#   ____        _     _            _____      _                 _
#  / ___| _ __ | |__ (_)_ __ __  _| ____|_  _| |_ ___ _ __  ___(_) ___  _ __  ___
#  \___ \| '_ \| '_ \| | '_ \\ \/ /  _| \ \/ / __/ _ \ '_ \/ __| |/ _ \| '_ \/ __|
#   ___) | |_) | | | | | | | |>  <| |___ >  <| ||  __/ | | \__ \ | (_) | | | \__ \
#  |____/| .__/|_| |_|_|_| |_/_/\_\_____/_/\_\\__\___|_| |_|___/_|\___/|_| |_|___/
#        |_|
# ==============================================================================
# Authors:          Patrick Lehmann
#
# Python Module:    Extensions for the Sphinx documentation tool.
#
# License:
# ==============================================================================
# Copyright 2017-2019 Patrick Lehmann - Bötzingen, Germany
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#
from pyAttributes import Attribute


__api__ = [
	'DocumentMemberAttribute'
]
__all__ = __api__


class DocumentMemberAttribute(Attribute):
	def __init__(self, value=True):
		super().__init__()
		self.value = value
