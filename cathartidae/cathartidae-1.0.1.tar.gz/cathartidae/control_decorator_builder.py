import attr

from cathartidae.lib.echos import echo

__all__ = ["ControlDecoratorBuilder"]


# of course we could just consolidate all decorators to take in a callback, and delegate dynamic/static operand behavior
# to the user. initially, I wanted precision about what the user was going to be doing, now it might be worth reevaluating
# since getting rid of the distinction on our end would simplify things. ALOT. we will reevaluate the need for this serious change
@attr.s
class ControlDecoratorBuilder(object):
    abstract_block_constructor = attr.ib()
    pre_operation              = attr.ib(default=echo)

    def add(self, builder_key, value):
        setattr(self, builder_key, value)
        return self

    def invoke(self, *args, **kwargs):
        AbstractBlockConstructor = self.abstract_block_constructor
        try:
            return AbstractBlockConstructor(self, self.pre_operation)(*args, **kwargs)
        except AttributeError as ex:
            msg = "Either the appropriate values were not resolved to the decorator builder. Or an invalid operation was performed on a value without an expected attribute. Inner exception: {}".format(ex)
            raise Exception(msg)
