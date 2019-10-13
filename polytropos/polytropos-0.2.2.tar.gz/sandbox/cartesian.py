import itertools

example = [[["a", 1], ["b", 2], ["c", 3]], [["foo"]], [[True], [False]]]

# SO 10823877
def flatten(container):
    for i in container:
        if isinstance(i, (list, tuple)):  # I didn't know you could supply a tuple of classes...
            for j in flatten(i):
                yield j
        else:
            yield i

for nested in itertools.product(*example):
    flat = list(flatten(nested))
    print(flat)
