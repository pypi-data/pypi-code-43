# -*- coding: utf-8 -*-
#
# Copyright © 2019 Stephan Seitz <stephan.seitz@fau.de>
#
# Distributed under terms of the GPLv3 license.

"""

"""

import os
import unittest

import pyconrad.autoinit
import pyconrad.phantoms

if 'CI' in os.environ:
    pyconrad.imshow = unittest.mock.MagicMock()


def test_phantoms():
    phantom = pyconrad.phantoms.shepp_logan(100, 100, 100)
    pyconrad.imshow(phantom, "phantom")


def main():
    test_phantoms()


if __name__ == '__main__':
    main()
