from __future__ import annotations

import logging
_logger = logging.getLogger(__name__)

import collections
import functools
import inspect
import random
import weakref

from dataclasses import dataclass, field
from typing      import Iterable

from mnectar.config      import Setting
from mnectar.registry    import Registry, Plugin
from mnectar.util.signal import Signal

class View(Plugin, registry=Registry.Playlist):
    """
    A Read-Only view of a list of mrl records.

    This class takes any list of mrl records and acts as a read-only container for
    indexing into and iterating over the list of records.  The record can be of any
    Mapping data type (a dictionary-like object) so long as it provides an 'mrl'
    attribute so that records can be easily searched by mrl.

    This class is designed to work as a base-class for other read-only views which
    modify the apparent content of the list without modifying the actual underlying data
    object.  Each view based on this class should have unique methods so that multiple
    views may be combined to provide compound functionality.

    Recommended subclass implementation:

    * Create the subclass
    * Define an 'action' method (e.g. 'sort')
    * Mark the action method using the decorator ``@View.action``
    * In the action method:
      * Prepare a generator (or any Iterable type)
        * Each item must be a size 2 tuple:
          (orignal_content_index, original_content_value)
        * The original content *MUST* be accessed using ``self.all``
      * Update the content mapping:
        * ``self._populate_map(view_generator)``
    * Update the internal data mapping by calling `self._populate_map(view_generator)`

    Example:

        >>> class Sorted(View, registry=Registry.Playlist):
        ...     @View.action
        ...     def sort(self):
        ...         self._populate_map(sorted(
        ...             enumerate(self.all),
        ...             key=lambda _: _[1]
        ...         ))

    Views may also be chained together by providing one view as the initializer for
    another view.  If the above example usage is followed, the View class will
    automatically simplify the lookup process for each chained view so that calls to
    ``__getitem__()`` directly access the original list, bypassing the intermediate
    chained views.  This significantly improves performance.

    In addition, all available actions will be propogated to the chained
    view.

    Example:
        >>> class Filtered(View, registry=Registry.Playlist):
        ...     @View.action
        ...     def sort(self, column, value):
        ...         self._populate_map(filter(
        ...             lambda _: _[1][column] == value,
        ...             enumerate(self.all),
        ...         ))
        ... foo = Sorted(Filtered(my_library, app))
        ... foo.sort()
        ... foo.filter('album', 'My Album')
        ... foo[0] # 'Sorted' looks up the value in 'my_library' bypassing 'Filtered'

    Terminology:

    Inner Chain View:  A view used as content for another view
    Outer Chain View:  A view which uses this view as its content

    Example:

        >>> source_data = []
        ... view_1 = Editable(soruce_data)
        ... view_2 = Filtered(view_1)
        ... view_3 = Sorted(view_2)
        ... view_4 = Ordered(view_2)

    Considering the above code objects:

        view_1:
            - Inner View: None
            - Outer Views: view_2
        view_2:
            - Inner View: view_1
            - Outer Views: view_3, view_4
        view 3:
            - Inner View: view_2
            - Outer View: None
        view 4:
            - Inner View: view_2
            - Outer View: None
    """

    _first_only = False
    _default    = None

    @staticmethod
    def action(method):
        """
        Method decorator to be used with subclasses.

        Marks a method as a view action which is available when chaining together
        multiple views.
        """
        method._is_view_action = True

        @functools.wraps(method)
        def wrapped(self, *arg, **kw):
            return_value = method(self, *arg, **kw)
            self.update_outer()
            return return_value
        return wrapped

    @staticmethod
    def index_convert(argname):
        """
        Method decorator which marks a method as needing an index conversion when called
        from an outer chained view.

        Usage:
            class Foo(View, ...):
                @index_convert('idx')
                def my_func(self, idx):
                    ...
        """

        def decorator(method):
            argspec  = inspect.getfullargspec(method)
            if argname in argspec.args:
                # Save the location of the index arg for when calling as positional argument
                # ... But subtract 1 because this is a class method and 'self' should be
                #     ignored
                argindex = argspec.args.index(argname) - 1
            elif argname in argspec.kwonlyargs:
                # Will be found as a keyword, no need to save the index
                argindex = None
            else:
                raise ValueError(f"Index '{argname}' from decorator `@index_convert(...)` not found (not outer-most decorator?)")

            method._index_convert=(argname, argindex)
            return method

        return decorator

    def __index_convert_wrap(self, method):
        """
        Method decorator which will update an index in a chained view into an index in
        the view implementing the method.  This decorator is applied when classes are
        chained together, never as an explicit '@' decorator to the method.
        """

        argname, argindex  = method._index_convert

        @functools.wraps(method)
        def wrapped(*args, **kwargs):
            # Obtain the new index by doing a lookup of the object
            # ... this compares id values which are maintained between chained views
            # Once found, update the calling args/kwargs and call the real method
            if argname in kwargs:
                old_index = kwargs[argname]
                if old_index >= len(self):
                    kwargs[argname] = len(self.__chained)
                else:
                    new_index = self.__chained.index(self[old_index])
                    kwargs[argname] = new_index
            else:
                old_index = args[argindex]
                if old_index >= len(self):
                    new_args = list(args)
                    new_args[argindex] = len(self.__chained)
                    args = tuple(new_args)
                else:
                    new_args = list(args)
                    new_index = self.__chained.index(self[old_index])
                    new_args[argindex] = new_index
                    args = tuple(new_args)
            return method(*args, **kwargs)

        return wrapped

    def __init_subclass__(cls, first_only: bool = False, **kw):
        """
        Subclass Configuration Parameters:

        :param first_only: This view must be first in a chain (cannot be an outer view)
        """
        super().__init_subclass__(**kw)
        cls._first_only = first_only

    def __init__(self, content, app=None, *, default=None):
        if self._first_only and isinstance(content, View):
            raise ValueError(f"'{self.__class__.__name__}' view can only be the first view in a chain!")

        # Views can be initialized with no app if it is defined by the content.
        # ... This permits chaining view creation with no intermediate variables.
        # ... This must be done before initializing the parent class
        if app is None and hasattr(content, 'app'):
            app = content.app

        # But if app is still None, raise an error
        if app is None:
            raise TypeError("__init__() missing 1 required positional argument: 'app'")

        # Initialize the plugin class now the `app` variable is taken care of
        super().__init__(app)

        # Find any actions in the contained view and propogatre them to this view
        if isinstance(content, View):
            self.__chained = content
            self.__content = content.__content

            for name, method in inspect.getmembers(
                    content,
                    lambda _: hasattr(_, "_is_view_action")
            ):
                if not hasattr(self, name):
                    if hasattr(method, '_index_convert'):
                        method = self.__index_convert_wrap(method)
                    setattr(self, name, method)
        else:
            self.__chained = None
            self.__content = content

        # Create a set of outer chained views
        # ... An "outer chained view" is any view which uses THIS view as its content
        # ... This permits calling methods in any view and updating the entire chain in
        #     both directions.
        # ... A weak reference is used so that outer chained views can be safely deleted
        #     without invalidating the entire chain.
        self.__chained_outer = weakref.WeakSet()
        if self.__chained is not None:
            self.__chained.__chained_outer.add(self)

        # Save the default action (if any)
        # ... which is used optionally by the subclass
        # ... so no format or restriction is defined here!
        self._default = default

        # Perform the default action for the class
        self.update()

    def __add_outer_view(self, view):
        """
        Add a reference to an outer view
        """

    @property
    def all(self):
        """
        All records this view was initialized with.

        This may be another View object in the case of chained views.
        """
        if self.__chained is not None:
            return self.__chained
        else:
            return self.__content

    @property
    def inner(self):
        """
        The inner view (if any) or None if this is the top level view
        """
        if self.__chained is not None:
            return self.__chained
        else:
            return None

    @property
    def chain(self):
        """
        The compmlete inner chain (if any) including this view
        """
        chain = [self]
        view = self
        while view.inner:
            view = view.inner
            chain.append(view)
        return tuple(chain)

    @property
    def outer(self):
        """
        A weakref set of outer views which reference this view
        """
        return self.__chained_outer

    def _chained_index(self, index, who):
        """
        Convert a view index into an index into the original content.
        """
        if self.__chained is not None and self == who:
            return self.__chained._chained_index(index, who)
        elif who != self:
            return self._map_idx[index]
        else:
            return index

    def _populate_map(self, content: Iterable):
        """
        Update the view mapping for this view bsed on the provided iterator.  This
        method must be called any time this view may have changed.

        :param content: an iterable object returning (index,record) pairs
        """
        self._map_id = {
            id(rec): self._chained_index(index, self)
            for index,rec in content
        }
        self._map_idx = tuple(self._map_id.values())
        self._map_mrl = {
            self.__content[_].mrl: _
            for _ in self._map_idx
        }

    def update(self):
        """
        Update the view after the content has changed

        The default implementation simply refreshes the view from the content and should
        be overridden to use the action defined by the class, reapplying the most recent
        action applied.
        """
        self._populate_map(enumerate(self.all))

    def update_outer(self):
        """
        Update all outer elements in the view chain.

        An outer element is any view which uses this view as its content.
        """

        # Call a separate recursion method
        # ... This ensures this class is not accidentally updated twice
        for outer in self.outer:
            outer.__update_outer_recursion()

    def __update_outer_recursion(self):
        """
        Private method used for recursive outer chain view updates
        """
        # Update ourselves
        self.update()

        # Update outer views along the chain
        for outer in self.outer:
            outer.__update_outer_recursion()

    def __len__(self):
        return len(self._map_id)

    def __getitem__(self, index):
        try:
            if isinstance(index, int):
                return self.__content[self._map_idx[index]]
            elif isinstance(index, ViewPointer):
                return self[self.index(index)]
            elif isinstance(index, str):
                return self.__content[self._map_mrl[index]]
            elif isinstance(index, slice):
                return [self.__content[self._map_idx[_]] for _ in range(*index.indices(len(self)))]
            else:
                raise TypeError(f"Invalid index type: {type(index)}")
        except IndexError as ex:
            raise IndexError(f"Invalid View Index: {index}")
        except KeyError as ex:
            raise IndexError(f"Invalid View MRL: {index}")
        except ValueError as ex:
            raise IndexError(f"Invalid View Pointer: {index}")

    def __contains__(self, item):
        return (
            type(item) == str and item in self._map_mrl
            or id(item) in self._map_id and hasattr(item, 'mrl')
            or isinstance(item, ViewPointer) and item.valid and self.__contains__(item.record)
            or isinstance(item, View) and self.contains_view(item)
        )

    def contains_view(self, view: View) -> bool:
        """
        Implements __contains__ for a view, indicating if a specified view is contained
        in the inner chain of views for this object.

        :param view: The view to test
        :returns: True if `view` is an inner view of this view, else False
        """
        return view == self or (self.inner is not None and self.inner.contains_view(view))

    def contains_id(self, id_value: int) -> bool:
        """
        Test if the view contains the id() value of a record

        :param id_value: The id() value to test for
        :returns: True if `id_value` exists in this view
        """
        return id_value in self._map_id

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def index(self, item, *, is_id=False):
        if type(item) == int and is_id == True:
            return tuple(self._map_id.keys()).index(item)
        elif item in self and not type(item) == View:
            if type(item) == str:
                return tuple(self._map_mrl.keys()).index(item)
            elif isinstance(item, ViewPointer):
                return self.index(item.id, is_id=True)
            else:
                return tuple(self._map_id.keys()).index(id(item))
        else:
            raise ValueError(f"'{item}' not in playlist")

    def count(self, item):
        if type(item) == str:
            return len([_ for _ in self if _.mrl == item])
        elif isinstance(item, ViewPointer):
            return len([_ for _ in self if _ == item.record])
        else:
            return len([_ for _ in self if _ == item])

    def pointer(self, index: Union[int,str,ViewPointer]) -> ViewPointer:
        """
        Obtain a pointer to this view which can be used to iterate over records.

        :param index: An index into the view
        :returns: A view pointer (not valid if the index does not exist)
        """
        try:
            return ViewPointer(self.app, self, id(self[index]), self[index].mrl)
        except IndexError:
            return ViewPointer(self.app, self, )


