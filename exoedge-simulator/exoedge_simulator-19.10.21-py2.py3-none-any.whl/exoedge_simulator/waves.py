
""" waves """
import logging
import math
import time

LOG = logging.getLogger(__name__)

def _apply_asdr(value, # pylint: disable=R0913
                attack=3,       # time in seconds
                decay=3,        # time in seconds
                sustaint=3,     # time in seconds
                sustainl=0.7,   # level to sustain at (0.0-1.0)
                release=3,      # time in seconds
                gap=3           # time in seconds
               ):
    def _mapper(x, in_min, in_max, out_min, out_max): # pylint: disable=C0103
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    stage = time.time() % (attack + decay + sustaint + release + gap)
    gain = 1
    if stage <= attack:
        # need to map range 0-1 over full attack time
        gain = _mapper(stage, 0, attack, 0, 1)
    elif stage <= (attack + decay):
        # need to map range 1-sustainl over full decay time
        gain = _mapper(stage, attack, attack+decay, 1, sustainl)
    elif stage <= (attack + decay + sustaint):
        gain = sustainl
    elif stage <= (attack + decay + sustaint + release):
        # need to map range sustainl-0 over full release time
        gain = _mapper(
            stage,
            attack + decay + sustaint,
            attack + decay + sustaint + release,
            sustainl,
            0
        )
    elif stage <= (attack + decay + sustaint + release + gap):
        gain = 0

    return value * gain

def _wave_sine(r):
    return math.sin(2 * math.pi * r)

def _wave_cosin(r):
    return math.cos(2 * math.pi * r)

def _wave_square(r):
    if r < 0.5:
        return 1
    else:
        return 0

def _wave_triangle(ratio):
    if ratio == 0.5:
        return 1
    elif ratio < 0.5:
        return ratio * 2
    else:
        return ratio * 2 - 1

def _wave_saw_asc(ratio):
    return ratio

def _wave_saw_desc(ratio):
    return 1 - ratio

def _amp_lineargain(value, gain=1.0, offset=0.0):
    return (value * gain) + offset

def do_wave(shape='sin', period=60, amplifier=None, envelope=None, precision=2):
    """ Generate a wave from the current time.

    Parameters:
        shape:          The shape of the wave.
                        Input type:
                            * str
                        Inputs:
                            * 'sin' (default)
                            * 'cos'
                            * 'square'
                            * 'triangle'
                            * 'saw_asc'
                            * 'saw_desc'

        period:         The period, in seconds, of the wave.
                        Input type:
                            * int
                        Inputs:
                            * any (default:60)

        amplifier:      Amplifier to apply to the wave.
                        Default: None
                        Input type:
                            * dict
                        Inputs:
                            * 'type':       'lineargain'
                            * 'gain':       1.0  (default)      # any float
                            * 'offset':     0.0  (default)      # any float

        envelope:       ASDR envelope to apply to the wave.
                        Input type:
                            * dict
                        Inputs:
                            * 'attack':     3,   (default)      # time in seconds
                            * 'decay':      3,   (default)      # time in seconds
                            * 'sustaint':   3,   (default)      # time in seconds
                            * 'sustainl':   0.7, (default)      # level to sustain at (0.0-1.0)
                            * 'release':    3,   (default)      # time in seconds
                            * 'gap':        3    (default)      # time in seconds
        precision:      Number of decimal points to return
                        Input type:
                            * int
                        Inputs:
                            * any (default:2)
    """
    LOG.info(
        "shape: {} period: {} amplifier: {} envelope: {} precision: {}"
        .format(shape, period, amplifier, envelope, precision))

    ratio = (time.time() % period) / period

    if shape == 'sin':
        waved = _wave_sine(ratio)
    elif shape == 'cos':
        waved = _wave_cosin(ratio)
    elif shape == 'square':
        waved = _wave_square(ratio)
    elif shape == 'triangle':
        waved = _wave_triangle(ratio)
    elif shape == 'saw_asc':
        waved = _wave_saw_asc(ratio)
    elif shape == 'saw_desc':
        waved = _wave_saw_desc(ratio)
    else:
        waved = 1

    # Is there more than one kind of these?
    amped = waved
    if amplifier != None:
        if amplifier['type'] == 'lineargain':
            params = amplifier.copy()
            params.pop('type')
            params['value'] = waved
            amped = _amp_lineargain(**params)

    if envelope != None:
        params = envelope.copy()
        params['value'] = amped
        envp = _apply_asdr(**params)
    else:
        envp = amped

    return round(envp, precision)
