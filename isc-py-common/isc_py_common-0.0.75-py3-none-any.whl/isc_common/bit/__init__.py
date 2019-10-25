def IsBitOn(value, bit):
    res = (value & (1 << bit))
    if isinstance(res, int):
        return res
    return (value & (1 << bit))._value != 0


def TurnBitOn(value, bit):
    return value | (1 << bit)


def TurnBitOff(value, bit):
    return value & ~ (1 << bit)


def CopyBit(value, bit):
    if IsBitOn(value, bit):
        return TurnBitOn(value, bit)
    else:
        return TurnBitOff(value, bit)
