# Copyright 2013-2016 Tom Eulenfeld, MIT license
"""
Tests for imaging module.
"""
import unittest
from obspy import read_events, read_inventory, read

from rf import iter_event_data, IterMultipleComponents


class UtilTestCase(unittest.TestCase):

    def test_iter_event_data(self):
        events = read_events()
        inventory = read_inventory().select(channel='HH?')

        def dummy_get_waveforms(starttime=None, **kwargs):
            stream = read()
            for tr in stream:
                tr.stats.starttime = starttime
            return stream
        streams = list(iter_event_data(events, inventory, dummy_get_waveforms))
        self.assertEqual(len(streams), 2)
        del events[0].origins[0].depth  # also test issue #7
        with self.assertWarnsRegex(UserWarning, 'No origin depth'):
            streams = list(iter_event_data(events, inventory,
                                           dummy_get_waveforms))
        self.assertEqual(len(streams), 0)

    def test_IterMultipleComponents(self):
        stream = read() + read()
        for tr in stream[3:]:
            tr.stats.station = 'XX'
        for sub in IterMultipleComponents(stream):
            self.assertEqual(len(sub), 3)
        stream = read()[:2] + read()[:2]
        for tr in stream[:2]:
            tr.stats.eventid = 'event 1'
        for tr in stream[2:]:
            tr.stats.eventid = 'event 2'
        for sub in IterMultipleComponents(stream, key='eventid',
                                          number_components=2):
            self.assertEqual(len(sub), 2)
        # test if the iterator is working as expected (and test issue 9)
        stream = read() + read()[1:] + read()[2:]
        for tr in stream[3:5]:
            tr.stats.station = 'XX'
        for tr in stream[5:]:
            tr.stats.station = 'YY'
        streams1 = list(IterMultipleComponents(stream))
        self.assertEqual(len(streams1), 3)
        streams2 = list(IterMultipleComponents(stream, number_components=1))
        self.assertEqual(len(streams2), 1)
        streams3 = list(IterMultipleComponents(stream,
                                               number_components=(1, 2)))
        self.assertEqual(len(streams3), 2)



def suite():
    return unittest.makeSuite(UtilTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
