"""This module contains two types of classes: the Fields sequence class, and
the fields it contains. Fields represent the columns (or groups of columns) in
the RTM worksheet."""

# --- Standard Library Imports ------------------------------------------------
import collections
import functools

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.containers.field as ft
import rtm.validate.validation as val
from rtm.main import context_managers as context


class Fields(collections.abc.Sequence):
    # --- Collect field classes -----------------------------------------------
    field_classes = []

    @classmethod
    def collect_field(cls):
        """Append a field class to this Fields sequence."""

        def decorator(field_):
            cls.field_classes.append(field_)
            return field_

        return decorator

    # --- Field Object Methods
    def __init__(self):
        """The Fields class is a sequence of fields. First, the field classes
        are collected in the order they're expected to appear in the RTM via
        the `collect_field` decorator. When initialized, all fields in the
        sequence get initialized too."""
        self.height = context.worksheet_columns.get().height  # height is the number of rows of values.
        self._fields = [field_class() for field_class in self.field_classes]

    def get_field_object(self, field_class):
        """Given a field class or name of field class, return the matching
        field object"""
        for _field in self:
            if isinstance(field_class, str):
                if _field.__class__.__name__ == field_class:
                    return _field
            else:
                if isinstance(_field, field_class):
                    return _field
        raise ValueError(f'{field_class} not found in {self.__class__}')

    def validate(self):
        """Validate all field objects in this sequence."""
        for field in self:
            field.validate()

    def print(self):
        """Output validation results to console for field objects in sequence"""
        # TODO give this a better name, one that shows that this is command line output
        for field_ in self:
            field_.print()

    @property
    def excel_markup(self):
        comments = collections.defaultdict(list)
        for field in self:
            for key, value in field.excel_markup.items():
                comments[key] += value
        return comments



    # --- Sequence ------------------------------------------------------------
    def __getitem__(self, item):
        return self._fields[item]

    def __len__(self) -> int:
        return len(self._fields)


@Fields.collect_field()
class ID(ft.Field):

    def __init__(self):
        """The ID field uniquely identifies each row (work item) and should
        sort alphabetically in case the excel sheet gets accidentally sorted on
        some other column."""
        super().__init__(name="ID")

    def validate(self):
        """Validate this field"""
        work_items = context.work_items.get()
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),
                # No need for explicit "not empty" check b/c this is caught by pxxx
                #   format and val_match_parent_prefix.
                val.unique(self.values),
                val.alphabetical_sort(self.values),
                val.procedure_step_format(self.values, work_items),
                val.start_w_root_id(),
            ]

    def get_index(self, id_value):
        # TODO Later, improve with a bisect search of a sorted list
        try:
            return self.values.index(id_value)
        except ValueError:
            return -1


@Fields.collect_field()
class CascadeBlock(ft.Field):

    def __init__(self):
        """The CascadeBlock is the most complicated of the RTM fields. it spans
        multiple columns and must help determine the parent for each work item."""
        self.name = 'Cascade Block'
        self._subfields = []
        for subfield_name in self._get_subfield_names():
            subfield = ft.Field(subfield_name)
            if subfield.found:
                self._subfields.append(subfield)
            else:
                self.last_field_not_found = subfield_name
                break

    @staticmethod
    def _get_subfield_names():
        """Return list of column headers. The first several are required. The
        last dozen or so are unlikely to be found on the RTM. This is because
        the user is allowed as many Design Output Solutions as they need."""
        field_names = ["Procedure Step", "Need", "Design Input"]
        for i in range(1, 20):
            field_names.append(f"Solution Level {str(i)}")
        return field_names

    @property
    def found(self):
        """True if at least one RTM column was found matching the headers
        given by self._get_subfield_names"""
        if len(self) > 0:
            return True
        else:
            return False

    @property
    def values(self):
        """Return a list of lists of cell values (for rows 2+)"""
        return [subfield.values for subfield in self]

    @property
    def position_left(self):
        """Return position of the first subfield"""
        if self.found:
            return self[0].position_left
        else:
            return -1

    @property
    def position_right(self):
        """Return position of the last subfield"""
        if self.found:
            return self[-1].position_left
        else:
            return -1

    # @functools.lru_cache()
    # TODO how often does get_row get used? If more than once, add lru cache back in?
    def get_row(self, index) -> list:
        return [col[index] for col in self.values]

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),  # LEFT/RIGHT ORDER
                val.cascade_block_not_empty(),  # NOT EMPTY
                val.single_entry(),  # SINGLE ENTRY
                val.use_all_columns(),  # USE ALL COLUMNS
                val.orphan_work_items(),  # ORPHAN WORK ITEMS
                val.solution_level_terminal(),  # SOLUTION LEVEL TERMINAL
                val.f_entry(),  # F
                val.x_entry(),  # X
            ]

    # --- Sequence ------------------------------------------------------------
    def __len__(self):
        return len(self._subfields)

    def __getitem__(self, item):
        return self._subfields[item]


