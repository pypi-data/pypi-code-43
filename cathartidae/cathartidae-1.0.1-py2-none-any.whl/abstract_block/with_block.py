from cathartidae.abstract_block.abstract_block import AbstractBlock

__all__ = ["WithBlock"]


class WithBlock(AbstractBlock):

    def __call__(self, *args, **kwargs):
        with self.pre_operator(self.decorator_builder.operand):
            return self.decorator_builder.func(*args, **kwargs)