import inspect

from strategery.exceptions import StrategyError


def get_requirements(targets, preprocessed):
    requirements = set([t for t in targets if t not in preprocessed])
    visited = set([key for key in preprocessed])

    while True:
        to_visit = [req for req in requirements if req not in visited]
        if len(to_visit) is 0:
            break
        for task in to_visit:
            visited.add(task)
            if hasattr(task, "dependencies"):
                for dep in task.dependencies:
                    if not callable(dep) and dep not in preprocessed:
                        raise StrategyError('Task {t} failed, expected parameter {d}, but parameter was not found.\nat "{f}:{l}".'.format(
                            t=task.__name__,
                            d=dep.__name__ if hasattr(dep, "__name__") else str(dep),
                            f=inspect.getmodule(task).__file__,
                            l=task.__code__.co_firstlineno
                        ))
                    if dep not in visited:
                        requirements.add(dep)

    return requirements

def dependencies_met(task, queue, preprocessed):
    flat = set(preprocessed)
    for stage in queue:
        flat = flat.union(stage)

    if hasattr(task, "dependencies"):
        for dep in task.dependencies:
            if dep not in flat:
                return False

    return True

def get_strategy(targets, start, preprocessed):
    requirements = get_requirements(targets, preprocessed)
    queue = []
    if start:
        queue.append([start])
        requirements.remove(start)
    while (len(requirements) > 0):
        ready_tasks = [req for req in requirements if dependencies_met(req, queue, preprocessed)]
        if len(ready_tasks) > 0:
            queue.append(ready_tasks)
            for task in ready_tasks:
                requirements.remove(task)
            continue

        raise Exception("Couldn't resolve a strategy for targets " + targets)
    return queue