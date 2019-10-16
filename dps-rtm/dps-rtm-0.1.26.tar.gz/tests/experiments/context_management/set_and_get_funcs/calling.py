import tests.experiments.context_management.set_and_get_funcs.digits as d


def print_len():
    print(len(d.get_digits()))


with d.set_digits():
    print_len()