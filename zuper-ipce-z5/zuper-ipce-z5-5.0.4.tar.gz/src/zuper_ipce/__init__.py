__version__ = "5.0.4"
from .logging import logger

logger.info(f"zuper-ipce {__version__}")


from .types import IPCE, TypeLike
from .constants import IEDO, IESO
from .conv_ipce_from_object import ipce_from_object
from .conv_ipce_from_typelike import ipce_from_typelike
from .conv_object_from_ipce import object_from_ipce
from .conv_typelike_from_ipce import typelike_from_ipce

_ = (
    ipce_from_object,
    object_from_ipce,
    typelike_from_ipce,
    ipce_from_typelike,
    TypeLike,
    IPCE,
    IEDO,
    IESO,
)
