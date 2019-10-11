from typing import *
from typing_inspect import is_generic_type, get_args, get_origin

from dataclasses_json import DataClassJsonMixin

def is_list_type(tp) -> bool:
    """
    Test if the type is a generic list type, including subclasses excluding
    non-generic classes.
    Examples::
    
    is_list_type(int) == False
    is_list_type(list) == False
    is_list_type(List) == True
    is_list_type(List[str, int]) == True
    class MyClass(List[str]):
        ...
    is_list_type(MyClass) == True
    """
    
    return is_generic_type(tp) and issubclass(get_origin(tp) or tp, List)

T = TypeVar('T')
@overload
def unfold_list_type(tp: Type[List[T]]) -> Type[T]:
    pass
@overload
def unfold_list_type(tp: Type[T]) -> None:
    pass
@overload
def unfold_list_type(tp: Any) -> None:
    pass
def unfold_list_type(tp: Union[Type[List[T]], Any]) -> Optional[Type[T]]:
    """
    Checks argument is Type[List[T]], and returns Type[T]; None otherwise
    Examples::
    
    unfold_list_type(int) == None
    unfold_list_type(list) == None
    unfold_list_type(List) == None
    unfold_list_type(List[int]) == int
    class MyClass(List[str]):
        ...
    unfold_list_type(MyClass) == None
    unfold_list_type(List[MyClass]) == MyClass
    
    :param tp: Type[List[T]] or Any
    :return: Optional[Type[T]]
    """
    
    if (not is_list_type(tp)):
        return None
    x = get_args(tp)
    if (x and isinstance(x, tuple)):
        if (len(x) == 1):
            x = x[0]
        else:
            return None

    if (x and isinstance(x, type)):
        # noinspection PyTypeChecker
        return x
    else:
        return None

_MT = DataClassJsonMixin
ModelType = TypeVar('ModelType', bound=_MT)
def unfold_json_dataclass_list_type(model: Union[Type[ModelType], Type[List[ModelType]]], *, check_match: bool = True) -> Tuple[Type[ModelType], bool]:
    """
    Checks argument is either Type[List[T]] or Type[T] where T is a json dataclass,
    and returns Type[T] and (is argument a list-type)
    Raises TypeError exception if T is not a json dataclass 
    
    Examples::
    
    @dataclass
    class MyJsonDataclass(DataClassJsonMixin):
        ...
    unfold_json_dataclass_list_type(MyJsonDataclass) == (MyJsonDataclass, False)
    unfold_json_dataclass_list_type(List[MyJsonDataclass]) == (MyJsonDataclass, True)
    
    # But!
    
    unfold_json_dataclass_list_type(int) # raises TypeError
    unfold_json_dataclass_list_type(list) # raises TypeError
    unfold_json_dataclass_list_type(List) # raises TypeError
    unfold_json_dataclass_list_type(List[int]) # raises TypeError
    class MyClass(List[str]):
        ...
    unfold_list_type(MyClass) # raises TypeError
    unfold_list_type(List[MyClass]) # raises TypeError
    
    :param model: Type[T] or Type[List[T]]
    :param check_match: bool (optional, default: True)
    If True, checks T is a json dataclass, and raises a TypeError if it is not.
    :return Type[T], bool
     - first: expanded type T
     - second: True if argument was List[T], False otherwise
    :raises TypeError if T is not a json dataclass
    """
    
    tp = unfold_list_type(model)
    if (tp is None):
        multi = False
        tp = model
    else:
        multi = True
    
    if (check_match):
        if (not issubclass(tp, _MT)):
            raise TypeError(f"'{tp}' from '{model}' (type: '{type(model)}') is neither a json dataclass nor list of json dataclass")
    
    return tp, multi

__all__ = \
[
    'unfold_list_type',
    'unfold_json_dataclass_list_type',
    'is_list_type',
]
