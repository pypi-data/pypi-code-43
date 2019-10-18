from cathartidae.constants import BuilderKeysEnum

__all__ = ["ControlDecorator"]


class ControlDecorator(object):
    def __init__(self, builder_args, decorator_builder):
        self.operand           = builder_args.get(BuilderKeysEnum.OPERAND)
        self.func              = builder_args.get(BuilderKeysEnum.FUNC)
        self.default           = builder_args.get(BuilderKeysEnum.DEFAULT)
        self.decorator_builder = decorator_builder

    def __call__(self, *args, **kwargs):
        decorator_builder = (self.decorator_builder.add(BuilderKeysEnum.FUNC, self.func)
                                                   .add(BuilderKeysEnum.OPERAND, self.operand)
                                                   .add(BuilderKeysEnum.DEFAULT, self.default))
        return decorator_builder.invoke(*args, **kwargs)