class WholeLibrary(View, registry=Registry.Playlist):
    """
    This view is designed to work directly with the library to content to automatically
    update when files are added or removed from monitored directories.
    """

    def on_inserted_or_updated(self, records):
        """
        Library records have been inserted or updated externally.
        """
        for rec in records:
            # Look up using the MRL
            # ... lookup of the record directly will fail
            # ... because object ids are comapred
            if not rec['mrl'] in self.all:
                self.all.append(rec)

        self.update()
        self.update_outer()

    def on_deleted(self, records):
        """
        Library records have been deleted externally
        """
        for rec in records:
            # Look up using the MRL
            # ... lookup of the record directly will fail
            # ... because object ids are comapred
            if rec['mrl'] in self.all:
                self.all.remove(rec['mrl'])
        self.update()
        self.update_outer()


class Filtered(View, registry=Registry.Playlist):
    _default = ""

    def update(self):
        self.filter()

    @View.action
    def filter(self, filterstr=None):
        # Detect if the previous filter should be used ...
        if filterstr is None:
            filterstr = self._default or ""

        # Save the filter string for later use
        self._default = filterstr

        filtered = self.app.search.filtered(enumerate(self.all), filterstr, lambda _: _[1])

        self._populate_map(filtered)

class Sorted(View, registry=Registry.Playlist):
    _default = None

    def update(self):
        self.sort()

    @View.action
    def sort(self, column=None, reverse=False, *, smart=True):
        # Detect if the previous sort should be used ...
        if column is None:
            if type(self._default) in (list,tuple):
                column,reverse,smart = self._default
            elif type(self._default) == str:
                column = self._default
            else:
                column = self.app.columns[0].name

        # Convert any string column to an index
        elif type(column) == int:
            column = self.app.columns[column].name

        # Save the sort details for later use ....
        self._default = (column, reverse, smart)

        # Convert any string column to an index
        colnum = self.app.columns.indexOfName(column)

        if smart:
            # Collect sort details
            col_dict   = self.app.columns
            sort_cols  = self.app.columns[colnum].sortCols
            sort_funcs = [col_dict[_].sortFunc    for _ in sort_cols]
            sort_defs  = [col_dict[_].sortDefault for _ in sort_cols]
            sort_key   = lambda _: "#".join([f"{default if col not in _[1] else func(_[1], col)}" for col,func,default in zip(sort_cols,sort_funcs,sort_defs)])

            # Create sorted playlist generator
            sorted_playlist = sorted(enumerate(self.all), key=sort_key, reverse=reverse)

        else:
            sort_key = lambda _: self.app.columns[colnum].sortFunc(_[1],column)
            sorted_playlist = sorted(enumerate(self.all), key=sort_key, reverse=reverse)

        self._populate_map(sorted_playlist)

