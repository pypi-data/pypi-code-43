# ukedown
# Copyright (C) 2017 Stuart Sears
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

## PATTERNS FOR UKEDOWN ##
# These are all python regular expressions, RTFM if needed
# when used that will probably be compiled thus:
# re.compile(PATTERN, re.UNICODE|re.DOTALL)

# approximation of chords - covers major minor dim aug sus and 7/9/13 etc
# CHORD = r'\(([A-G][adgijmnsu0-9#b+-\/\*]*(?:\s*[\u2013\u2014-]\s*single(?:\s*strums?)?)?)\)'
CHORD = r'\(([A-G][adgijmnsu0-9#b+-\/\*A-G]*)\)'

DASHES = r'\u2010\u2011\u2012\u2013\u2014'

# used to split title and artist from our first line
HYPHENS = r'\s*(?:-|\u2011|\u2013|\u2014|\u2015)\s*'

# backing vox - anything in () that is not a chord.
VOX = r'\(([\'\w\s]+)\)'
# VOX = r'\(([^\)]+)\)'

# band/performance instructions - use a different delimiter - {}
NOTES = r'\{([^}]+)\}'

# lines that start (and optionally end) with a | character are
# part of boxed paragraphs
BOX = r'(^|\n)\| *([^ ][^|]*)\|?$'

# a line containing something encapsulated by [] characters
HEADER = r'\[([^]]+)\]'

# pattern to pickup and "boldify" repetitions
REPEATS = r'(x\d+)'

