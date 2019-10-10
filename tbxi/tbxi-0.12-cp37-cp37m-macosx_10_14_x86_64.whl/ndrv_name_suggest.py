import struct


from .pef import PEF, pidata


def parse_version(num):
    maj, minbug, stage, unreleased = num.to_bytes(4, byteorder='big')

    maj = '%x' % maj
    minor, bugfix = '%02x' % minbug

    if stage == 0x80:
        stage = 'f'
    elif stage == 0x60:
        stage = 'b'
    elif stage == 0x40:
        stage = 'a'
    elif stage == 0x20:
        stage = 'd'
    else:
        stage = '?'

    unreleased = '%0x' % unreleased

    vers = maj + '.' + minor + '.' + bugfix

    if (stage, unreleased) != ('f', '0'):
        vers += stage + unreleased

    return vers


def suggest_name(pef):
    if not pef.startswith(b'Joy!peff'): return

    pef = PEF(pef)

    for sectype, section in zip(pef.sectypes, pef.sections):
        if sectype == 2: section = pidata(section)

        if section and sectype in (1, 2):
            hdr_ofs = section.find(b'mtej')
            if hdr_ofs != -1:
                sig, strvers, devnam, drvvers = struct.unpack_from('>4s L 32p L', section, hdr_ofs)                

                print(sig, strvers, devnam, parse_version(drvvers))
