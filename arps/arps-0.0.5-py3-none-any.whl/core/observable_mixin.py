import random
import asyncio
import inspect
from functools import partial, wraps, update_wrapper


class ObservableMixin:
    '''This mixin class offers a way to subscribe to events and notify
    listeners

    There are two queue available for notification. One has higher
    priority than the other.

    It offers conditional notifications.

    The order of the notification is the same order that the listeners
    were added.

    '''

    def __init__(self):
        self._high_listeners = list()
        self._low_listeners = list()
        self.notified_tasks = list()

    def add_listener(self, listen, *, predicate=None):
        '''High priority queue is default
        '''

        self._add_listener(listen, queue=self._high_listeners, predicate=predicate)

    def add_listener_low_priority(self, listen, *, predicate=None):
        '''Low priority queue needs to be called explicitly
        '''
        self._add_listener(listen, queue=self._low_listeners, predicate=predicate)

    def _add_listener(self, listen, *, queue, predicate=None):
        '''Add a new listener to track when the resource is modified

        It supports async and non async listeners

        Args:
        - listen: function that will receive an event when the
          resource is modified
        - predicate:
        '''
        predicate = predicate or (lambda _: True)
        listener = partial(self.conditional_listener, listen, predicate)
        update_wrapper(listener, listen)
        queue.append(listener)

    def remove_listener(self, listener):
        result_low = [_listener for _listener in self._low_listeners if listener == _listener.args[0]]
        result_high = [_listener for _listener in self._high_listeners if listener == _listener.args[0]]
        if result_low:
            result, queue = result_low, self._low_listeners
        elif result_high:
            result, queue = result_high, self._high_listeners
        else:
            return

        if len(result) != 1:
            print('\n'.join(str(element) for element in result))
        assert len(result) == 1, 'Expected 1, got {}: {}'.format(len(result), result)

        queue.remove(result[0])

    async def notify(self, event):
        self.notified_tasks = [task for task in self.notified_tasks if not task.done()]
        for listener in self._high_listeners:
            self.notified_tasks.append(asyncio.create_task(listener(event)))
        for listener in self._low_listeners:
            self.notified_tasks.append(asyncio.create_task(listener(event)))

    async def wait_for_notified_tasks(self):
        await asyncio.wait_for(asyncio.gather(*self.notified_tasks), timeout=10)
        self.notified_tasks.clear()

    def clear(self):
        self._high_listeners.clear()
        self._low_listeners.clear()

    async def conditional_listener(self, action, action_condition, event):
        '''Execute an action, passing an event as parameter, if condition is
        met

        Args:
        - action: action to be executed (can be sync or async)
        - action_condition: predicate based on the event
        - event: event passed to action
        '''

        if not action_condition(event):
            return

        async_action = wrap_into_async(action)

        if len(inspect.signature(action).parameters):
            await async_action(event)
        else:
            await async_action()


def wrap_into_async(sync_or_async):
    '''Wrap the function just to run as async

    '''
    if asyncio.iscoroutinefunction(sync_or_async):
        return sync_or_async

    @wraps(sync_or_async)
    async def inner(*args, **kwargs):
        return sync_or_async(*args, **kwargs)

    return inner


class StochasticObservableMixin(ObservableMixin):
    '''This class offers a way to modify the notification behaviour of
ObservableMixin.

    The current version offers only the notification order using the
    random.random function
    '''

    async def notify(self, event):
        random.shuffle(self._high_listeners)
        random.shuffle(self._low_listeners)
        await super().notify(event)
