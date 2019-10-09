import platform
bit = platform.architecture()[0]

if(bit == '32bit'):
    from haohaninfo.GOrder.GOCommand import GOCommand
    from haohaninfo.GOrder.GOQuote import GOQuote
    from haohaninfo.GOrder.GOGetKBar import GetKBar as GetHistoryKBar
else:
    from haohaninfo.GOrder.GOCommand64 import GOCommand
    from haohaninfo.GOrder.GOQuote64 import GOQuote
    from haohaninfo.GOrder.GOGetKBar64 import GetKBar as GetHistoryKBar