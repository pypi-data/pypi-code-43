import numpy as np
from IPython.display import Audio
from IPython.display import display as d

def alert():
    """ makes sound on client using javascript (works with remote server) """      
    framerate = 44100
    duration=0.6
    freq=300
    t = np.linspace(0,duration,framerate*duration)
    data = np.sin(2*np.pi*freq*t)
    d(Audio(data,rate=framerate, autoplay=True))