from contextlib import contextmanager


class Trigger(object):
    def __init__(self, event, **kwargs):
        """
        An Instance of Trigger can be given an input that is evaluated on the basis
        of the event function. If the event function has once returned True, the
        triger is "ON" from now on plus <delay>

        Args:
            event (callable(str) -> bool): trigger function that is a boolean
                function of a string
            **kwargs:
                delay (int):
                    start at line -> 0
                    start after line -> 1
                    ...
                skip (int): do not trigger at the first <skip> trigger events
        """
        if isinstance(event, Trigger):
            # copy constructor
            delay = kwargs.pop('delay', event._delay)
            skip = kwargs.pop('skip', event._skip)
            event = event._triggerFunction
        else:
            delay = kwargs.pop('delay', 0)
            skip = kwargs.pop('skip', 0)
        self._triggerFunction = event
        self._delay = delay
        self._skip = skip
        self.reset()

    def reset(self):
        self._active_in = None
        self._occurence = 0

    def copy(self):
        """
        Examples:
            >>> from transcoding import LooseTrigger
            >>> t = LooseTrigger(lambda x: False)
            >>> isinstance(t.copy(), LooseTrigger)
            True

        """
        return self.__class__(self)
        
    def __call__(self, line):
        """"
        Evaluate the trigger
        """
        if line is None:
            # shortcut trigger if None is given
            trigger = True
            self._active_in = 1  # set it 1 so with -1 on bottom = 0
        else:
            trigger = self._triggerFunction(line)

        # progress the countDown
        if self._active_in is None:
            # trigger has not yet triggered
            if trigger:
                # trigger found
                self._occurence += 1
                if self._occurence > self._skip:
                    self._active_in = self._delay
        elif self._active_in is not None:
            # trigger will activate ...
            self._active_in -= 1
        return trigger

    @property
    def active_in(self):
        """
        (int|None):
            None: no trigger found yet
            int: trigger found and active in <active_in> steps.
                -> active_in == 0 means, the trigger just activated.
        """
        return self._active_in

    def found(self):
        return self.active_in is not None

    def active(self):
        return self.found() and not self.active_in > 0

    def pending(self):
        """
        = not found & not active
        """
        return not (self.found() or self.active()) 

    def activate(self):
        self._active_in = 0


class LooseTrigger(Trigger):
    """
    This Trigger should be used, if the event does not strongly depend on the
    input, i.e. triggers on multiple inputs.
    E.g. event = lambda x: True
    or event = lambda x: bool(x)
    It is only existing to be able o check, wheter a trigger will always trigger
    or not.
    """
    pass


@contextmanager
def time_shift(shift, *triggerObjects):
    for to in triggerObjects:
        to._delay += shift
    yield
    for to in triggerObjects:
        to._delay -= shift


if __name__ == '__main__':
    import doctest
    doctest.testmod()
