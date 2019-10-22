"""
.csv file transcoding
"""
import transcoding as tc


def get_transcoding(delimiter=',', text_delimiter='"'):
    b_list = tc.List('{entries}',
                     separator=delimiter)
    b_loop = tc.Loop('lines', [b_list],
                     stop_iter=tc.Trigger(lambda x: x is None))
    csv_transcoding = tc.Transcoding(b_loop)
    return csv_transcoding
