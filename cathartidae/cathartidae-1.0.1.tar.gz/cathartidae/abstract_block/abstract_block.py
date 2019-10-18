import attr

__all__ = ["AbstractBlock"]


@attr.s
class AbstractBlock(object):
    decorator_builder    = attr.ib()
    pre_operator         = attr.ib()
