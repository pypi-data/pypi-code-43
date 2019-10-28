"""SQLAlchemy-Function

This module defines a FunctionMixin and FunctionBase. The FunctionMixin is a 
mixin for creating Function models. The FunctionBase is a base mixin for 
models which are parents of Function models.
"""

from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.inspection import inspect
from sqlalchemy_mutable import MutableListType, MutableDictType


class FunctionMixin():
    """Mixin for Function models

    A Function model has a parent, a function, args, and kwargs. When called
    the Function model executes its function, passing in its parent (if 
    applicable) and its args and kwargs.

    Function models also have an index for convenient use with ordering_list.
    """
    index = Column(Integer)
    _func = Column(PickleType)
    args = Column(MutableListType)
    kwargs = Column(MutableDictType)

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, value):
        assert value is None or callable(value), (
            'Attempted to set function attribute to non-function value'
            )
        self._func = value

    def __init__(self, parent=None, func=None, args=[], kwargs={}):
        if parent is not None:
            self.parent = parent
        self.func = func
        self.args, self.kwargs = args, kwargs
        super().__init__()
    
    def __call__(self):
        if self.func is None:
            return
        if hasattr(self, 'parent'):
            return self.func(self.parent, *self.args, **self.kwargs)
        return self.func(*self.args, **self.kwargs)


class FunctionBase():
    """Function base mixin

    Models which are parents of Function models should inherit this base. 
    They should call _set_function_relationships before any Function 
    attributes are set.
    
    Users can then set function attributes to functions or function models. 
    When set to functions, FunctionBase will automatically convert the
    functions to Function models.

    e.g. the following commands are equivalent:
    model.function = function 
    model.function = Function(parent=model, func=function)

    Similar logic applies to lists. e.g. the following are equivalent:
    model.functions = function
    model.functions = [function]
    model.functions = Function(parent=model, func=function)
    model.functions = [Function(parent=model, func=function)]
    """
    _function_relationships = Column(PickleType)
    
    def __setattr__(self, name, value):
        """
        Convert value to Function model if setting a function relationship
        """
        if name == '_sa_instance_state':
            return super().__setattr__(name, value)
        function_relationships = self._function_relationships or []
        if name in function_relationships:
            relationship = inspect(self).mapper.relationships[name]
            model_class = relationship.mapper.class_
            if relationship.uselist:
                value = value if isinstance(value, list) else [value]
                value = self._to_function_models(value, model_class)
            else:
                value = self._to_function_model(value, model_class)
        return super().__setattr__(name, value)

    def _to_function_models(self, funcs, model_class):
        """Convert a list of functions to Function models"""
        models = [self._to_function_model(f, model_class) for f in funcs]
        return [m for m in models if m is not None]
    
    def _to_function_model(self, func, model_class):
        """Convert a single function to a Function model"""
        if isinstance(func, model_class):
            return func
        if callable(func):
            return model_class(self, func)
        if func is None:
            return None
        raise ValueError(
            'Function relationships requre Function models or callables'
        )

    def _set_function_relationships(self):
        """Find and store all function relationships
        
        Models which inherit from FunctionModelBase should call this 
        before function attributes are assigned.
        """
        relationships = inspect(self).mapper.relationships
        self._function_relationships = [
            r.key for r in relationships 
            if FunctionMixin in r.mapper.class_.__mro__
        ]