import platform
bit = platform.architecture()[0]

if(bit == '32bit'):
    from haohaninfo.MicroPlay.MicroPlayCommand import MicroPlayCommand
    from haohaninfo.MicroPlay.MicroPlayQuote import MicroPlayQuote
else:
    from haohaninfo.MicroPlay.MicroPlayCommand64 import MicroPlayCommand
    from haohaninfo.MicroPlay.MicroPlayQuote64 import MicroPlayQuote