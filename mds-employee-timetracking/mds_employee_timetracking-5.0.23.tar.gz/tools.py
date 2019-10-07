# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from datetime import timedelta
from trytond.pool import Pool
from trytond.transaction import Transaction


def get_translation(msg_id, msg_type, msg_source):
    """ get translation in target-language
    """
    Translation = Pool().get('ir.translation')
    context = Transaction().context

    txt1 = msg_source
    tr_lst = Translation.search([
                ('name', '=', msg_id), 
                ('type', '=', msg_type),
                ('src', '=', msg_source),
                ('lang', '=', context.get('language', 'en')),
                ])
    if len(tr_lst) == 1:
        txt1 = tr_lst[0].value

    return txt1

# end get_translation

    
def fmttimedelta(deltaval, noplussign=False, sepbyh=False):
    """ format time delta
    """
    if not isinstance(deltaval, type(timedelta(seconds=1))):
        return ''
    else :
        minutes = deltaval.days * 24 * 60
        (m2, rem1)  = divmod(deltaval.seconds, 60)
        minutes += m2

        if noplussign == True:
            neg1 = ''
        else :
            neg1 = '+'
        if minutes < 0:
            neg1 = '-'
            minutes = -minutes
            if rem1 != 0:
                minutes -= 1

        (h1, m1) = divmod(minutes, 60)
        
        if sepbyh == True:
            fmt1 = '%s%02dh%02d'
        else :
            fmt1 = '%s%02d:%02d'
        return fmt1 % (neg1, h1, m1)
# end fmttimedelta


def round_timedelta(tdval, rndmode='up'):
    """ round timedelta-value up/down to minute
    """
    if isinstance(tdval, type(None)):
        return None
        
    sec1 = tdval.seconds + tdval.days*24*60*60
    neg1 = False
    if sec1 < 0:
        neg1 = True
        sec1 = -sec1

    (minutes, seconds) = divmod(sec1, 60)
    
    if not rndmode in ['up', 'down']:
        raise ValueError(u"wrong parameter in'rndmode': '%s' (up/down)" % rndmode)

    if minutes == 0:
        pass
    else :
        if neg1 == False:
            if rndmode == 'up':
                if seconds != 0:
                    minutes += 1
        else :
            if rndmode == 'down':
                if seconds != 0:
                    minutes += 1                

    if neg1 == True:
        minutes = -minutes
    return timedelta(seconds=minutes*60)

# end round_timedelta


def format_float(numbr, groups=False, stripzeros=False, numdec=2):
    """ converts Numeric/Float/integer-number to '0,00'
    """
    fmt1 = '%%.%df' % numdec
    fmt2 = '{:,.%df}' % numdec

    t1 = (fmt1 % 0.0).replace('.', ',')

    if not isinstance(numbr, type(None)):
        if groups == False:
            t1 = (fmt1 % numbr).replace('.', ',')
        else :
            t1 =  fmt2.format(numbr).replace('.',';').replace(',','.').replace(';',',')
    if stripzeros == True:
        # cut trailing zeros and decimal delimiter
        if t1.endswith('0'):
            t1 = t1[:-1]
        if t1.endswith('0'):
            t1 = t1[:-1]
        if t1.endswith(','):
            t1 = t1[:-1]
    return t1
# ende format_float
