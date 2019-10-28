#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# @copyright Copyright (C) Guichet Entreprises - All Rights Reserved
# 	All Rights Reserved.
# 	Unauthorized copying of this file, via any medium is strictly prohibited
# 	Dissemination of this information or reproduction of this material
# 	is strictly forbidden unless prior written permission is obtained
# 	from Guichet Entreprises.
###############################################################################
import os.path
import json

from .template import generate_template
from .release import get as get_release

__all__ = ['generate_template', 'get_release']

__pkg_json__ = os.path.join(os.path.dirname(__file__),
                       "..", "package.json")

if os.path.isfile(__pkg_json__):
	with open(os.path.join(os.path.dirname(__file__),
						   "..", "package.json")) as json_file:
		__data__ = json.load(json_file)

	__module_name__ = "xe2layout"
	__version__ = __data__['version']
	__author__ = __data__['author']
	__copyright__ = __data__['copyright']
	__credits__ = __data__['credits']
	__license__ = __data__['license']
	__maintainer__ = __data__['author']
	__email__ = __data__['email']
	__status__ = "Production"
	__url__ = __data__['url']

