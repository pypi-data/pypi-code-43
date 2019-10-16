# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
#
# This file is part of Frootlab Aughra, https://www.frootlab.org/aughra
#
#  Aughra is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Aughra is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Aughra. If not, see <http://www.gnu.org/licenses/>.
#
"""Aughra code catalog.

Aughra is a planed catalog server for algorithm storage and evaluation. Aughra
aims to serve as an algorithm catalog for Rian to allow the client-side
automatic usage of currently best fitting (CBF) algorithms. Thereby any
respectively used CBF algorithm is determined server-sided by it's category and
a chosen metric. An example for such a metric would be the average prediction
accuracy within a fixed set of *gold standard samples* of the respective domain
of application (e.g. latin handwriting samples, spoken word samples, TCGA gene
expression data, etc.). Nevertheless also the metric by itself can be a CBF
algorithm.

"""
__version__ = '0.0.1'
__license__ = 'GPLv3'
__copyright__ = '2019 Frootlab'
__description__ = 'Catalog Server and Algorithm Repository'
__url__ = 'https://www.frootlab.org/aughra'
__organization__ = 'Frootlab'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']
__maintainer__ = 'Patrick Michl'
__credits__ = ['']
__docformat__ = 'google'
