import copy
import logging
import operator

from dataclasses         import dataclass, field
from mnectar.util.signal import Signal

_logger = logging.getLogger(__name__)

@dataclass
class Column:
    name:        str                                    # Column name in database (unique)
    description: str                                    # Description for user display (short)
    sizeHint:    int      = -1                          # Width hint for tabular displays (May not apply to all UIs)
    display:     bool     = True                        # If this column can be displayed to the user
    hidden:      bool     = False                       # If this column hould be hidden in GUI table displays
    filterAuto:  bool     = False                       # If this column should be searched when no column name is provided
    displayFunc: callable = lambda r,c: r[c]            # Function to get and change the value when displayed (r==record, c==column)
    sortFunc:    callable = lambda r,c: r[c].lower()    # Function to get and change the value when sorting (r==record, c==column)
    sortCols:    list     = field(default_factory=list) # When sorting, use these columns instead of the selected column
    sortDefault: str      = ""                          # Default sort string if no value exists for this column

    def __post_init__(self):
        if len(self.sortCols) == 0:
            self.sortCols.append(self.name)


class ColumnManager(dict):
    """
    This class is designed to act as a global column database owned by the application
    """

    # This class relies on Python >= 3.7 where ordered dictionaries are guaranteed!

    changed = Signal() # The list of columns changed

    def __init__(self, other=None):
        if other is not None:
            self.extend(other.values())

    def copy(self):
        return type(self)(self)

    def add(self, col):
        """
        Add a new column definition.
        Returns the old definition if the column exists, or None if this is a new column.
        """

        if type(col) != Column:
            raise TypeError("Each column definition must be of type: 'Column'")

        if col.name in self:
            _logger.warning(f"Duplicate Column '{col.name}'.  Replacing {self[col.name]} with {col}")
            old = self[col.name]
        else:
            old = None

        super().__setitem__(col.name, col)
        return old

    def extend(self, columns):
        for col in columns:
            self.add(col)

    def update(self, other):
        for name,column in other.items():
            self.add(column)

    def remove(self, name):
        return self.pop(name)

    def list(self):
        return list(self.values())

    def names(self, **keys):
        return [col.name for col in self.values() if
                all([getattr(col,key) == val for key,val in keys.items()])]

    def filterAsDict(self, **keys):
        return {name:col for name,col in self.items() if
                all([getattr(col,key) == val for key,val in keys.items()])}

    def filterAsList(self, **keys):
        return [col for col in self.values() if
                all([getattr(col,key) == val for key,val in keys.items()])]

    def index(self, **keys):
        return [idx for idx,col in enumerate(self.values()) if
                all([getattr(col,key) == val for key,val in keys.items()])]

    def indexOfName(self, name):
        return list(self.keys()).index(name)

    def __getitem__(self, value):
        if type(value) == int:
            return list(self.values())[value]
        else:
            return super().__getitem__(value)

    def __setitem__(self, name, col):
        if type(col) != Column:
            raise TypeError("Each column definition must be of type: 'Column'")

        if col.name in self:
            _logger.warning(f"Duplicate Column '{col.name}'.  Replacing {self[col.name]} with {col}")

        if col.name != name:
            raise KeyError(f"Dictionary name '{name}' does not match the column name '{col.name}'")

        super().__setitem__(col.name, col)

