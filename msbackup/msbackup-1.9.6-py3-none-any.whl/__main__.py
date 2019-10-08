# -*- coding: utf-8 -*-
"""Точка входа в приложение."""

import sys

try:
    from msbackup.cli import main
except ImportError:
    from cli import main


sys.exit(main())
