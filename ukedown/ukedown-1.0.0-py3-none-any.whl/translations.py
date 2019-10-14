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

# patterns for  translating all the horrible 'smart' characters that word etc like to
# put in when you just want boring hyphens or quotes or brackets (or whatever)
# basically  this is a dictionary mapping ord(UNICODE) to UNICODE_REPLACEMENT


WP_JUNK = {
        # first hyphen characters, there are a few and wordprocessors do love 'em
        '\u2010': '-', # hyphen
        '\u2011': '-', # non-breaking hyphen
        '\u2012': '-', # figure-dash
        '\u2013': '-', # en-dash
        '\u2014': '-', # em-dash
        '\u2015': '-', # horizontal bar
        # then the silly pretty quote things): let's just use the normal ascii ones
        '\u2018': "'", # left single quotation
        '\u2019': "'", # right single quotation
        '\u201c': '"', # left double quotation
        '\u201d': '"', # right double quotation
        '\u2026': '...', # ellipsis
        }

# unicode strings have their own 'translate' method so we just need a table:
UNICODE_CLEAN_TABLE = dict((ord(k), v) for k,v in list(WP_JUNK.items()))