@Fields.collect_field()
class CascadeLevel(ft.Field):

    def __init__(self):
        """The Cascade Level field goes hand-in-hand with the Cascade Block. It
        even duplicates some information to a degree. It's important that the
        values in this field agree with those in the Cascade Block."""
        super().__init__(name="Cascade Level")

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),
                val.not_empty(self.values),
                val.cascade_level_valid_input(self),
                val.cascade_block_match(),
            ]


Tag = collections.namedtuple('Tag', 'name index modifier')


class Edge:

    def __init__(self, index, tag_name, other_id, req_statement_field, id_field):
        """Instances of this class track a single secondary edge between parent
        and child documented as tags in the ReqStatement field. It requires
        the ReqStatement field to have already parsed its tags into a common
        format of index, tag_name, and modifier (in this case: the ID pointer)"""
        req_statement_field: ReqStatement
        id_field: ID
        self.req_statement_field = req_statement_field
        self.id_field = id_field
        self.index = index
        self.tag_name = tag_name  # Parent or Child
        self.other_id = other_id
        self.category = tag_name  # self.get_other_edge_tag(req_statement_field.edge_tag_names)
        self.other_index = self.get_other_index(other_id, id_field.values)

    @property
    def id_value(self):
        return self.id_field.values[self.index]

    @staticmethod
    def get_other_index(other_id, id_values):
        for index, id_value in enumerate(id_values):
            if id_value == other_id:
                return index
        return -1

    # def get_other_edge_tag(self, both_edge_tag_names):
    #     edge_tags = set(both_edge_tag_names)  # create shallow copy
    #     try:
    #         edge_tags.remove(self.tag_name)
    #     except KeyError:
    #         return ''
    #     return edge_tags.pop()

    @property
    def connected(self):
        """Connected means the ID (e.g. P010-0020) passed to this edge exists."""
        return True if self.other_index != -1 else False

    @property
    def mutual(self):
        return False if self.target_edge is None else True

    @property
    @functools.lru_cache()
    def target_edge(self):
        if not self.connected:
            return None
        all_edges = self.req_statement_field.edges.as_dict
        if self.other_index not in all_edges:
            return None
        edges_at_target = all_edges[self.other_index]
        for edge in edges_at_target:
            if edge.other_index == self.index:
                return edge
        return None

    def __repr__(self):
        return f"<{self.index}/{self.id_value} " \
               f"{'mutual ' if self.mutual else ''}" \
               f"{self.category} of {self.other_index}/{self.other_id}>"


class Edges:

    def __init__(self, req_statement_field, id_field):
        """This container class stores the data methods"""
        req_statement_field: ReqStatement
        id_field: ID
        self._edges = collections.defaultdict(list)

        # Populate self._edges
        for tag in req_statement_field.tags:
            tag: Tag
            if tag.name not in req_statement_field.edge_tag_names:
                continue
            self._edges[tag.index].append(Edge(
                index=tag.index,
                tag_name=tag.name,
                other_id=tag.modifier,
                req_statement_field=req_statement_field,
                id_field=id_field,
            ))

    @property
    def as_list(self):
        list_of_edges = []
        for edges in self._edges.values():
            list_of_edges += edges
        return list_of_edges

    @property
    def as_dict(self):
        return self._edges


