# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2019 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = ['commands']

from .build import BuildCurseforge, BuildLocal, BuildServer, BuildRouthio
from .findmodupdates import FindModUpdatesCommand
from .info import InfoCommand
from .launch import LaunchCommand
from .lock import LockCommand
from .search import SearchCommand
from .updatedb import UpdateDbCommand

##############################################################################

commands = [
             BuildCurseforge,
             BuildLocal,
             BuildRouthio,
             BuildServer,
             FindModUpdatesCommand,
             InfoCommand,
             LaunchCommand,
             LockCommand,
             SearchCommand,
             UpdateDbCommand,
           ]

##############################################################################
# THE END
