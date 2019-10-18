from cathartidae.abstract_block.abstract_block import AbstractBlock

__all__ = ["WhileBlock", "WhileBlockGenerator"]


class WhileBlock(AbstractBlock):
    def __call__(self, *args, **kwargs):
        while self.pre_operator(self.decorator_builder.operand):
            self.decorator_builder.func(*args, **kwargs)


class WhileBlockGenerator(AbstractBlock):
    def __call__(self, *args, **kwargs):
        while self.pre_operator(self.decorator_builder.operand):
            yield self.decorator_builder.func(*args, **kwargs)