from tests.experiements.context_management import custom_class as cc

doubler = cc.Doubler()
with cc.set_count(2):
    doubled = doubler()
print(doubled)


class Tripler(cc.Doubler):
    def __call__(self):
        return 3 * self.get_count()


tripler = Tripler()
# with cc.set_count(3):
doubled = tripler()
print(doubled)

# print(tripler())
