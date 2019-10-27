from sha3 import keccak_256

def string_to_hex(string):
  ret = ''
  for ch in sanitize_hex(string):
    ch = sanitize_hex(hex(ord(ch)))
    ret = ret + ch
  return ret

def sanitize_hex(word):
  if word.startswith('0x'):
    return word[2:]
  return word

def checksum_encode(addr):
  p = keccak_256(bytearray.fromhex(string_to_hex(addr[2:].lower()))).hexdigest()
  v = int(p,16)
  ret = '0x'

  for i, c in enumerate(addr[2:]):
    if c in '0123456789':
      ret = ret + c
    else:
      ret = ret + ( c.upper() if (v & (2**(255 - 4*i))) else c.lower() )

  return ret


def test(addrstr):
  assert(addrstr == checksum_encode(addrstr))

test('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
test('0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359')
test('0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB')
test('0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb')
