from abc import ABCMeta, abstractmethod

class Model:
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):

        args = self._init_preprocess(kwargs)

        if type(args) is not dict:
            raise Exception('_init_preprocess() must return a dict')

        for key, value in args.items():
            if key in self._accepted_params():
                setattr(self, key, value)

    def _init_preprocess(self, args):
        """
        sometimes additional work needs to be done when init an model such
        as instantiating nested models. You should override this method

        should return args (modify if needed)
        """
        return args

    @abstractmethod
    def _accepted_params(self):
        """
        Abstract method. This should return a list of all parameters which
        this model should accept
        """
        pass


    @classmethod
    def from_list(cls, items):
        """
        :param items:
        :type items: list
        :return: list
        """
        return [cls(**item) for item in items]
