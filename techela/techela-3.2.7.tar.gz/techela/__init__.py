"""A flask of techela."""

import argparse
import os
import subprocess
import sys
from pkg_resources import get_distribution


__version__ = get_distribution('techela').version
