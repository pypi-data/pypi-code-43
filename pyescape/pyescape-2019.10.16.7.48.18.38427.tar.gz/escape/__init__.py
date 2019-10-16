class Escape:
    def __init__(self, avoid: str):
        self.avoid = avoid

    def __call__(self, string):
        i = 0
        s = []
        add = s.append
        size = len(string)
        avoid = self.avoid
        while i < size:

            # ignore back slashes and the char after them
            if string[i] == '\\':
                while i < size:
                    add(string[i])
                    i += 1

                    if string[i] != '\\':
                        add(string[i])
                        i += 1
                        break

            # avoid
            elif string[i] in avoid:
                add('\\')
                add(string[i])
                i += 1

            else:
                add(string[i])
                i += 1

        return "".join(s)
