from unittest.mock import Mock, MagicMock


# For simplicity, we'll always configure tw mock to filter by tags when it's
# asked for.
def make_tags_filter(tasks):
    def _filter(filterstr):
        return [t for t in tasks if filterstr in t.tags]
    return _filter


def configure_tw(tw, tasks):
    tw.tasks.filter.side_effect = make_tags_filter(tasks)
    tw.tasks.all.return_value = tasks


def configure_execute_command(tw, stdout=None, stderr=None, retcode=0):
    if stdout is None:
        stdout = []
    if stderr is None:
        stderr = []

    tw.execute_command.return_value = (stdout, stderr, retcode)


def make_task_mock(id_, descr=None, tags=None, auto=False):
    if auto:
        if not descr:
            descr = 'Task {}'.format(id_)

    if tags is None:
        tags = []

    mock = MagicMock(
        id=id_, uuid=str(id_), description=descr,
        tags=tags)

    mock.__getitem__ = Mock()
    mock.__getitem__.side_effect = lambda name, self=mock: getattr(self, name)

    mock.__str__ = Mock()
    mock.__str__.return_value = descr if descr else ''

    mock.__repr__ = Mock()
    mock.__repr__.return_value = 'Task({})'.format(descr) if descr else 'Task()'

    return mock


def make_tasks(start, end=None, **kw):
    assert start > 0
    if end is None:
        end = start + 1
    return [make_task_mock(i, **kw) for i in range(start, end)]
