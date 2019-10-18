from cathartidae.abstract_block.abstract_block import AbstractBlock
from cathartidae.constants import BuilderKeysEnum

__all__ = ["IfBlock"]


class IfBlock(AbstractBlock):

    def __call__(self, *args, **kwargs):
        if self.pre_operator(self.decorator_builder.operand):
            return self.decorator_builder.func(*args, **kwargs)
        return self.decorator_builder.default