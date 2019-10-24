__version__ = '0.0.1'

def convert_bban_to_iban(bban: str) -> str:
    """
    Convert an account number from BBAN to IBAN format.
    :param bban: Account number in BBAN format
    :return: Account number in IBAN format
    """
    len_orig = len(bban)
    bban_repl = bban.replace('-', '')
    len_repl = len(bban_repl)
    zeros = '0000000'

    if len_orig == 16 and bban.find('-') == -1:
        accno_machinelang = bban[0:4] + bban[5:8] + bban[9:]
    elif bban_repl[0] in ('4', '5'):
        if 8 <= len_repl <= 13:
            accno_machinelang = bban_repl[0:7] + zeros[:(14 - len_repl)] + bban_repl[7:]
        else:
            accno_machinelang = bban_repl
    elif 7 <= len_repl <= 13:
        accno_machinelang = bban_repl[0:6] + zeros[:(14 - len_repl)] + bban_repl[6:]
    else:
        raise ValueError('BBAN is too short')

    checksum = 98 - int(accno_machinelang + '151800') % 97
    iban = 'FI' + (zeros + str(checksum))[-2:] + accno_machinelang
    return iban


def convert_iban_to_bban(iban: str) -> str:
    """
    Convert an account number from IBAN to BBAN manchine language format.
    :param iban: Account number in IBAN format
    :return: Account number in BBAN machine language format
    """
    len_iban = len(iban)
    country_iban = iban[:2]

    if len_iban == 18 and country_iban == 'FI':
        if iban[4] in ('4', '5'):
            bban = iban[4:10] + '0' + iban[10] + '0' + iban[11:]
        else:
            bban = iban[4:10] + '00' + iban[10:]
    else:
        raise ValueError('IBAN is not in Finnish format')

    return bban
