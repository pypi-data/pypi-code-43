import setuptools

setuptools.setup(
        name = 'pym2149',
        version = '4',
        description = 'YM2149 emulator supporting YM files, OSC, MIDI to JACK, PortAudio, WAV',
        install_requires = ['mock', 'pyaudio', 'pyrbo', 'diapyr', 'aridity', 'outjack', 'mynblep', 'lagoon', 'splut', 'timelyOSC', 'pyven'],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = ['ym2jack', 'samples', 'ym2txt', 'midi2jack', 'bpmtool', 'dosound2jack', 'lc2wav', 'dsd2wav', 'lc2txt', 'lc2jack', 'dosound2wav', 'ym2wav', 'ym2portaudio', 'midi2wav'],
        scripts = ['ym2jack.py', 'samples.py', 'ym2txt.py', 'midi2jack.py', 'bpmtool.py', 'dosound2jack.py', 'lc2wav.py', 'dsd2wav.py', 'lc2txt.py', 'lc2jack.py', 'dosound2wav.py', 'ym2wav.py', 'ym2portaudio.py', 'midi2wav.py'])
