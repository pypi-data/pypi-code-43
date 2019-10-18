
"""
hangup.py

Representation of Bandwidth's hangup BXML verb

@author Jacob Mulford
@copyright Bandwidth INC
"""

from .base_verb import AbstractBxmlVerb


class Hangup(AbstractBxmlVerb):

    def to_xml(self):
        return "<Hangup/>"
