# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Modules for log scope, including the definition of context manager and decorator."""
import uuid
from functools import wraps
from datetime import datetime
from copy import deepcopy
from contextlib import contextmanager
from collections import deque

from azureml import telemetry
from azureml.telemetry.contracts import Event as _Event, RequiredFields as _RequiredFields


class LogScope:
    """Represents a single log scope in which some scope specific log context info is stored."""

    @staticmethod
    def get_current() -> 'LogScope':
        """Get the current LogScope in effect.

        :return: Returns the current LogScope.
        :rtype: LogScope
        """
        return _ScopeStack._current()

    @staticmethod
    def get_root() -> 'LogScope':
        """Get the root scope in current scope stack."""
        return _ScopeStack._root()

    def __init__(self, component_name, scope_name, na_properties: set = None, parent_scope: 'LogScope' = None,
                 **kwargs):
        """Construct a LogScope."""
        self.component_name = component_name
        self.name = scope_name
        self._parent_scope = parent_scope
        if parent_scope is None:
            self.shared_context = {}  # init the shared_context for the top level log scope

        # first, set na_properties, so that they will be available if neither parent nor current scope defines them
        na_value = 'NotAvailable'
        self.scoped_context = {k: na_value for k in na_properties} if na_properties is not None else {}

        # second, inherit from parent_scope
        self.id = str(uuid.uuid4())
        if parent_scope is not None:
            self.parent_id = parent_scope.id
            self.scoped_context.update(deepcopy(parent_scope.scoped_context))
        else:
            self.parent_id = self.id

        # third, save any properties passed in
        if kwargs is not None:
            self.scoped_context.update(kwargs)

    def __setitem__(self, key, value):
        """Assign value to the log signal key within this log scope."""
        self.scoped_context[key] = value

    def __getitem__(self, key):
        """Get the value of the log signal key within this log scope."""
        root_scope = _ScopeStack._root()
        shared_value = None if root_scope is None else root_scope.shared_context.get(key, None)
        return self.scoped_context.get(key, shared_value)

    def __contains__(self, key):
        """To check if signal key is set in the log scope."""
        return key in self.scoped_context or key in _ScopeStack._root().shared_context

    def __str__(self):
        """Return a string to show the log signals this log scope contains."""
        return self.scoped_context.__str__()

    def set_shared_value(self, key, value):
        """Set the value which will be shared inside the top scope.

        :param key: The name of the key.
        :type key: str
        :param value: The value of the key to set.
        :type value: str
        """
        if key in self.scoped_context:
            # that means key is set in current scope or inherited from a parent scope
            conflict_scope = next(  # find the top most one
                (s for s in _ScopeStack._ctx_stack if s.scoped_context.get(key, value) != value),
                None)
            if conflict_scope:
                # todo: log a special event
                print('shared context conflict for {}, value from component {} in scope {} is {}' +
                      'while value from component {} in scope {} is {}.'
                      .format(key, self.component_name, self.name, value, conflict_scope.component_name,
                              conflict_scope.name, conflict_scope[key]))
                return

        # set the value to shared context
        top_scope = _ScopeStack._root()
        top_scope.shared_context[key] = value

    def get_rollup_value(self, key):
        """Get the value for the key from scope, and all its parent scopes, along with component and scope name.

        :param key: The name of the key for which you want to get the rollup value.
        :type key: str
        :return: A list of tuples consisting of the component name, scope name, and value.
        :rtype: builtin.list [(str, str, str)]

        """
        compound_values = []
        curr_scope = self
        while curr_scope is not None:
            val = curr_scope[key]
            if val is None:
                # key is not in curr_scope, this implies it is not in any of its parent scopes
                # (otherwise it will be inheritted), so it it is safe to stop the iteration
                break
            compound_values.append((curr_scope.component_name, curr_scope.name, curr_scope[key]))
            curr_scope = curr_scope._parent_scope
        return compound_values

    ROOT_SCOPE_ID = "RootScopeId"
    PARENT_SCOPE_ID = "ParentScopeId"
    SCOPE_ID = "ScopeId"

    def get_merged_props(self, props: dict) -> dict:
        """Merge passed in props with those context info collected in the log scope."""
        merged = self.scoped_context.copy()
        merged.update(props)
        merged[LogScope.SCOPE_ID] = self.id
        merged[LogScope.PARENT_SCOPE_ID] = self.parent_id
        merged[LogScope.ROOT_SCOPE_ID] = self.get_root().id
        return merged


class _ScopeStack:
    """The stack to contain all the current nested log scopes."""

    _ctx_stack = deque([])

    @classmethod
    def _create_and_push(cls, component_name, name, na_properties, **kwargs) -> LogScope:
        next = LogScope(component_name, name, na_properties, cls._current(), **kwargs)
        cls._ctx_stack.append(next)
        return next

    @classmethod
    def _pop(cls) -> LogScope:
        return cls._ctx_stack.pop()

    @classmethod
    def _current(cls) -> LogScope:
        return cls._ctx_stack[-1] if cls._ctx_stack else None

    @classmethod
    def _root(cls) -> LogScope:
        return cls._ctx_stack[0] if cls._ctx_stack else None


@contextmanager
def context_scope(component_name, name, track=False, na_properties: set = None, **kwargs) -> LogScope:
    """
    Initialize a log scope.

    :param component_name: The name of the component that owns the scope.
    :type component_name: str
    :param name: The name of the scope.
    :type name: str
    :param track: Indicates if a context scope or a tracking scope should be returned.
    :type track: bool
    :param na_properties: A set of property names which are not available within the scope, and will be filled
        with value 'NotAvailable' if they are not set in any of the parent scope.
    :type na_properties: set
    :param kwargs: The list of the key/value pairs which will be initially stored in the log scope.
    :param kwargs: dict
    :return: If ``track`` is False, which it is by default, then this function returns a normal context scope;
        otherwise, it returns a track scope which will track the duration, complete status and error message
        automatically.
    :rtype: LogScope

    """
    if track:
        start_time = datetime.utcnow()
        exception = None
        completion_status = 'success'
    try:
        scope = _ScopeStack._create_and_push(component_name, name, na_properties, **kwargs)
        yield scope
    except Exception as e:
        completion_status = 'failure'
        exception = e
        raise e
    finally:
        if track:
            end_time = datetime.utcnow()
            duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)

            scope['completionStatus'] = completion_status
            scope['durationMs'] = duration_ms
            err_msg = str(exception) if exception else None
            logger = telemetry.get_event_logger()
            track_event = _Event(
                name='{}.Scope.Tracking'.format(scope.component_name),
                required_fields=_RequiredFields(),
                extension_fields={
                    'tracking_msg': 'scope {}|{}, completed with status {}, duration {}ms. error msg: {}'
                                    .format(component_name, name, completion_status, duration_ms, err_msg)
                }
            )
            logger.log_event(track_event)
        _ScopeStack._pop()


def ctx_scope(component_name, track=False, na_properties=None, **prop_kwargs):
    """ctx_scope is a function decorator, which is a short cut of context_scope applied on a whole function."""
    def cntx_scope(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with context_scope(component_name, func.__name__, track, na_properties, **prop_kwargs):
                return func(*args, **kwargs)

        return wrapper
    return cntx_scope
