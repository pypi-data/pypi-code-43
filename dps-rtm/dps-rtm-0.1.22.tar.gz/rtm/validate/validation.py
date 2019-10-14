"""Each of these functions checks a specific aspect of an RTM field and returns
a ValidationResult object, ready to be printed on the terminal as the final
output of this app."""

# --- Standard Library Imports ------------------------------------------------
import collections
import re
import functools

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.containers.fields
import rtm.validate.checks as checks
import rtm.main.context_managers as context
from rtm.validate.validator_output import ValidationResult
from rtm.containers.work_items import MissingWorkItem


# --- General-purpose validation ----------------------------------------------
def field_exist(field_found, field_name=None) -> ValidationResult:
    """Given field_found=True/False, return a ValidationResult, ready to be
    printed to console."""

    if field_found:
        score = "Pass"
        explanation = None
    else:
        score = "Error"
        explanation = "Field not found. Make sure your headers exactly match the title shown above."
    return ValidationResult(
        score=score,
        title="Field Exist",
        cli_explanation=explanation,
        markup_type='notes',
        markup_explanation=f"Field not found. Make sure your header matches '{field_name}' exactly.",
    )


def left_right_order(field_self) -> ValidationResult:
    """Does this field actually appear after the one it's supposed to?"""
    title = "Left/Right Order"

    # --- Field that is supposed to be positioned to this field's left
    field_left = rtm.containers.fields.get_expected_field_left(field_self)

    if field_left is None:
        # argument field is supposed to be all the way to the left.
        # It's always in the correct position.
        score = "Pass"
        explanation = "This field appears to the left of all the others"
    elif field_left.position_right <= field_self.position_left:
        # argument field is to the right of its expected left-hand neighbor
        score = "Pass"
        explanation = (
            f"This field comes after the {field_left.name} field as it should"
        )
    else:
        score = "Error"
        explanation = f"This field should come after {field_left.name}"
    return ValidationResult(score, title, explanation, markup_type='header')


def not_empty(values) -> ValidationResult:
    """All cells must be non-empty"""
    error_indices = []
    for index, value in enumerate(values):
        if checks.cell_empty(value):
            error_indices.append(index)
    if not error_indices:
        score = "Pass"
        explanation = "All cells are non-blank"
    else:
        score = "Error"
        explanation = "Action Required. The following rows are blank: "
    return ValidationResult(
        score,
        title="Not Empty",
        cli_explanation=explanation,
        nonconforming_indices=error_indices,
        markup_type='body',
        markup_explanation='This cell must contain a value.'
    )


# --- ID ----------------------------------------------------------------------
def procedure_step_format(id_values, work_items):
    """Check all root work items for the correct ID format. This check is made
    indirectly on all other work items when they're compared back to their own
    root work item."""

    def correctly_formatted(value) -> bool:
        if not isinstance(value, str) or len(value) != 4:
            return False
        x = re.match("P\d\d\d", value)
        return bool(x)

    error_indices = [
        index
        for index, value in enumerate(id_values)
        if work_items[index].is_root and not correctly_formatted(value)
    ]

    # Output
    title = 'Procedure Step Format'
    if not error_indices:
        score = "Pass"
        explanation = "All Procedure Step IDs correctly follow the 'PXYZ' format"
    else:
        score = "Error"
        explanation = "The following Procedure Step IDs do not follow the 'PXYZ' format: "
    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


def unique(values):
    """Each cell in the ID field should be unique. This ensures 1) they can be
    uniquely identified and 2) an alphabetical sort on that column is
    deterministic (has the same result each time)."""

    title = 'Unique Rows'

    # Record how many times each value appears
    tally = collections.defaultdict(list)
    for index, value in enumerate(values):
        tally[value].append(index)

    # For repeated ID's, get all indices except for the first.
    error_indices = []
    for indices in tally.values():
        error_indices += indices[1:]
    error_indices.sort()

    if not error_indices:
        score = "Pass"
        explanation = "All IDs are unique."
    else:
        score = "Error"
        explanation = "The following rows contain duplicate IDs: "

    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


def start_w_root_id():
    """Each work item starts with its root ID"""

    id_values = context.fields.get().get_field_object('ID').values
    work_items = context.work_items.get()

    error_indices = []
    for index, work_item in enumerate(work_items):

        # Skip this index if it doesn't have a root.
        # That error will be caught elsewhere.
        if isinstance(work_item.root, MissingWorkItem):
            continue
        # if work_item.root.index == -1:
        #     continue

        self_id = id_values[index]
        root_id = id_values[work_item.root.index]
        if not checks.id_prefix_format(self_id, root_id):
            error_indices.append(index)

    # Output
    title = "Start with root ID"
    if not error_indices:
        score = "Pass"
        explanation = "Each parent/child pair uses the same prefix (e.g. 'P010-')"
    else:
        score = "Error"
        explanation = "Each parent/child pair must use the same prefix (e.g. 'P010-'). The following rows don't: "
    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


