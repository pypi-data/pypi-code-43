from cathartidae.abstract_block.abstract_block import AbstractBlock

__all__ = ["ForBlock", "ForBlockGenerator"]


class ForBlock(AbstractBlock):
    def __call__(self, *args, **kwargs):
        for _ in self.pre_operator(self.decorator_builder.operand):
            self.decorator_builder.func(*args, **kwargs)


class ForBlockGenerator(AbstractBlock):
    def __call__(self, *args, **kwargs):
        for _ in self.pre_operator(self.decorator_builder.operand):
            yield self.decorator_builder.func(*args, **kwargs)