class Editable(View, registry=Registry.Playlist, first_only=True):
    """
    This is a mixin view (no View.action) methods defined which makes any view editable.
    """

    @View.action
    def append(self, item):
        self.all.append(item)
        self.update()

    @View.action
    @View.index_convert('index')
    def insert(self, index, item):
        if len(self) == 0:
            real_index = 0
        else:
            real_index = self._chained_index(index, self)
        self.all.insert(real_index, item)
        self.update()

    @View.action
    def extend(self, other):
        self.all.extend(other)
        self.update()

    @View.action
    @View.index_convert('index')
    def pop(self, index):
        real_index = self._chained_index(index, self)
        popped = self.all.pop(real_index)
        self.update()
        return popped

    @View.action
    def remove(self, value):
        if type(value) == str:
            self.all.remove(self[value])
        else:
            self.all.remove(value)
        self.update()

class Changed(View, registry=Registry.Playlist):
    """
    This is a mixin class (no View.aciton) which provides a signal indicating the
    content has changed in one of the chained views.

    Note that if the signal is not propogated to outer views!
    """

    changed = Signal() # All content changed (library reload)

    def update(self):
        super().update()
        self.changed.emit()


class Randomized(View, registry=Registry.Playlist):
    """
    Randomize the order of the view contents.
    """

    def update(self):
        self.randomize()

    @View.action
    def randomize(self):
        self._populate_map(random.sample(list(enumerate(self.all)), len(self.all)))


