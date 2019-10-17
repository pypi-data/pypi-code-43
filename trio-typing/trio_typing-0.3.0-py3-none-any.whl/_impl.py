import trio
from abc import abstractmethod, abstractproperty
from typing import (
    Any,
    Awaitable,
    Callable,
    FrozenSet,
    Generic,
    Optional,
    TypeVar,
    overload,
)
from typing_extensions import Protocol
from mypy_extensions import NamedArg

__all__ = ["CancelScope", "Nursery", "TaskStatus"]

T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


class TaskStatus(Protocol[T_contra]):
    # PLUGIN: disallow bare .started() when type does not include None
    @abstractmethod
    @overload
    def started(self) -> None:
        ...

    @abstractmethod
    @overload
    def started(self, value: T_contra) -> None:
        ...

    @abstractmethod
    def started(self, value: Optional[T_contra] = None) -> None:
        raise NotImplementedError


class CancelScope(Protocol):
    deadline: float
    shield: bool
    cancel_called: bool
    cancelled_caught: bool

    @abstractmethod
    def cancel(self) -> None:
        raise NotImplementedError


class Nursery(Protocol):
    cancel_scope: CancelScope

    @abstractproperty
    def child_tasks(self) -> FrozenSet[trio.hazmat.Task]:
        raise NotImplementedError

    @abstractproperty
    def parent_task(self) -> trio.hazmat.Task:
        raise NotImplementedError

    # PLUGIN: properly variadic start_soon() and start()
    @abstractmethod
    @overload
    def start_soon(
        self, async_fn: Callable[[], Awaitable[None]], *, name: object = None
    ) -> None:
        ...

    @abstractmethod
    @overload
    def start_soon(
        self,
        async_fn: Callable[[T1], Awaitable[None]],
        __arg1: T1,
        *,
        name: object = None
    ) -> None:
        ...

    @abstractmethod
    @overload
    def start_soon(
        self,
        async_fn: Callable[[T1, T2], Awaitable[None]],
        __arg1: T1,
        __arg2: T2,
        *,
        name: object = None
    ) -> None:
        ...

    @abstractmethod
    @overload
    def start_soon(
        self,
        async_fn: Callable[[T1, T2, T3], Awaitable[None]],
        __arg1: T1,
        __arg2: T2,
        __arg3: T3,
        *,
        name: object = None
    ) -> None:
        ...

    @abstractmethod
    @overload
    def start_soon(
        self,
        async_fn: Callable[[T1, T2, T3, T4], Awaitable[None]],
        __arg1: T1,
        __arg2: T2,
        __arg3: T3,
        __arg4: T4,
        *,
        name: object = None
    ) -> None:
        ...

    @abstractmethod  # type: ignore
    def start_soon(self, async_fn: object, *, name: object = None) -> None:
        raise NotImplementedError

    @abstractmethod
    @overload
    async def start(
        self,
        async_fn: Callable[[NamedArg(TaskStatus[T], "task_status")], Awaitable[None]],
        *,
        name: object = None
    ) -> T:
        ...

    @abstractmethod
    @overload
    async def start(
        self,
        async_fn: Callable[
            [T1, NamedArg(TaskStatus[T], "task_status")], Awaitable[None]
        ],
        __arg1: T1,
        *,
        name: object = None
    ) -> T:
        ...

    @abstractmethod
    @overload
    async def start(
        self,
        async_fn: Callable[
            [T1, T2, NamedArg(TaskStatus[T], "task_status")], Awaitable[None]
        ],
        __arg1: T1,
        __arg2: T2,
        *,
        name: object = None
    ) -> T:
        ...

    @abstractmethod
    @overload
    async def start(
        self,
        async_fn: Callable[
            [T1, T2, T3, NamedArg(TaskStatus[T], "task_status")], Awaitable[None]
        ],
        __arg1: T1,
        __arg2: T2,
        __arg3: T3,
        *,
        name: object = None
    ) -> T:
        ...

    @abstractmethod
    @overload
    async def start(
        self,
        async_fn: Callable[
            [T1, T2, T3, T4, NamedArg(TaskStatus[T], "task_status")], Awaitable[None]
        ],
        __arg1: T1,
        __arg2: T2,
        __arg3: T3,
        __arg4: T4,
        *,
        name: object = None
    ) -> T:
        ...

    @abstractmethod  # type: ignore
    async def start(self, async_fn: object, *, name: object = None) -> Any:
        raise NotImplementedError
