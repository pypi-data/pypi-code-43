from lura.log import Logging

logs = Logging(
  std_logger = __name__,
  std_format = Logging.formats.hax,
)

del Logging

from giga.coreutils import System
from giga.coreutils import Local
from giga.coreutils import Ssh
from giga.config import Cancel
from giga.config import Fail
from giga.config import Configuration
from giga.group import Group
from giga import configs