# @functools.lru_cache()
def alphabetical_sort(values):
    """Each cell in the ID field should come alphabetically after the prior one."""

    error_indices = []
    for index, value in enumerate(values):
        if index == 0:
            continue
        string_pair = [values[index - 1], values[index]]
        if string_pair != sorted(string_pair):  # alphabetical sort check
            error_indices.append(index)

    # Output
    title = 'Alphabetical Sort'
    if not error_indices:
        score = "Pass"
        explanation = "All cells appear in alphabetical order"
    else:
        score = "Error"
        explanation = "The following rows are not in alphabetical order: "
    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


# --- Cascade Block -----------------------------------------------------------
def cascade_block_not_empty() -> ValidationResult:
    """Each row in cascade block must have at least one entry."""
    title = 'Not Empty'
    error_indices = [
        work_item.index
        for work_item in context.work_items.get()
        if work_item.depth is None
    ]
    if not error_indices:
        score = "Pass"
        explanation = "All rows are non-blank"
    else:
        score = "Error"
        explanation = (
            "Action Required. The following rows have blank cascade blocks: "
        )
    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


def single_entry() -> ValidationResult:
    """Each row in cascade block must contain only one entry"""

    error_indices = [
        work_item.index
        for work_item in context.work_items.get()
        if len(work_item.cascade_block_row) != 1
    ]
    if not error_indices:
        score = "Pass"
        explanation = "All rows have a single entry"
    else:
        score = "Warning"
        explanation = (
            "Action Required. The following rows are blank or have multiple entries: "
        )
    return ValidationResult(
        score,
        title='Single Entry',
        cli_explanation=explanation,
        nonconforming_indices=error_indices,
        markup_type='body',
        markup_explanation='This Cascade Block contains more than one entry.'
    )


def use_all_columns() -> ValidationResult:
    """The cascade block shouldn't have any unused columns."""

    # Setup fields
    fields = context.fields.get()
    cascade_block = fields.get_field_object('CascadeBlock')
    subfield_count = len(cascade_block)
    positions_expected = set(range(subfield_count))

    # Setup Work Items
    work_items = context.work_items.get()
    positions_actual = set(
        work_item.depth for
        work_item in
        work_items
    )

    missing_positions = positions_expected - positions_actual

    # Output
    title = "Use All Columns"
    if len(missing_positions) == 0:
        score = "Pass"
        explanation = f"All cascade levels were used."
    else:
        score = "Warning"
        explanation = f"Some cascade levels are unused"

    return ValidationResult(score, title, explanation, markup_type='header')


def orphan_work_items() -> ValidationResult:
    title = "Orphan Work Items"
    score = "Pass"
    explanation = "Each work item must trace back to a procedure step. " \
                  "This check is not yet implemented. This is a placeholder."
    return ValidationResult(score, title, explanation, markup_type='body')


@functools.lru_cache()
def solution_level_terminal() -> ValidationResult:
    """Each cascade path must terminate in a Solution Level."""

    # Setup
    work_items = context.work_items.get()
    terminal_work_items = work_items.leaf_items
    error_indices = [
        work_item.index
        for work_item in terminal_work_items
        if not work_item.allowed_to_be_terminal_work_item
    ]

    # Output
    if not error_indices:
        score = "Pass"
        explanation = f"All Terminal Work Items are of Cascade Level `Solution Level`"
    else:
        score = "Error"
        explanation = f"The following rows terminate a cascade path prior to Solution Level: "
    return ValidationResult(
        score=score,
        title="Terminal Items",
        cli_explanation=explanation,
        nonconforming_indices=error_indices,
        markup_type='body',
        markup_explanation='This item should have at least one child.'
    )


def f_entry() -> ValidationResult:
    """Terminal work items (i.e. leaf nodes) are marked with 'F' in the Cascade Block."""

    # Setup
    work_items = context.work_items.get()
    exclude_indices = solution_level_terminal().indices
    error_indices = [
        work_item.index
        for work_item in work_items.leaf_items
        if work_item.value != 'F'
        and work_item.index not in exclude_indices
    ]

    # Output
    title = "Leaf Items = F"
    if not error_indices:
        score = "Pass"
        explanation = f"All Terminal Work Items are marked with an `F`"
    else:
        score = "Error"
        explanation = f"The following rows have a value other than `F`: "
    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


