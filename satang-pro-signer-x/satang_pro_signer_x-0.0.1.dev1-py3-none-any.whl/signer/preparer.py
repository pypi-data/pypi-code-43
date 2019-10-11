class Preparer:
    def __init__(self, obj, prefix: str = ""):
        self.obj = obj
        self.prefix = prefix

    def append_prefix(self, val) -> str:
        prefix = val

        if not isinstance(prefix, str):
            prefix = str(prefix)

        if len(self.prefix) > 0:
            prefix = f'{self.prefix}[{prefix}]'
        return prefix

    def parse(self) -> str:
        pass

class DictPreparer(Preparer):
    def parse(self) -> str:

        parts = []
        for k, v in sorted(self.obj.items()):
            parts.append(
                PreparerFactory().get_preparer(v, self.append_prefix(k)).parse()
            )

        return '&'.join(parts)

class ListPreparer(Preparer):
    def parse(self) -> str:

        parts = []
        for i, v in enumerate(self.obj):
            parts.append(
                PreparerFactory().get_preparer(v, self.append_prefix(i)).parse()
            )

        return '&'.join(parts)

class NonePreparer(Preparer):
    def parse(self) -> str:
        return ""

# class that require prefix
class ValuePreparer(Preparer):
    def __init__(self, obj, prefix: str = ""):
        super().__init__(obj, prefix)

        if len(prefix) == 0:
            raise ValueError(f'Single {type(obj)} could not be accepted')

class StrPreparer(ValuePreparer):
    def parse(self) -> str:

        return self.prefix + "=" + self.obj

class IntPreparer(ValuePreparer):
    def parse(self) -> str:

        return self.prefix + "=" + str(self.obj)

class FloatPreparer(ValuePreparer):
    def parse(self) -> str:

        return f'{self.prefix}={str(self.obj)}'

class PreparerFactory:
    def get_preparer(self, obj, prefix: str = "") -> Preparer:
        if isinstance(obj, dict):
            return DictPreparer(obj, prefix)
        elif isinstance(obj, list):
            return ListPreparer(obj, prefix)
        elif isinstance(obj, str):
            return StrPreparer(obj, prefix)
        elif isinstance(obj, int):
            return IntPreparer(obj, prefix)
        elif isinstance(obj, float):
            return FloatPreparer(obj, prefix)
        elif obj is None:
            return NonePreparer(obj, prefix)

        raise Exception(f"type {type(obj)} have not been supported yet")