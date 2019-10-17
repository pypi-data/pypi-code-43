class Constants:
    wif_prefixes = None
    raw_prefixes = None
    prefixes = None
    net_to_hrp = None
    hrp_to_net = None
    key_prefixes = None
    public_key_version_strings = None
    private_key_version_strings = None


class BitcoinConstants(Constants):
    wif_prefixes = {'mainnet': 0x80, 'testnet': 0xef}

    raw_prefixes = {('mainnet', 'p2pkh'): bytearray(b'\x00'),
                    ('testnet', 'p2pkh'): bytearray(b'\x6f'),
                    ('mainnet', 'p2sh'): bytearray(b'\x05'),
                    ('testnet', 'p2sh'): bytearray(b'\xc4')}

    prefixes = {'1': ('p2pkh', 'mainnet'),
                'm': ('p2pkh', 'testnet'),
                'n': ('p2pkh', 'testnet'),
                '3': ('p2sh', 'mainnet'),
                '2': ('p2sh', 'testnet')}

    net_to_hrp = {'mainnet': 'bc',
                  'testnet': 'tb'}

    hrp_to_net = {'bc': 'mainnet',
                  'tb': 'testnet'}

    key_prefixes = {'x': 'mainnet', 't': 'testnet'}

    public_key_version_strings = {'mainnet': b'\x04\x88\xb2\x1e', 'testnet': b'\x04\x35\x87\xcf'}

    private_key_version_strings = {'mainnet': b'\x04\x88\xad\xe4', 'testnet': b'\x04\x35\x83\x94'}


class DashConstants(Constants):
    wif_prefixes = {'dash': 0xCC, 'dashtest': 0xEF}

    raw_prefixes = {('dash', 'p2pkh'): bytearray(b'\x4c'),
                    ('dashtest', 'p2pkh'): bytearray(b'\x8c'),
                    ('dashtest', 'p2sh'): bytearray(b'\x13'),
                    ('dash', 'p2sh'): bytearray(b'\x10')}

    prefixes = {'X': ('p2pkh', 'dash'),
                'y': ('p2pkh', 'dashtest'),
                '8': ('p2pkh', 'dashtest'),
                '7': ('p2sh', 'dash'),
                '9': ('p2sh', 'dashtest')}

    net_to_hrp = {'dash': 'bc',
                  'dashtest': 'tb'}

    hrp_to_net = {'bc': 'dash',
                  'tb': 'dashtest'}

    key_prefixes = {'x': 'dash', 't': 'dashtest'}

    public_key_version_strings = {'dash': b'\x04\x88\xb2\x1e', 'dashtest': b'\x04\x35\x87\xcf'}

    private_key_version_strings = {'dash': b'\x04\x88\xad\xe4', 'dashtest': b'\x04\x35\x83\x94'}


class LitecoinConstants(Constants):
    wif_prefixes = {'litecoin': 0xB0, 'litecointest': 0xEF}

    raw_prefixes = {('litecoin', 'p2pkh'): bytearray(b'\x30'),
                    ('litecointest', 'p2pkh'): bytearray(b'\x6f'),
                    ('litecoin', 'p2sh'): bytearray(b'\x32'),
                    ('litecointest', 'p2sh'): bytearray(b'\x3a')}

    prefixes = {'L': ('p2pkh', 'litecoin'),
                'M': ('p2sh', 'litecoin'),
                'm': ('p2pkh', 'litecointest'),
                'n': ('p2pkh', 'litecointest'),
                'Q': ('p2sh', 'litecointest'),
                }

    net_to_hrp = {'litecoin': 'bc',
                  'litecointest': 'tb'}

    hrp_to_net = {'bc': 'litecoin',
                  'tb': 'litecointest'}

    key_prefixes = {'x': 'litecoin', 't': 'litecointest'}

    public_key_version_strings = {'litecoin': b'\x04\x88\xb2\x1e', 'litecointest': b'\x04\x35\x87\xcf'}

    private_key_version_strings = {'litecoin': b'\x04\x88\xad\xe4', 'litecointest': b'\x04\x35\x83\x94'}


class KomodoConstants(Constants):
    wif_prefixes = {'komodo': 0xBC, 'komodotest': 0x80}

    raw_prefixes = {('komodo', 'p2pkh'): bytearray(b'\x3C'),
                    ('komodo', 'p2sh'): bytearray(b'\x55'),
                    ('komodotest', 'p2pkh'): bytearray(b'\x00'),
                    ('komodotest', 'p2sh'): bytearray(b'\x05')
                    }

    prefixes = {'R': ('p2pkh', 'komodo'),
                'b': ('p2sh', 'komodo'),
                '1': ('p2pkh', 'komodotest'),
                '3': ('p2sh', 'komodotest')
                }

    net_to_hrp = {'komodo': 'bc',
                  'komodotest': 'tb'}

    hrp_to_net = {'bc': 'komodo',
                  'tb': 'komodotest'}

    key_prefixes = {'x': 'komodo', 't': 'komodotest'}

    public_key_version_strings = {'komodo': b'\x04\x88\xb2\x1e', 'komodotest': b'\x04\x35\x87\xcf'}

    private_key_version_strings = {'komodo': b'\x04\x88\xad\xe4', 'komodotest': b'\x04\x35\x83\x94'}


class ZcashConstants(Constants):
    """
        Zcash uses bech32 only for sapling, which is an network upgrade scheduled for october 2018
        for that reason the net_to_hrp and hrp_to_net constants are filled with sapling values that
        the rest of the code probably can't really handle
    """

    wif_prefixes = {'zcash': 0x80, 'zcashtest': 0x80}

    raw_prefixes = {
        ('zcash', 'p2pkh'): bytearray(b'\x1c\xb8'),
        ('zcash', 'p2sh'): bytearray(b'\x1c\xbd'),
        ('zcashtest', 'p2pkh'): bytearray(b'\x1d\x25'),
        ('zcashtest', 'p2sh'): bytearray(b'\x1c\xba')
    }

    prefixes = {
        't1': ('p2pkh', 'zcash'),
        't3': ('p2sh', 'zcash'),
        'tm': ('p2pkh', 'zcashtest'),
        't2': ('p2sh', 'zcashtest')
    }

    net_to_hrp = {'zcash': 'zs',
                  'zcashtest': 'ztestsapling'}

    hrp_to_net = {'zs': 'zcash',
                  'ztestsapling': 'zcashtest'}

    key_prefixes = {'x': 'zcash', 't': 'zcashtest'}

    public_key_version_strings = {'zcash': b'\x04\x88\xb2\x1e', 'zcashtest': b'\x04\x35\x87\xcf'}

    private_key_version_strings = {'zcash': b'\x04\x88\xad\xe4', 'zcashtest': b'\x04\x35\x83\x94'}


NETWORKS = {'mainnet': BitcoinConstants(),
            'testnet': BitcoinConstants(),
            'regtest': BitcoinConstants(),
            'litecoin': LitecoinConstants(),
            'litecointest': LitecoinConstants(),
            'dash': DashConstants(),
            'dashtest': DashConstants(),
            'komodo': KomodoConstants(),
            'komodotest': KomodoConstants(),
            'zcash': ZcashConstants(),
            'zcashtest': ZcashConstants()}
