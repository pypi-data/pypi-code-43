

def name_of(entry):
    return entry.__name__


class State:

    def __init__(self):
        self.count = 0

    def __str__(self):
        return f"State(count={self.count})"


class StateFun:

    @staticmethod
    def increment(state, *_):
        state.count += 1

    @staticmethod
    def decrement(state, *_):
        state.count -= 1


class StateSupport:

    @staticmethod
    def method_dict():
        method_dict = list()
        for intent in StateFun.__dict__:
            if intent.startswith("_"):
                continue
            member = getattr(StateFun, intent)
            if callable(member):
                method_dict.append(member)
        return method_dict


class ArkonUnit:

    def __init__(self):

        state = State()

        methods = dict()

        for method in StateSupport.method_list():
            intent = name_of(method)
            methods[intent] = lambda *args, method = method: method(*args)

        increment = methods[name_of(StateFun.increment)]

        increment(state)

        print(state)


ArkonUnit()
