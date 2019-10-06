from jppy.daqtimeslicereader import PyJDAQTimesliceReader
import numpy as np

filename = 'test.root'

r = PyJDAQTimesliceReader(filename, "JDAQTimesliceL1")

r.retrieve_timeslice(0)
print(r.n_frames)
print(r.number_of_hits)

channel_ids = np.zeros(r.number_of_hits, dtype='i')
dom_ids = np.zeros(r.number_of_hits, dtype='i')
times = np.zeros(r.number_of_hits, dtype='i')
tots = np.zeros(r.number_of_hits, dtype='i')

r.get_hits(channel_ids, dom_ids, times, tots)
print(tots)

print(np.unique(dom_ids))
