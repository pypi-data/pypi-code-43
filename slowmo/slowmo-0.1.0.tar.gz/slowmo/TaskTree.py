from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from slowmo.Task import Task


@dataclass(frozen=True)
class TaskTree:
    task: Task
    subtrees: Tuple[TaskTree, ...] = tuple()

    @staticmethod
    def get_at(tt: TaskTree, path: Tuple[int, ...]) -> TaskTree:
        if len(path) == 0:
            return tt

        ix = path[0]
        st = tt.subtrees[ix]
        return TaskTree.get_at(st, path[1:])

    @staticmethod
    def replace_at(
        tt: TaskTree, path: Tuple[int, ...], replace: Callable[[TaskTree], TaskTree]
    ) -> TaskTree:
        if len(path) == 0:
            return replace(tt)
        ix = path[0]
        sts = tt.subtrees
        subtrees = (
            *sts[:ix],
            TaskTree.replace_at(sts[ix], path[1:], replace),
            *sts[ix + 1 :],
        )
        return TaskTree(tt.task, subtrees)

    @staticmethod
    def add_subtree(tt: TaskTree, st: TaskTree) -> TaskTree:
        return TaskTree(tt.task, tt.subtrees + (st,))

    @staticmethod
    def display(tt: TaskTree, path=tuple(), spinner="X") -> str:
        d = ["\t" * len(path) + Task.display(tt.task, spinner)]
        for i, st in enumerate(tt.subtrees):
            d += [TaskTree.display(st, path + (i,), spinner)]
        return "\n".join(d)

    @staticmethod
    def size(root: TaskTree) -> int:
        if len(root.subtrees) == 0:
            return 1
        return 1 + sum(TaskTree.size(st) for st in root.subtrees)
