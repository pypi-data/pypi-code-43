"""Whereas the validation functions return results that will be outputted by
the RTM Validator, these "checks" functions perform smaller tasks, like
checking individual cells."""

# --- Standard Library Imports ------------------------------------------------
import collections


# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------


def cell_empty(value) -> bool:
    """Checks if a cell is empty. Cells contain True or False return False"""
    if isinstance(value, bool):
        return False
    if not value:
        return True
    return False


def id_prefix_format(self_id, root_id) -> bool:
    """This is used to check if a work item's ID starts with the root item's
    ID. This function assumes that the root ID must always be a string."""
    # if not isinstance(root_id, str):
    #     return False
    try:
        prefix_len = len(root_id)
        self_prefix = self_id[:prefix_len]
    except TypeError:
        return False
    result = True if self_prefix == root_id else False
    return result


def values_in_acceptable_entries(sequence, allowed_values) -> bool:
    """Each value in the sequence must be an allowed values. Otherwise, False."""
    if len(sequence) == 0:
        return True
    for item in sequence:
        if item not in allowed_values:
            return False
    return True



# I would like to have included this variable in the CascadeLevel, but that
# would cause circular references.
allowed_cascade_levels = {  # keys: level, values: position
    'PROCEDURE STEP': [0],
    'USER NEED': [1],
    'BUSINESS NEED': [1],
    'RISK NEED': [1],
    'REGULATORY NEED': [1],
    'DESIGN INPUT': [2],
    'DESIGN SOLUTION': list(range(3, 20))
}


def numbers():
    print("Called")
    return list(range(10))

if __name__ == "__main__":
    pass
