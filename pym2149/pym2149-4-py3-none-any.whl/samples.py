#!/usr/bin/env pyven

# Copyright 2014, 2018, 2019 Andrzej Cichocki

# This file is part of pym2149.
#
# pym2149 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pym2149 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pym2149.  If not, see <http://www.gnu.org/licenses/>.

from pym2149.initlogging import logging
from pym2149.pitch import Freq
from pym2149.config import ConfigName
from pym2149.timer import SimpleTimer
from pym2149 import out
from pym2149.boot import boot
from pym2149.iface import Stream, Config, Timer
from pym2149.program import Note
from pym2149.mediation import SimpleMediation
from pym2149.channels import Channels
from pym2149.dac import PWMEffect, SinusEffect
from pym2149.timerimpl import ChipTimer
from pym2149.ym2149 import LogicalRegisters
from diapyr import types
from diapyr.start import Started
import os, time

log = logging.getLogger(__name__)

class BaseTone(Note):

    def noteon(self):
        self.toneflag = True
        self.fixedlevel = 15
        self.toneperiod = self.period

class Tone(BaseTone):

    def __init__(self, *args):
        super().__init__(*args)
        self.period = Freq(self.freq).toneperiod(self.nomclock)

class Noise(Note):

    def noteon(self):
        self.noiseflag = True
        self.fixedlevel = 15
        self.chip.noiseperiod = Freq(self.freq).noiseperiod(self.nomclock)

class Both(Note):

    def noteon(self):
        self.toneflag = True
        self.noiseflag = True
        self.fixedlevel = 15
        self.toneperiod = Freq(self.tfreq).toneperiod(self.nomclock)
        self.chip.noiseperiod = Freq(self.nfreq).noiseperiod(self.nomclock)

class Env(Note):

    def noteon(self):
        self.levelmode = 1
        self.chip.envperiod = Freq(self.freq).envperiod(self.nomclock, self.shape)
        self.chip.envshape = self.shape

class All(Note):

    tfreq, nfreq, efreq, shape = 1000, 5000, 1, 0x0e

    def noteon(self):
        self.toneflag = True
        self.noiseflag = True
        self.levelmode = 1
        self.toneperiod = Freq(self.tfreq).toneperiod(self.nomclock)
        self.chip.noiseperiod = Freq(self.nfreq).noiseperiod(self.nomclock)
        self.chip.envperiod = Freq(self.efreq).envperiod(self.nomclock, self.shape)
        self.chip.envshape = self.shape

class PWM(Note):

    def noteon(self):
        self.toneflag = True
        self.timer.effect.value = PWMEffect(self.chip.fixedlevels[self.chipchan])
        self.fixedlevel = 15
        self.toneperiod = Freq(self.tfreq).toneperiod(self.nomclock)
        self.timer.freq.value = self.rtfreq

# TODO LATER: Find out why the result appears shifted a few samples to the right.
class Sinus(Note):

    def noteon(self):
        self.timer.effect.value = SinusEffect(self.chip.fixedlevels[self.chipchan])
        self.timer.freq.value = self.freq * 4 # FIXME: It should know wavelength from effect.

    def noteonframe(self, frame):
        self.fixedlevel = 15 - frame // 5

class Frames(list): pass

class ProgramIds(dict): pass

class Player:

    @types(Config, Timer, Stream, Channels, Frames, ProgramIds, LogicalRegisters)
    def __init__(self, config, timer, stream, channels, frames, programids, chip):
        self.updaterate = config.updaterate
        self.neutralvel = config.neutralvelocity
        self.chipchannels = config.chipchannels
        self.midichan = config.midichannelbase
        self.timer = timer
        self.stream = stream
        self.channels = channels
        self.frames = frames
        self.programids = programids
        self.chip = chip

    def __call__(self):
        # Play silence on all chip channels:
        for chan in range(self.chipchannels):
            self.chip.flagsoff(chan)
            self.chip.fixedlevels[chan].value = 13 # Neutral DC.
        for program in self.frames:
            if program:
                self.channels.programchange(self.midichan, self.programids[program])
                # This noteon should override any previous noteon for the same note:
                self.channels.noteon(self.midichan, 60, self.neutralvel)
            self.channels.updateall()
            for b in self.timer.blocksforperiod(self.updaterate):
                self.stream.call(b)
            self.channels.closeframe()
        self.stream.flush()

