"""
Parse chord notation and return key and mode.
"""
from .general import Error
from .notes import Note


class ChordError(Error):
    pass


class Chord:
    def __init__(self, chord_name: str):
        self.name = chord_name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ChordError("Only strings are accepted")
        pass  # Check regex for appropriate chord


class ChordConverter:
    pass  # Convert chords to scales (keys) for roman numeral analysis


class ChordTransposer:
    pass  # parse chord to get position relative to base interval (if there's sharp/flat), then go to new key and add that position back to the sign
    # e.g. D# in G major --> +1 to D in G major
    # convert to Eb major --> Bb +1 ==> B in Eb major
