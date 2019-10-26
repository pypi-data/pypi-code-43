from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic, List, Union, Tuple, Type

T1 = TypeVar('T1')
T2 = TypeVar('T2')
T3 = TypeVar('T3')
T4 = TypeVar('T4')
T5 = TypeVar('T5')
T6 = TypeVar('T6')
T7 = TypeVar('T7')
Out = TypeVar('Out')

class Fn(Generic[T1, T2]):
  def __init__(self, c: Callable[[T1], T2]) -> None:
    self.c = c

  def __call__(self, t1: T1) -> T2:
    return self.c(t1)
  
@dataclass
class F1(Generic[T1]):
  run: T1
@dataclass
class F2(Generic[T2]):
  run: T2 
@dataclass
class F3(Generic[T3]):
  run: T3 
@dataclass
class F4(Generic[T4]):
  run: T4 
@dataclass
class F5(Generic[T5]):
  run: T5 
@dataclass
class F6(Generic[T6]):
  run: T6 
@dataclass
class F7(Generic[T7]):
  run: T7 

Sum2 = Union[F1[T1], F2[T2]]
Sum3 = Union[F1[T1], F2[T2], F3[T3]]
Sum4 = Union[F1[T1], F2[T2], F3[T3], F4[T4]]
Sum5 = Union[F1[T1], F2[T2], F3[T3], F4[T4], F5[T5]]
Sum6 = Union[F1[T1], F2[T2], F3[T3], F4[T4], F5[T5], F6[T6]]
Sum7 = Union[F1[T1], F2[T2], F3[T3], F4[T4], F5[T5], F6[T6], F7[T7]]

class Semigroup(Generic[T1], ABC):
  @abstractmethod
  def append(self, a1: T1, a2: T1) -> T1: pass

class KeepLeft(Semigroup[T1]):
  def append(self, a1: T1, a2: T1) -> T1:
    return a1

class KeepRight(Semigroup[T1]):
  def append(self, a1: T1, a2: T1) -> T1:
    return a2

class ListSg(Generic[T1], Semigroup[List[T1]]):
  def append(self, a1: List[T1], a2: List[T1]) -> List[T1]:
    return a1 + a2

def append2(d1: Sum2[T1, T2], d2: Sum2[T1, T3]) -> Sum2[T1, Tuple[T2, T3]]:
  return append2sg(d1, d2, KeepLeft[T1]())

def append2sg(d1: Sum2[T1, T2], d2: Sum2[T1, T3], sg: Semigroup[T1]) -> Sum2[T1, Tuple[T2, T3]]:
  if isinstance(d1, F2):
    if isinstance(d2, F2):
      return F2((d1.run, d2.run))
    else:
      return F1(d2.run)
  else:
    if isinstance(d2, F1):
      return F1(sg.append(d1.run, d2.run))
    else:
      return F1(d1.run)

def join2(d: Sum2[T1, Sum2[T1, T2]]) -> Sum2[T1, T2]:
  if isinstance(d, F2):
    return d.run
  else:
    return F1(d.run)

def bind2(d: Sum2[T1, T2], k: Callable[[T2], Sum2[T1, T3]]) -> Sum2[T1, T3]:
  if isinstance(d, F2):
    return k(d.run)
  else:
    return d

def liftBind2(t: Type[T1], k: Callable[[T2], Sum2[T1, T3]]) -> Callable[[Sum2[T1, T2]], Sum2[T1, T3]]:
  def x(d: Sum2[T1, T2]) -> Sum2[T1, T3]:
    return bind2(d, k)
  return x

def map2(d: Sum2[T1, T2], f: Callable[[T2], T3]) -> Sum2[T1, T3]:
  if isinstance(d, F2):
    return F2(f(d.run))
  else:
    return d

def lift2(t: Type[T1], f: Callable[[T2], T3]) -> Callable[[Sum2[T1, T2]], Sum2[T1, T3]]:
    def x(d: Sum2[T1, T2]) -> Sum2[T1, T3]:
      return map2(d, f)
    return x

@dataclass
class fold2(Generic[T1, T2, Out]):
  fold: Tuple[Callable[[T1], Out], Callable[[T2], Out]]

  def __call__(self, d: Sum2[T1, T2]) -> Out:
    if isinstance(d, F1): 
      return self.fold[0](d.run)
    elif isinstance(d, F2): 
      return self.fold[1](d.run)
    else: assert False

@dataclass
class fold3(Generic[T1, T2, T3, Out]):
  fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
              Callable[[T3], Out]]

  def __call__(self, d: Sum3[T1, T2, T3]) -> Out:
    if isinstance(d, F1): 
      return self.fold[0](d.run)
    elif isinstance(d, F2): 
      return self.fold[1](d.run)
    elif isinstance(d, F3): 
      return self.fold[2](d.run)
    else: assert False

@dataclass
class fold4(Generic[T1, T2, T3, T4, Out]):
  fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
                Callable[[T3], Out], Callable[[T4], Out]]

  def __call__(self, d: Sum4[T1, T2, T3, T4]) -> Out:
    if isinstance(d, F1): 
      return self.fold[0](d.run)
    elif isinstance(d, F2): 
      return self.fold[1](d.run)
    elif isinstance(d, F3): 
      return self.fold[2](d.run)
    elif isinstance(d, F4): 
      return self.fold[3](d.run)
    else: assert False

@dataclass
class fold5(Generic[T1, T2, T3, T4, T5, Out]):
  fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
              Callable[[T3], Out], Callable[[T4], Out],
              Callable[[T5], Out]]

  def __call__(self, d: Sum5[T1, T2, T3, T4, T5]) -> Out:
    if isinstance(d, F1): 
      return self.fold[0](d.run)
    elif isinstance(d, F2): 
      return self.fold[1](d.run)
    elif isinstance(d, F3): 
      return self.fold[2](d.run)
    elif isinstance(d, F4): 
      return self.fold[3](d.run)
    elif isinstance(d, F5): 
      return self.fold[4](d.run)
    else: assert False

@dataclass
class fold6(Generic[T1, T2, T3, T4, T5, T6, Out]):
  fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
              Callable[[T3], Out], Callable[[T4], Out],
              Callable[[T5], Out], Callable[[T6], Out]]

  def __call_(self, d: Sum6[T1, T2, T3, T4, T5, T6]) -> Out:
    if isinstance(d, F1): 
      return self.fold[0](d.run)
    elif isinstance(d, F2): 
      return self.fold[1](d.run)
    elif isinstance(d, F3): 
      return self.fold[2](d.run)
    elif isinstance(d, F4): 
      return self.fold[3](d.run)
    elif isinstance(d, F5): 
      return self.fold[4](d.run)
    elif isinstance(d, F6): 
      return self.fold[5](d.run)
    else: assert False

@dataclass
class fold7(Generic[T1, T2, T3, T4, T5, T6, T7, Out]):
  fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
              Callable[[T3], Out], Callable[[T4], Out],
              Callable[[T5], Out], Callable[[T6], Out],
              Callable[[T7], Out]]

  def __call__(self, d: Sum7[T1, T2, T3, T4, T5, T6, T7]) -> Out:
    if isinstance(d, F1): 
      return self.fold[0](d.run)
    elif isinstance(d, F2): 
      return self.fold[1](d.run)
    elif isinstance(d, F3): 
      return self.fold[2](d.run)
    elif isinstance(d, F4): 
      return self.fold[3](d.run)
    elif isinstance(d, F5): 
      return self.fold[4](d.run)
    elif isinstance(d, F6): 
      return self.fold[5](d.run)
    elif isinstance(d, F7): 
      return self.fold[6](d.run)
    else: assert False
