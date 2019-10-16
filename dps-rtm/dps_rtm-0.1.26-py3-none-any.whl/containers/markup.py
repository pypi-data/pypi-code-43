"""The class below is used to store comments that can be printed either to console or excel."""

# --- Standard Library Imports ------------------------------------------------
import collections

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
# None


CellMarkup = collections.namedtuple("CellMarkup", "comment is_error indent size is_bold")
# is_error will drive what color to highlight the cell (e.g. green for neutral and orange for error)
# indent: indent the cell contents if true
CellMarkup.__new__.__defaults__ = ('', False, False, None, False)
