class Range:
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

    def __contains__(self, v):
        return self.begin <= v < self.end

    def __str__(self):
        return 'extrange.Range({}, {})'.format(self.begin, self.end)

    def __repr__(self):
        return 'extrange.Range({}, {})'.format(
            repr(self.begin),
            repr(self.end),
        )
