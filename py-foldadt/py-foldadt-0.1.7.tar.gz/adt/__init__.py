from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic, Union, Tuple

T1 = TypeVar('T1')
T2 = TypeVar('T2')
T3 = TypeVar('T3')
T4 = TypeVar('T4')
T5 = TypeVar('T5')
T6 = TypeVar('T6')
T7 = TypeVar('T7')
Out = TypeVar('Out')

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

def append2(d1: Sum2[T1, T2], d2: Sum2[T1, T3]) -> Sum2[T1, Tuple[T2, T3]]:
  if isinstance(d1, F2):
    if isinstance(d2, F2):
      return F2((d1.run, d2.run))
    else:
      return F1(d2.run)
  else:
    return F1(d1.run)

def join2(d: Sum2[T1, Sum2[T1, T2]]) -> Sum2[T1, T2]:
  if isinstance(d, F2):
    return d.run
  else:
    return F1(d.run)

def fold2(d: Sum2[T1, T2], 
          fold: Tuple[Callable[[T1], Out], Callable[[T2], Out]]) -> Out: 
  if isinstance(d, F1): 
    return fold[0](d.run)
  elif isinstance(d, F2): 
    return fold[1](d.run)
  else: assert False

def fold3(d: Sum3[T1, T2, T3],
          fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
                      Callable[[T3], Out]]) -> Out: 
  if isinstance(d, F1): 
    return fold[0](d.run)
  elif isinstance(d, F2): 
    return fold[1](d.run)
  elif isinstance(d, F3): 
    return fold[2](d.run)
  else: assert False

def fold4(d: Sum4[T1, T2, T3, T4],
          fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
                      Callable[[T3], Out], Callable[[T4], Out]]) -> Out: 
  if isinstance(d, F1): 
    return fold[0](d.run)
  elif isinstance(d, F2): 
    return fold[1](d.run)
  elif isinstance(d, F3): 
    return fold[2](d.run)
  elif isinstance(d, F4): 
    return fold[3](d.run)
  else: assert False

def fold5(d: Sum5[T1, T2, T3, T4, T5],
          fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
                      Callable[[T3], Out], Callable[[T4], Out],
                      Callable[[T5], Out]]) -> Out: 
  if isinstance(d, F1): 
    return fold[0](d.run)
  elif isinstance(d, F2): 
    return fold[1](d.run)
  elif isinstance(d, F3): 
    return fold[2](d.run)
  elif isinstance(d, F4): 
    return fold[3](d.run)
  elif isinstance(d, F5): 
    return fold[4](d.run)
  else: assert False

def fold6(d: Sum6[T1, T2, T3, T4, T5, T6],
          fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
                      Callable[[T3], Out], Callable[[T4], Out],
                      Callable[[T5], Out], Callable[[T6], Out]]) -> Out: 
  if isinstance(d, F1): 
    return fold[0](d.run)
  elif isinstance(d, F2): 
    return fold[1](d.run)
  elif isinstance(d, F3): 
    return fold[2](d.run)
  elif isinstance(d, F4): 
    return fold[3](d.run)
  elif isinstance(d, F5): 
    return fold[4](d.run)
  elif isinstance(d, F6): 
    return fold[5](d.run)
  else: assert False

def fold7(d: Sum7[T1, T2, T3, T4, T5, T6, T7],
          fold: Tuple[Callable[[T1], Out], Callable[[T2], Out],
                      Callable[[T3], Out], Callable[[T4], Out],
                      Callable[[T5], Out], Callable[[T6], Out],
                      Callable[[T7], Out]]) -> Out: 
  if isinstance(d, F1): 
    return fold[0](d.run)
  elif isinstance(d, F2): 
    return fold[1](d.run)
  elif isinstance(d, F3): 
    return fold[2](d.run)
  elif isinstance(d, F4): 
    return fold[3](d.run)
  elif isinstance(d, F5): 
    return fold[4](d.run)
  elif isinstance(d, F6): 
    return fold[5](d.run)
  elif isinstance(d, F7): 
    return fold[6](d.run)
  else: assert False
