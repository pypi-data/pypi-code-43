"""This module defines both the work item class (equivalent to a worksheet row)
and the work items class, a custom sequence contains all work items."""

# --- Standard Library Imports ------------------------------------------------
import collections
import functools

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.main.context_managers as context
from rtm.validate.checks import cell_empty


CascadeBlockCell = collections.namedtuple("CascadeBlockCell", "depth value")


class WorkItem:

    def __init__(self, index):
        """A work item is basically a row in the RTM worksheet. It's an item
        that likely a parent and at least one child."""
        self.index = index  # work item's vertical position relative to other work items
        self.edges = []

    @property
    @functools.lru_cache()
    def cascade_block_row(self):
        """Return list of tuples (depth, cell_value)"""
        cascade_block = context.fields.get().get_field_object('CascadeBlock')
        cascade_block_row_cells = cascade_block.get_row(self.index)
        return [
            CascadeBlockCell(depth, value)
            for depth, value in enumerate(cascade_block_row_cells)
            if not cell_empty(value)
        ]

    @property
    def value(self):
        try:
            return self.cascade_block_row[0][1]
        except IndexError:
            return None

    @property
    def depth(self):
        """Depth is equivalent to the number of edges from this work item to a root work item."""
        try:
            return self.cascade_block_row[0].depth
        except IndexError:
            return None

    @property
    def is_root(self):
        """Is this work item a Procedure Step?"""
        # TODO covered by test?
        return True if self.depth == 0 else False

    @property
    @functools.lru_cache()
    def parent(self):
        # TODO rename to parent
        """Return parent work item"""

        # If no position (cascade block row was blank), then no parent
        if self.depth is None:
            return MissingWorkItem(self)

        # If root item (e.g. procedure step), then no parent!
        if self.is_root:
            return MissingWorkItem(self)

        # Search backwards through previous work items
        work_items = context.work_items.get()
        for index in reversed(range(self.index)):

            other = work_items[index]

            if other.depth is None:
                # Skip work items that have a blank cascade. Keep looking.
                continue
            elif other.depth == self.depth:
                # same position, same parent
                return other.parent
            elif other.depth == self.depth - 1:
                # one column to the left; that work item IS the parent
                return other
            elif other.depth < self.depth - 1:
                # cur_work_item is too far to the left. There's a gap in the chain. No parent
                return MissingWorkItem(self)
            else:
                # self.position < other.position
                # Skip work items that come later in the cascade. Keep looking.
                continue

        # We should never get to this point. I was going to return a
        # MissingWorkItem at this point, but I'd rather an exception get thrown
        # and have to fix it.

    @property
    @functools.lru_cache()
    def root(self):
        """Return this work item's root item. The 'root' is the parent of the
        parent of the parent...etc. i.e. the Procedure Step"""
        if self.is_root:
            return self
        return self.parent.root

    @property
    def has_root(self) -> bool:
        # If a work item doesn't have a root, then that error will be caught elsewhere.
        # No need to return an error here.
        return self.root is not MissingWorkItem

    @property
    def allowed_to_be_terminal_work_item(self) -> bool:
        return self.depth >= 3

    def __repr__(self):
        return f"<d: {self.depth}, is_root: {self.is_root}, p: {self.parent.index}, r: {self.root.index}>"


class MissingWorkItem(WorkItem):

    def __init__(self, creator):
        super().__init__(-1)  # index = -1 (error)
        self.creator = creator

    @property
    def cascade_block_row(self):
        return []

    @property
    def depth(self):
        return None

    @property
    def is_root(self):
        return False

    @property
    def parent(self):
        return self

    @property
    def root(self):
        return self


class WorkItems(collections.abc.Sequence):

    def __init__(self):
        """Sequence of work items"""
        self._work_items = [WorkItem(index) for index in range(context.fields.get().height)]

    @property
    def child_count(self) -> dict:
        result = collections.defaultdict(int)
        for work_item in self:
            result[work_item.parent.index] += 1
        return result

    @property
    def childless_items(self) -> list:
        all_indices = set(range(len(self)))
        indices_with_children = set(self.child_count.keys())
        childless_indices = sorted(list(all_indices - indices_with_children))
        return [self[index] for index in childless_indices]

    @property
    def leaf_items(self):
        # Leaves meet two criteria:
        #   No children
        #   Has a root item
        #   Isn't a room item (which is actually redundant given the above check)
        # A "terminal" work item is a leaf in a graph: http://mathworld.wolfram.com/TreeLeaf.html
        return [work_item for work_item in self.childless_items if work_item.has_root]

    # --- Sequence ------------------------------------------------------------
    def __getitem__(self, item) -> WorkItem:
        return self._work_items[item]

    def __len__(self) -> int:
        return len(self._work_items)


if __name__ == "__main__":
    pass
    # class TestThingee:
    #     def __init__(self):
    #         self.stuff = 1
    #
    #     @property
    #     def stuff(self):
    #         return 2
    #
    # thingee = TestThingee()
    # print(thingee.stuff)