@Fields.collect_field()
class ReqStatement(ft.Field):

    def __init__(self):
        """The Requirement Statement field is basically a large text block.
        Besides the req statement itself, it also contains tags, such as for
        marking additional parents and children."""
        super().__init__("Requirement Statement")
        self.edge_tag_names = {'ParentOf', 'ChildOf'}
        self.allowed_tag_names = self.edge_tag_names | {
            'Function',
            'MatingParts',
            'MechProperties',
            'UserInterface',
        }
        self._tags = None
        self._edges = None

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),  # LEFT/RIGHT ORDER
                val.not_empty(self.values),  # NOT EMPTY
                val.missing_tags(),  # MISSING TAGS
                val.custom_tags(),  # CUSTOM TAGS
                val.parent_child_modifiers(),  # PARENT/CHILD MODIFIERS
                val.mutual_parent_child(),  # MUTUAL PARENT/CHILD
            ]

    @staticmethod
    def convert_to_hashtag(tags):
        return set(
            '#' + tag
            for tag in tags
        )

    @property
    def tags(self):
        if self._tags is None:
            self._tags = []

            # Extract tags --------------------------------------------------------
            for index, cell_value in enumerate(self.values):
                # --- split up cell string ----------------------------------------
                try:
                    cell_lines = cell_value.split('\n')
                except AttributeError:
                    continue
                for line in cell_lines:
                    words = line.split()
                    # --- Check for tag -------------------------------------------
                    if len(words) > 0:
                        potential_tag = words[0]
                    else:
                        continue
                    if potential_tag.startswith('#'):
                        tag_name = potential_tag[1:]
                        modifier = words[1] if len(words) > 1 else ''
                        # --- Save tag, index, and modifier -----------------------
                        self._tags.append(Tag(tag_name, index, modifier))
        return self._tags

    @property
    # @functools.lru_cache()
    def tags_ven_diagram(self):
        allowed_tags = self.allowed_tag_names
        actual_tags = set(tag.name for tag in self.tags)

        TagNames = collections.namedtuple('TagNames', 'base actual base_found missing additional')

        return TagNames(
            base=allowed_tags,
            actual=actual_tags,
            base_found=actual_tags & allowed_tags,
            missing=allowed_tags - actual_tags,
            additional=actual_tags - allowed_tags,
        )

    @property
    def edges(self):
        if self._edges is None:
            fields: Fields = context.fields.get()
            self._edges = Edges(
                req_statement_field=self,
                id_field=fields.get_field_object('ID')
            )
        return self._edges


@Fields.collect_field()
class ReqRationale(ft.Field):

    def __init__(self):
        """This field has very few requirements."""
        super().__init__(name="Requirement Rationale")

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),
                val.not_empty(self.values),
            ]


@Fields.collect_field()
class VVStrategy(ft.Field):

    def __init__(self):
        """The V&V Strategy field is subject to few rules."""
        super().__init__(name="Verification or Validation Strategy")

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),
                val.not_empty(self.values),
                val.business_need_na(self.values),
            ]


@Fields.collect_field()
class VVResults(ft.Field):

    def __init__(self):
        """Verification or Validation Results field"""
        super().__init__(name="Verification or Validation Results")

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),
                val.not_empty(self.values),
                val.business_need_na(self.values),
            ]


@Fields.collect_field()
class Devices(ft.Field):

    def __init__(self):
        """Devices field"""
        super().__init__(name="Devices")

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),
                val.not_empty(self.values),
            ]


@Fields.collect_field()
class DOFeatures(ft.Field):

    def __init__(self):
        """"Design Output Features field"""
        super().__init__(name="Design Output Feature (with CTQ ID #)")

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),
                val.not_empty(self.values),
                val.ctq_format(self.values),
                val.missing_ctq(self.values),
            ]


@Fields.collect_field()
class CTQ(ft.Field):

    def __init__(self):
        """CTQ field"""
        super().__init__(name="CTQ? Yes, No, N/A")

    def validate(self):
        """Validate this field"""
        self._val_results = self.val_results_header_and_field_exists()
        if self.found:
            self._val_results += [
                val.left_right_order(self),
                val.not_empty(self.values),
                val.ctq_valid_input(self.values),
                val.ctq_to_yes(self.values),
            ]


def get_expected_field_left(field):
    """Return the field object that *should* come before the argument field object."""
    initialized_fields = context.fields.get()
    index_prev_field = None
    for index, field_current in enumerate(initialized_fields):
        if field is field_current:
            index_prev_field = index - 1
            break
    if index_prev_field is None:
        raise ValueError
    elif index_prev_field == -1:
        return None
    else:
        return initialized_fields[index_prev_field]


if __name__ == "__main__":
    pass