class Grouped(View, registry=Registry.Playlist):
    """
    Group the view content by a specified column without otherwise changing the order.

    In order to sort by the group wrap this around a Sorted view and sort by the same
    column.
    """

    _default = ""

    def update(self):
        self.group()

    @View.action
    def group(self, group=None):
        if group is None:
            group = self._default or ""

        self._default = group

        if group == "":
            super().update()
        else:
            # Using dict as an ordered set (python 3.7+)
            group_values = {_[group]: None for _ in self.all}
            groups = tuple(group_values.keys())
            self._populate_map(
                sorted(
                    enumerate(self.all),
                    key = lambda _: groups.index(_[1][group])
                )
            )


class RandomGroup(View, registry=Registry.Playlist):
    """
    Group the view by the specified column, randomizing the order of the groups without
    changing the order within each group.
    """

    _default = ""

    def update(self):
        self.randomize_group()

    @View.action
    def randomize_group(self, group=None):
        if group is None:
            group = self._default or ""

        self._default = group

        if group == "":
            super().update()
        else:
            # Using dict as an ordered set (python 3.7+)
            group_values = {_.get(group, ""): None for _ in self.all}
            groups = tuple(group_values.keys())
            group_randomized = random.sample(groups, len(groups))
            self._populate_map(
                sorted(
                    enumerate(self.all),
                    key = lambda _: group_randomized.index(_[1].get(group, ""))
                )
            )


