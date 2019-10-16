"""This module defines the Field class, a base class that all fields will build
on. See __init__ for more detail."""

# --- Standard Library Imports ------------------------------------------------
from collections import defaultdict, namedtuple

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.main.context_managers as context
from rtm.containers.worksheet_columns import get_matching_worksheet_columns
from rtm.validate import validator_output
from rtm.main import config
from rtm.validate.validator_output import OutputHeader
import rtm.validate.validation as val


class Field:

    def __init__(self, name):
        """All columns (except for the Cascade Block) in the RTM excel
        worksheet are represented by this class. Objects of this class record
        the header, the cell values, the columns horizontal position, etc. """

        self.name = name

        # --- Get matching columns --------------------------------------------
        # The excel sheet might contain multiple columns that match this
        # field's name. We save all of them here, but only the first one gets used.
        # If there's more than one match, the user is alerted.
        # TODO Make sure this is actually true.
        matching_worksheet_columns = get_matching_worksheet_columns(
            context.worksheet_columns.get(),
            name,
        )

        # --- Override defaults if matches are found --------------------------
        if len(matching_worksheet_columns) >= 1:
            # Get all matching indices (used for checking duplicate data and proper sorting)
            # Used in later checks of relative column position
            self._positions = [col.position for col in matching_worksheet_columns]
            # From first matching column, get cell values for rows 2+
            # Get first matching column data
            # Duplicate columns are ignored; user receives warning.
            self.values = matching_worksheet_columns[0].values
        else:
            self._positions = None
            self.values = None

        # --- Set up for validation -------------------------------------------
        self._correct_position = None
        self._val_results = []

    @property
    def found(self):
        """True if at least one RTM column has self.name as its header"""
        if self.values is None:
            return False
        return True

    @property
    def position_left(self):
        """Return horizontal/columnar position of this field. Used to make sure
        this column is in the correct position relative to the two fields
        expected to be to the left and right."""
        if self.found:
            return self._positions[0]
        else:
            return -1

    @property
    def position_right(self):
        """For single-column fields (i.e. most fields), the left and right
        positions are the same. Multi-column fields (i.e. Cascade Block) return
        different values for left and right positions."""
        return self.position_left

    @property
    def column(self):
        return self.position_left + 1

    def print(self):
        """Print to console 1) field name and 2) the field's validation results."""
        for result in self._val_results:
            result.print()

    @property
    def excel_markup(self):
        """Return dict. Key= row number. Value= List of comments."""
        markup = defaultdict(list)
        for val_result in self._val_results[1:]:  # exclude the first item, which is just the header
            val_result: validator_output.ValidationResult
            if val_result.score == 'Pass':
                continue
            val_type = val_result.excel_type
            if val_type == 'body':
                col = self.column
                comment = (val_result.title, val_result.comment)
                for row in val_result.rows:
                    location = (row, col)
                    markup[location].append(comment)
            elif val_type == 'header':
                row = config.header_row
                col = self.column
                location = (row, col)
                comment = (val_result.title, val_result.comment)
                markup[location].append(comment)
            elif val_type == 'notes':
                location = self.name
                comment = (val_result.title, val_result.comment)
                markup[location].append(comment)
            else:
                raise ValueError(f"{val_type} is not a valid validation type.")
        return markup

    def __str__(self):
        return self.__class__, self.found

    def val_results_header_and_field_exists(self):
        return [OutputHeader(self.name), val.field_exist(self.found, self.name)]


if __name__ == "__main__":
    a = {1, 2}
    b = 'a b'.split()
    b += a
    print(b)
