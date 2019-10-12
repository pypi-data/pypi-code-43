import os
import sys
sys.path.insert(0, '.')

# from .submission import submit
# from .environment import get_mode
# get_mode()
from . import config, eda, zoo
from .ensembling import stack
from .feature import helper_list as helpers
from .feature import selection, stl
from .feature.decorators import (deregister, dropper, helper, preview,
                                 register, selector)
from .feature.storage import FeatureSet
from .feature.storage import feature_list as features
from .modelling import CustomModel
from .storage import cache
from .storage.caching import load, ls, remove, rm, save
from .storage.dataframe import DataFrame as KTDF
from .storage.dataframe import link
from .validation.experiment import experiment_list as experiments
from .validation.leaderboard import leaderboard
from .validation.validator import Validator



lb = leaderboard

# import mprop
#
# @property
# def __version__(kts):
#     ans = os.popen(f'{sys.executable} -m pip show kts').read().split()
#     return [ans[i + 1] for i in range(len(ans)) if 'version' in ans[i].lower()][0]
#
# mprop.init()