class Shifted(View, registry=Registry.Playlist):
    """
    Resequence the playlist so that the current playing track is at the start of the
    playlist.  This is used by ordered view pointers to ensure that a new order plays
    all tracks in the playlist when not looping.
    """

    def update(self):
        self.shift()

    @View.action
    def shift(self, index=None):
        if index is None:
            index = self._default

        self._default = index

        if type(index) == int:
            start = index
        elif self.inner:
            try:
                start = self.inner.index(index)
            except ValueError:
                start = -1
        else:
            start = -1

        if 0 <= start < len(self.all):
            self._populate_map(
                sorted(
                    enumerate(self.all),
                    key = lambda _: _[0] + (len(self.all) if _[0] < start else 0)
                )
            )
        else:
            super().update()


class Selected(View, registry=Registry.Playlist):
    """
    Internal application view representing user selected records within a different view.
    """
    _default = []


    def update(self):
        self.select()

    @View.action
    def select(self, indicies=None):
        # Detect if the previous filter should be used ...
        if indicies is None:
            indicies = self._default or []

        if all([type(_) == int for _ in indicies]):
            # Created the filtered list of records based on index
            filtered = [(_, self.all[_]) for _ in indicies if _ < len(self.all)]
        elif all([type(_) == str for _ in indicies]):
            # Created the filtered list of records based on mrl
            filtered = [(self.all.index(_), self.all[_]) for _ in indicies if _ in self.all]
        elif all([type(_) == type(self.all[0]) for _ in indicies]):
            # Created the filtered list based on matching records
            filtered = [(self.all.index(_),_) for _ in indicies if _ in self.all]
        else:
            # Should never happen, but just in case ....
            filtered = []
            _logger.error(f"Unable to interpret selection list:\n{indicies}")

        self._populate_map(filtered)


