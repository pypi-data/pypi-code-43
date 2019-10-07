from pyaes.Field import sbox, GF, modulus
# sbox needed for key expansion


def expand_128(key):
    """
    Expands a given list of GF objects for the key schedule

    param key should be a list of size 16
    return value is a list of size 176


    :param key: [GF, GF, GF ... , GF]
    :return: [GF, GF, GF, ... , GF]
    """

    i = 1  # Rcon value

    while len(key) < 176:  # Goal of 176 bytes
        temp = key[-4:]  # Grab last 4 bytes of data
        if len(key) % 16 == 0:  # Every 16 bytes of generated data
            # Perform the key schedule core and increment the Rcon value by 1
            schedule_core(temp, i)
            i = i + 1
        for item in temp:
            # xor each value with the value that came 16 bytes before it
            key.append(item ^ key[-16])
    return key


def expand_192(key):
    """
    Expands a given list of GF objects for the key schedule

    param key should be a list of size 24
    return value is a list of size 204


    :param key: [GF, GF, GF ... , GF]
    :return: [GF, GF, GF, ... , GF]
    """
    i = 1  # Rcon value
    while len(key) < 208:  # Goal of 204 bytes
        temp = key[-4:]  # Grab last 4 bytes of data
        if len(key) % 24 == 0:
            # Perform the key schedule core and increment the Rcon value by 1
            schedule_core(temp, i)
            i = i + 1
        for item in temp:
            # xor each value with the value that came 24 bytes before it
            key.append(item ^ key[-24])

    return key


def expand_256(key):
    """
    Expands a given list of GF objects for the key schedule

    param key should be a list of size 32
    return value is a list of size 240


    :param key: [GF, GF, GF ... , GF]
    :return: [GF, GF, GF, ... , GF]
    """

    i = 1  # Rcon value
    while len(key) < 240:  # Goal of 240 bytes
        temp = key[-4:]  # Grab last 4 bytes of data

        if len(key) % 32 == 0:
            # Perform the key schedule core and increment the Rcon value by 1
            schedule_core(temp, i)
            i = i + 1

        # For AES-256 only
        if len(key) % 32 == 16:  # Occurs when len is either 16, 48, 112, 144, 176, or 208
            for index, item in enumerate(temp):
                # each value in the generated temp list goes through the
                # Rjindael S-Box
                temp[index] = sbox(item)

        for item in temp:
            # xor each value with the value that came 32 bytes before it
            key.append(item ^ key[-32])

    return key


def schedule_core(temp, i):
    """
    Circular shift input list once the the left
    Run each value of the list through the S-Box
    Apply Rcon to first element of list

    :param temp: [GF, GF, GF, ... , GF]
    :param i: int
    :return: [GF, GF, GF, ... , GF]
    """
    temp.append(temp.pop(0))  # Circular shift left
    for index, item in enumerate(temp):
        temp[index] = sbox(item)  # Sbox each element
    temp[0] = temp[0] ^ (GF(1 << (i - 1)) % modulus)
    return temp


def iter_key(key, size, *, reverse=False):
    """
    Creates generator that loops each round key repeatedly
    Quality of Life function



    :param key: [GF, GF, GF, ... , GF] (must have 16 elements)
    :param size: int (must be either 128, 192, or 256)
    :param reverse: bool (False for encrypt True for decrypt)
    :return: [[GF, GF, GF, ... , GF], [GF, GF, GF, ... , GF], ... , [GF, GF, GF, ... , GF]]
    """
    if size == 128:
        key = expand_128(key)
    elif size == 192:
        key = expand_192(key)
    elif size == 256:
        key = expand_256(key)
    else:
        raise ValueError
    keys = list()

    # Separate keys into each round key
    for i in range(0, len(key), 16):
        keys.append(key[i:i+16])

    if reverse:
        # If decrypting
        keys.reverse()

    while True:
        # Loop repeatedly
        for key in keys:
            # Through each round key individually
            yield key
