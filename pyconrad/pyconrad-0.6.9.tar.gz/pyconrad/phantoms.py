# -*- coding: utf-8 -*-
#
# Copyright © 2019 Stephan Seitz <stephan.seitz@fau.de>
#
# Distributed under terms of the GPLv3 license.

"""
Wrapper module around CONRAD's phantoms
"""

import numpy as np

from pyconrad._cache import disk_cache


@disk_cache
def shepp_logan(*shape):
    """
    Calculates a numerical Shepp-Logan phantom using NumericalSheppLogan3D
    """
    assert len(shape) == 3, "Has to be 3-d at the moment"

    from edu.stanford.rsl.conrad.phantom import NumericalSheppLogan3D
    return np.array(NumericalSheppLogan3D(*reversed(shape)).getNumericalSheppLoganPhantom())