class Target:

    try:
        from lagoon import sox
    except ImportError:
        log.warning("sox is not available, spectrograms won't be created.")

    def __init__(self, configname):
        self.targetpath = os.path.join(os.path.dirname(__file__), 'target')
        if not os.path.exists(self.targetpath):
            os.mkdir(self.targetpath)
        self.configname = configname

    def dump(self, beatsperbar, beats, name):
        path = os.path.join(self.targetpath, name)
        log.info(path)
        config, di = boot(self.configname)
        try:
            config.midichanneltoprogram = {} # We'll use programchange as necessary.
            config.outpath = path + '.wav'
            config.freqclamp = False # I want to see the very low periods.
            out.configure(di)
            di.add(SimpleMediation) # TODO LATER: Could be even simpler.
            di.add(Channels)
            channels = di(Channels)
            channels.midiprograms = {}
            di.add(ChipTimer)
            di.add(Player)
            programids = ProgramIds()
            frames = Frames()
            def register(program):
                programid = config.midiprogrambase + len(programids)
                channels.midiprograms[programid] = program
                programids[program] = programid
            lftimer = SimpleTimer(config.updaterate)
            for program in beats:
                if program and program not in programids:
                    register(program)
                frames.append(program)
                b, = lftimer.blocksforperiod(beatsperbar)
                for _ in range(b.framecount - 1):
                    frames.append(0)
            di.add(programids)
            di.add(frames)
            start = time.time()
            di.all(Started)
            di(Player)()
        finally:
            di.discardall()
        log.info("Render of %.3f seconds took %.3f seconds.", len(frames) / config.updaterate, time.time() - start)
        if hasattr(self, 'sox'):
            self.sox(path + '.wav', '-n', 'spectrogram', '-o', path + '.png')

def main():
    mainimpl(ConfigName())

def mainimpl(configname):
    class T250(Tone): freq = 250
    class T1k(Tone): freq = 1000
    class T1k5(Tone): freq = 1500
    class N5k(Noise): freq = 5000
    class N125k(Noise): freq = 125000
    class T1kN5k(Both): tfreq, nfreq = 1000, 5000
    class T1N5k(Both):
        nfreq = 5000
        def __init__(self, *args):
            super().__init__(*args)
            self.tfreq = self.nomclock // 16
    class Saw600(Env): freq, shape = 600, 0x08
    class Sin1k(Sinus): freq = 1000
    class Tri650(Env): freq, shape = 650, 0x0a
    class T2k(Tone): freq = 2000
    class T3k(Tone): freq = 3000
    class T4k(Tone): freq = 4000
    class PWM250(PWM): tfreq, rtfreq = 250, 250
    class PWM100(PWM): tfreq, rtfreq = 100, 101 # Necessarily detune.
    tones = []
    for p in range(1, 9):
        class t(BaseTone): period = p
        tones.append(t)
    target = Target(configname)
    target.dump(2, [T250, 0, 0], 'tone250')
    target.dump(2, [T1k, 0, 0], 'tone1k')
    target.dump(2, [T1k5, 0, 0], 'tone1k5')
    target.dump(2, [N5k, 0, 0], 'noise5k')
    target.dump(2, [N125k, 0, 0], 'noise125k')
    target.dump(2, [T1kN5k, 0, 0], 'tone1k+noise5k')
    target.dump(2, [T1N5k, 0, 0], 'noise5k+tone1')
    target.dump(2, [Saw600, 0, 0], 'saw600')
    target.dump(2, [Sin1k, 0, 0, 0], 'sin1k')
    target.dump(2, [Tri650, 0, 0], 'tri650')
    target.dump(2, [All, 0, 0], 'tone1k+noise5k+tri1')
    target.dump(4, [T1k, T2k, T3k, T4k], 'tone1k,2k,3k,4k')
    target.dump(2, [PWM250, 0, 0], 'pwm250')
    target.dump(2, [PWM100, 0, 0], 'pwm100')
    target.dump(8, tones, 'tone1-8')

if '__main__' == __name__:
    main()
