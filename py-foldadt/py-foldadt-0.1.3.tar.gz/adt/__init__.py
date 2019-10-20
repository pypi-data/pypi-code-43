from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic, Union, NamedTuple

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

class Fold2(ABC, Generic[T1, T2, Out]):
  @abstractmethod
  def f1(self, f: T1) -> Out: pass
  @abstractmethod
  def f2(self, f: T2) -> Out: pass

  def __call__(self, d: Sum2[T1, T2]) -> Out:
    if isinstance(d, F1): 
      return self.f1(d.run)
    elif isinstance(d, F2): 
      return self.f2(d.run)
    else: assert False

class Fold3(Fold2[T1, T2, Out], Generic[T1, T2, T3, Out]):
  @abstractmethod
  def f3(self, f: T3) -> Out: pass

  def __call__(self, d: Sum3[T1, T2, T3]) -> Out:
    if isinstance(d, F3): 
      return self.f3(d.run)
    else: 
      return super().__call__(d)

class Fold4(Fold3[T1, T2, T3, Out], Generic[T1, T2, T3, T4, Out]):
  @abstractmethod
  def f4(self, f: T4) -> Out: pass

  def __call__(self, d: Sum4[T1, T2, T3, T4]) -> Out:
    if isinstance(d, F4): 
      return self.f4(d.run)
    else: 
      return super().__call__(d)

class Fold5(Fold4[T1, T2, T3, T4, Out], Generic[T1, T2, T3, T4, T5, Out]):
  @abstractmethod
  def f5(self, f: T5) -> Out: pass

  def __call__(self, d: Sum5[T1, T2, T3, T4, T5]) -> Out:
    if isinstance(d, F5): 
      return self.f5(d.run)
    else: 
      return super().__call__(d)

class Fold6(Fold5[T1, T2, T3, T4, T5, Out], 
            Generic[T1, T2, T3, T4, T5, T6, Out]):
  @abstractmethod
  def f6(self, f: T6) -> Out: pass

  def __call__(self, d: Sum6[T1, T2, T3, T4, T5, T6]) -> Out:
    if isinstance(d, F6): 
      return self.f6(d.run)
    else: 
      return super().__call__(d)

class Fold7(Fold6[T1, T2, T3, T4, T5, T6, Out], 
            Generic[T1, T2, T3, T4, T5, T6, T7, Out]):
  @abstractmethod
  def f7(self, f: T7) -> Out: pass

  def __call__(self, d: Sum7[T1, T2, T3, T4, T5, T6, T7]) -> Out:
    if isinstance(d, F7): 
      return self.f7(d.run)
    else: 
      return super().__call__(d)