def x_entry() -> ValidationResult:
    """All non-terminal work items (i.e. non-leaf graph nodes) are marked with 'X'"""

    # allowed_entries = "X F".split()
    #
    # error_indices = [
    #     index
    #     for index, work_item in enumerate(context.work_items.get())
    #     if not checks.values_in_acceptable_entries(
    #         sequence=[item.value for item in work_item.cascade_block_row],
    #         allowed_values=allowed_entries,
    #     )
    # ]
    #
    # # Output
    # title = "X Entry"
    # if not error_indices:
    #     score = "Pass"
    #     explanation = f"All entries are one of {allowed_entries}"
    # else:
    #     score = "Error"
    #     explanation = f"Action Required. The following rows contain something other than the allowed {allowed_entries}: "
    # return ValidationResult(score, title, explanation, error_indices)
    title = "X Entry"
    score = "Pass"
    explanation = "All other work items are marked with an `X`. " \
                  "This check is not yet implemented. This is a placeholder."
    return ValidationResult(score, title, explanation, markup_type='body')


# --- Cascade Level -----------------------------------------------------------
def cascade_level_valid_input(field) -> ValidationResult:
    """Check cascade levels against list of acceptable entries."""

    values = field.values
    allowed_values = checks.allowed_cascade_levels.keys()
    error_indices = [
        index
        for index, value in enumerate(values)
        if not checks.cell_empty(value)
           and value not in allowed_values
    ]

    # Output
    if not error_indices:
        score = "Pass"
        explanation = "All cell values are valid"
    else:
        score = "Error"
        explanation = f'The following cells contain values other than the allowed' \
                      f'\n\t\t\t{list(allowed_values)}:\n\t\t\t'
    return ValidationResult(
        score,
        title='Valid Input',
        cli_explanation=explanation,
        nonconforming_indices=error_indices,
        markup_type='body',
        markup_explanation='This cell contains an incorrect value. Choose from the following: {list(allowed_values)}',
    )


def cascade_block_match() -> ValidationResult:
    """A work item's cascade level entry must match its cascade block entry."""
    fields = context.fields.get()
    cascade_level = fields.get_field_object('CascadeLevel')
    body = cascade_level.values

    # --- Don't report on rows that failed for other reasons (i.e. blank or invalid input
    exclude_results = [
        not_empty(body),
        cascade_level_valid_input(cascade_level),
        cascade_block_not_empty()
    ]
    exclude_indices = []
    for result in exclude_results:
        exclude_indices += list(result.indices)
    indices_to_check = set(range(len(body))) - set(exclude_indices)

    error_indices = []
    work_items = context.work_items.get()
    for index in indices_to_check:
        cascade_block_position = work_items[index].depth
        cascade_level_value = body[index]
        allowed_positions = checks.allowed_cascade_levels[cascade_level_value]
        if cascade_block_position not in allowed_positions:
            error_indices.append(index)

    # Output
    title = 'Cascade Block Match'
    if not error_indices:
        score = "Pass"
        explanation = "All rows (that passed previous checks) match the position marked in the Cascade Block"
    else:
        score = "Error"
        explanation = f'The following rows do not match the cascade position marked in the Cascade Block:'
    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


# --- Requirement Statement ---------------------------------------------------
def missing_tags() -> ValidationResult:
    """Report on usage of out-of-the-box tags."""

    # --- Get data ------------------------------------------------------------
    req_statement = context.fields.get().get_field_object('ReqStatement')
    tags = req_statement.tags_ven_diagram

    # Output
    title = 'Base Tags'
    if not tags.missing:
        # All base tags were used
        score = 'Pass'
        explanation = f'All base tags found ({list(tags.base)}).'
    elif not tags.base_found:
        # No base tags were used
        score = 'Warning'
        explanation = f'No base tags were found ({list(tags.base)}).'
    else:
        # Some base tags were used
        score = 'Warning'
        explanation = f'These base tags were found: {list(tags.base_found)}. ' \
                      f'These were missing: {list(tags.missing)}'
    val_result = ValidationResult(score, title, explanation, markup_type='header')
    val_result.base_found = sorted(list(tags.base_found))
    val_result.missing = sorted(list(tags.missing))
    return val_result


