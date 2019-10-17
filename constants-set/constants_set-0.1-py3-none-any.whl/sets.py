# TODO: extract this class to a dedicated self-hosted repository
class ConstantsSet(set):
    def to_choices(self):
        return tuple((name, name) for name in sorted(self))

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

    def __str__(self):
        return ", ".join(sorted(self))

    def to_array(self):
        return sorted(self)
