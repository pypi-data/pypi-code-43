
def parse_rut(rut):
    rut = rut.lstrip('0')
    return "{0}-{1}".format(rut[:len(rut)-1], rut[len(rut)-1])