def custom_tags() -> ValidationResult:
    """Report on usage of custom tags."""

    # --- Get data ------------------------------------------------------------
    req_statement = context.fields.get().get_field_object('ReqStatement')
    tags = req_statement.tags_ven_diagram

    # --- Generate Output -----------------------------------------------------
    title = 'Custom Tags'
    if not tags.additional:
        # No custom tags
        score = 'Pass'
        explanation = 'No custom tags found.'
    else:
        # These custom tags were found.
        score = 'Warning'
        explanation = f"These custom tags were found: {list(tags.additional)}. " \
                      f"Make sure you didn't mean to use one of the base tags: {list(tags.base)}"
    val_result = ValidationResult(score, title, explanation, markup_type='header')
    val_result.custom = sorted(list(tags.additional))
    return val_result


def parent_child_modifiers() -> ValidationResult:
    """The parent and child tags from the Requirement Statement should each
    point to a valid ID."""

    # --- Get data ------------------------------------------------------------
    req_statement = context.fields.get().get_field_object('ReqStatement')

    # --- Look for unconnected edges ------------------------------------------
    error_indices = sorted(list(set(
        edge.index
        for edge in req_statement.edges.as_list
        if not edge.connected
    )))

    # Output
    title = 'Parent/Child Modifiers'
    if not error_indices:
        score = 'Pass'
        explanation = 'All #AdditionalParent and #Child tags match to existing IDs.'
    else:
        score = "Error"
        explanation = "The following rows have #AdditionalParent and #Child tags that don't match to any existing IDs: "
    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


def mutual_parent_child() -> ValidationResult:
    """The parent and child tags from the Requirement Statement should each
    point to a valid ID. That target row should have a matching tag that points
    back."""

    # --- Get data ------------------------------------------------------------
    req_statement = context.fields.get().get_field_object('ReqStatement')
    edges = req_statement.edges

    # --- Exclude indices that already failed other tests ---------------------
    excluded_indices = [index for index in parent_child_modifiers().indices]

    # --- Look for non-mutual edges -------------------------------------------
    error_indices = sorted(list(set(
        edge.index
        for edge in req_statement.edges.as_list
        if edge.connected and not edge.mutual
    )))

    # Output
    title = 'Mutual Parent/Child'
    tags_string = ' and '.join(req_statement.convert_to_hashtag(req_statement.edge_tag_names))
    if not error_indices:
        score = 'Pass'
        explanation = f'All {tags_string} tags match to existing IDs.'
    else:
        score = "Error"
        explanation = f"The following rows have {tags_string} tags that don't have a matching tag pointing back: "
    return ValidationResult(score, title, explanation, error_indices, markup_type='body')


# --- VorV Strategy, Results --------------------------------------------------
def business_need_na(values) -> ValidationResult:

    # ...

    # Output
    title = 'Business Need N/A'
    score = 'Pass'
    explanation = "Business Need work items are marked with 'N/A'. " \
                  "This check is not yet implemented. This is a placeholder."
    return ValidationResult(score, title, explanation, markup_type='body')


# --- DO Features -------------------------------------------------------------
def ctq_format(values) -> ValidationResult:

    # ...

    # Output
    title = 'CTQ Format'
    score = 'Pass'
    explanation = "If contains features that are CTQs, CTQ ID should be formatted as `CTQ##`. " \
                  "This check is not yet implemented. This is a placeholder."
    return ValidationResult(score, title, explanation, markup_type='body')


def missing_ctq(values) -> ValidationResult:

    # ...

    # Output
    title = 'Missing CTQ'
    score = 'Pass'
    explanation = "If CTQ Y/N is `yes`, this column must contain at least one CTQ. " \
                  "This check is not yet implemented. This is a placeholder."
    return ValidationResult(score, title, explanation, markup_type='body')


# --- CTQ Y/N -----------------------------------------------------------------
def ctq_valid_input(values) -> ValidationResult:

    # ...

    # Output
    title = 'Valid Input'
    score = 'Pass'
    explanation = "The only valid inputs for this column are ['yes', 'no', 'N/A', '-']. " \
                  "This check is not yet implemented. This is a placeholder."
    #  Note: only the procedure step can have a `-`
    return ValidationResult(score, title, explanation, markup_type='body')


def ctq_to_yes(values) -> ValidationResult:

    # ...

    # Output
    title = 'CTQ -> Yes'
    score = 'Pass'
    explanation = "Must be 'yes'if the DO Features column contains a CTQ. " \
                  "This check is not yet implemented. This is a placeholder."
    return ValidationResult(score, title, explanation, markup_type='body')


if __name__ == "__main__":
    pass
