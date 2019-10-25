from typing import List, Type
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
from swimlane_platform.upgrade_steps.upgrade_from_700_701 import UpgradeFrom700To701
from swimlane_platform.upgrade_steps.upgrade_from_701_800 import UpgradeFrom701To800
from swimlane_platform.upgrade_steps.upgrade_from_800_801 import UpgradeFrom800To801
from swimlane_platform.upgrade_steps.upgrade_from_801_900 import UpgradeFrom801To900
from swimlane_platform.upgrade_steps.upgrade_from_900_910 import UpgradeFrom900To910
from swimlane_platform.upgrade_steps.upgrade_from_910_911 import UpgradeFrom910To911
from swimlane_platform.upgrade_steps.upgrade_from_911_912 import UpgradeFrom911To912
from swimlane_platform.upgrade_steps.upgrade_from_912_1000 import UpgradeFrom912To1000


Upgrades = [
    UpgradeFrom700To701, 
    UpgradeFrom701To800, 
    UpgradeFrom800To801, 
    UpgradeFrom801To900, 
    UpgradeFrom900To910, 
    UpgradeFrom910To911,
    UpgradeFrom911To912,
    UpgradeFrom912To1000]  # type: List[Type[UpgradeStep]]
