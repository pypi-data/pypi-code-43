def write_line(line, filename, mode):
    with open(filename, mode) as f:
        f.write(line)


def read_line(filename, lineno=0):
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            if i >= lineno:
                return line
