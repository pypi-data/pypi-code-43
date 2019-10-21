""" Metrics Module """


from ..core.fix_variables import evaluate_integer


class Metrics(object):
    """ Metrics Class """

    def __init__(self):
        self._min_bw = 0
        self._max_delay = 0
        self._max_hops = 0
        self._avoid_shared = 0

    @property
    def min_bw(self):
        """ Getter """
        return self._min_bw

    @min_bw.setter
    def min_bw(self, min_bw):
        """ Setter """
        self._min_bw = evaluate_integer(min_bw, 'minimum_bandwidth')

    @property
    def max_delay(self):
        """ Getter """
        return self._max_delay

    @max_delay.setter
    def max_delay(self, max_delay):
        """ Setter """
        self._max_delay = evaluate_integer(max_delay, 'maximum_delay')

    @property
    def max_hops(self):
        """ Getter """
        return self._max_hops

    @max_hops.setter
    def max_hops(self, max_hops):
        """ Setter """
        self._max_hops = evaluate_integer(max_hops, 'maximum_hops')

    @property
    def avoid_shared(self):
        """ Getter """
        return self._avoid_shared

    @avoid_shared.setter
    def avoid_shared(self, avoid_shared):
        """ Setter """
        self._avoid_shared = evaluate_integer(avoid_shared, 'avoid_shared')

    def import_json(self, metrics):
        """ Import metrics from JSON """
        self.min_bw = metrics['min_bw']
        self.max_delay = metrics['max_delay']
        self.max_hops = metrics['max_hops']
        self.avoid_shared = metrics['avoid_shared']
