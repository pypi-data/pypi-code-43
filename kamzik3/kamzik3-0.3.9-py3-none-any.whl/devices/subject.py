from kamzik3.devices.observer import Observer


class Subject(object):
    """
    Implements Subject which server Observer updates and notifications.
    """

    _observers = None

    def __init__(self):
        if not self._observers:
            self._observers = []

    def notify(self, key, value):
        """
        Notify all observers with an subject_update
        :param key: mixed
        :param value: mixed
        :return: None
        """
        # with self.notify_lock:
        for observer in self._observers[:]:
            observer.subject_update(key, value, self)

    def attach_observer(self, observer):
        """
        Attach new observer.
        :param observer: Observer
        :return: None
        """
        if observer not in self._observers:
            if isinstance(observer, Observer):
                self._observers.append(observer)
            else:
                raise AttributeError(u"observer has to implement kamzik3.device.observer.Observer interface")

        self.handle_observer_attached(observer)

    def detach_observer(self, observer):
        """
        Detach Observer from list of observers
        :param observer: Observer
        :return: None
        """
        if observer in self._observers:
            self._observers.remove(observer)
            self.handle_observer_detached(observer)

    def handle_observer_attached(self, observer):
        """
        Hook to be fired after attached Observer
        :param observer: Observer
        :return: None
        """
        raise NotImplementedError("Has to be implemented")

    def handle_observer_detached(self, observer):
        """
        Hook to be fired after detached Observer
        :param observer: Observer
        :return: None
        """
        raise NotImplementedError("Has to be implemented")