@dataclass(frozen=True)
class ViewPointer:
    """
    A pointer used to iterate forwards and backwards through records in a view.
    Iteration order can optionally be modified by specifying an `order` view.
    """
    app:    object = None  # AppInit Instance (cannot import because of circular references)
    view:   View   = None
    id:     int    = 0
    mrl:    str    = ""
    order:  View   = field(default=None, compare=False, hash=True)

    loop = Setting('playback.loop', default=False)

    def reorder(self, order_view):
        """
        Create a new ordered view pointer.  This permits using an outer-chained view as
        a mechanism to access the view in this pointer without changing the actual view
        named by the pointer.  This maintains knowledge of the real data source for the
        pointer vs a different order in which it is accessed.
        """
        if not self.view in order_view:
            _logger.error("Attempt to create an ordered view pointer from views that are not chained!")
            return ViewPointer(self.app, self.view, order=order_view)
        else:
            if self.valid:
                rec = self.order[self.mrl]
                if rec in order_view:
                    idx = order_view.index(rec)
                    return ViewPointer(self.app, self.view, id(rec), rec.mrl, order_view)
                elif self.loop and len(order_view) > 0:
                    rec = order_view[0]
                    return ViewPointer(self.app, self.view, id(rec), rec.mrl, order_view)
                else:
                    return ViewPointer(self.app, self.view, order=order_view)
            else:
                return ViewPointer(self.app, self.view, order=order_view)

    def __post_init__(self):
        if self.order is None:
            object.__setattr__(self, 'order', self.view)

    def __iter__(self):
        pointer = start = self
        not_start = True
        while pointer.valid and not_start:
            yield pointer
            pointer = pointer.next
            not_start = pointer != start

    @property
    def view_index(self) -> int:
        if self.valid:
            return self.view.index(self.id, is_id=True)
        else:
            return None

    @property
    def order_index(self) -> int:
        if self.valid:
            return self.order.index(self.id, is_id=True)
        else:
            return None

    @property
    def valid(self) -> bool:
        """
        :returns: True if the pointer is valid (points to the correct record)
        """
        return self.order is not None and self.id != 0 and self.order.contains_id(self.id)

    @property
    def record(self):
        """
        Return the original record associated with this pointer.

        :returns: A record object or None if the record is not found.
        """
        if self.valid:
            return self.order[self.order_index]
        else:
            return None

    @property
    def next(self) -> ViewPointer:
        """
        Return the next pointer in the sequence, or raise a StopIteration exception if
        therre is no next record.

        :returns: A record object
        """
        if not self.valid:
            return ViewPointer(self.app, self.view, order=self.order)
        else:
            new = (self.order_index + 1)

            if self.loop:
                new %= len(self.order)

            if new >= len(self.order):
                return ViewPointer(self.app, self.view, order=self.order)

            rec = self.order[new]
            return ViewPointer(self.app, self.view, id(rec), rec.mrl, order=self.order)

    @property
    def prev(self) -> ViewPointer:
        """
        Return the previous pointer in the sequence, or raise a StopIteration exception if
        therre is no previous record.

        :returns: A record object
        """
        if not self.valid:
            return ViewPointer(self.app, self.view, order=self.order)
        else:
            new = (self.order_index - 1)

            if self.loop:
                new %= len(self.order)

            if new < 0:
                return ViewPointer(self.app, self.view, order=self.order)

            rec = self.order[new]
            return ViewPointer(self.app, self.view, id(rec), rec.mrl, order=self.order)

    @property
    def first(self) -> ViewPointer:
        """
        Return a pointer to the first record in the view.
        """
        pointer = self
        with ViewPointer.loop.tempval(self, False):
            while pointer.prev.valid:
                pointer = pointer.prev
        return pointer

    @property
    def last(self) -> ViewPointer:
        """
        Return a pointer to the last record in the view.
        """
        pointer = self
        with ViewPointer.loop.tempval(self, False):
            while pointer.next.valid:
                pointer = pointer.next
        return pointer
