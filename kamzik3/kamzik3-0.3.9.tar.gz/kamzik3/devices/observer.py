class Observer(object):
    """
    Implement this class to implement Kamzik3 Observer.
    """

    def subject_update(self, key, value, subject):
        """
        Receive an subject update.
        :param key: mixed
        :param value: mixed
        :param subject: Subject
        :return: None
        """
        raise NotImplementedError(u"Not implemented")

    def attach_to_subject(self, subject):
        """
        Connect Observer to Subject.
        :param subject: Subject
        :return: None
        """
        subject.attach_observer(self)

    def detach_subject(self, subject):
        """
        Connect Observer to Subject.
        :param subject: Subject
        :return: None
        """
        subject.detach_observer(self)
