"""Create mp3 files of spoken numbers"""

# Built-in imports
import math
import sys
import os
import random
import io
import pkgutil
from pathlib import Path

# PyPI imports
from pydub import AudioSegment


def _spoken(digits, digits_audio, speed, init_silence, countdown, **kw):
    """Create mp3 file content

    digits_audio[0] = voice says 0
    digits_audio[1] = voice says 1
    digits_audio[2] = voice says 2
    digits_audio[3] = voice says 3
    digits_audio[4] = voice says 4
    digits_audio[5] = voice says 5
    digits_audio[6] = voice says 6
    digits_audio[7] = voice says 7
    digits_audio[8] = voice says 8
    digits_audio[9] = voice says 9
    digits_audio[10] = voice says a
    digits_audio[11] = voice says b
    digits_audio[12] = voice says c
    """

    # Check input arguments
    try:
        speed = float(speed)
    except TypeError as error:
        raise TypeError('Argument `speed` must be float') from error
    try:
        init_silence = float(init_silence)
    except TypeError as error:
        raise TypeError('Argument `init_silence` must be float') from error

    max_duration = max(audio.duration_seconds for audio in digits_audio)
    if speed < max_duration:
        raise ValueError(
            f'Argument `speed` must be greater that {max_duration} sec')
    if init_silence < 0:
        raise ValueError('Argument `init_silence` must be non-negative')

    # Create audio playlist representing the count down sequence
    if countdown:
        digits_audio.append(AudioSegment.silent(duration=500))
        count_down_indices = [3, 2, 1, 10, 11, 12, 13]
        # Voice will say: 3 ... 2 ... 1 ... a ... b ... c ... ...
    else:
        count_down_indices = []

    length = init_silence
    output = AudioSegment.silent(duration=length*1_000)
    for digit in count_down_indices + digits:
        length += speed
        output += digits_audio[digit]
        padding_duration = 1_000*(length - output.duration_seconds)
        if padding_duration < 0:
            raise Exception('Padding duration was negative!')
        padding = AudioSegment.silent(duration=padding_duration)
        output += padding

    file = io.BytesIO()
    output.export(file, **kw)
    return file


def spoken(numbers, speed=1, init_silence=3, countdown=True,
           source='default', output_file='spoken.mp3', **kw):
    """Generate spoken numbers audio file.

    :param numbers: List of digits [0-9] to be spoken.
    :param speed: The pace at which numbers will be spoken in seconds.
        Default to one digit per second.
    :param init_silence: Number of seconds of silence before any audio
        will be spoken. Defaults to three seconds.
    :param countdown: If `True`, a countdown sequence will be spoken
        at start. Defaults to "3 ... 2 ... 1 ... a ... b ... c ... ...".
        There will be a short silence of one sec between the end of the
        count down and the start of memorization numbers.
    :param source: Audio files source. The string 'default' will use
        the default audio files included in the Python package. For
        custom audio files, you can specify the path to a directory
        as source. The directory must contain the required audio wav
        files: 0.wav ... 9.wav and a.wav, b.wav and c.wav.
    :param output_file: Name of output file. Defaults to `spoken.mp3`.
    """

    # Load *.wav files from `source`.
    source_is_dir = os.path.isdir(source)
    digits_audio = list()
    for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'a', 'b', 'c']:
        filename = f'{source}{os.sep}{i}.wav'
        if source_is_dir:
            # External directory
            file = open(filename, 'rb')
        else:
            # Package built-in
            data = pkgutil.get_data(__package__, filename)
            file = io.BytesIO(data)
        digits_audio.append(AudioSegment.from_wav(file))
        file.close()

    # Write the binary buffer to file
    output = _spoken(numbers, digits_audio, speed, init_silence, countdown,
                     **kw)
    with open(output_file, 'wb') as f:
        f.write(output.getbuffer())
