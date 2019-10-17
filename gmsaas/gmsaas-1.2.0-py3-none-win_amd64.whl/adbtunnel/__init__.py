# Copyright 2019 Genymobile
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
"""
ADB tunnel binary wrapper
"""
import os
import platform
from pkg_resources import resource_filename

from .genymotionadbtunneld import GenymotionAdbTunneld


def get_adb_tunnel():
    """Get a GenymotionAdbTunneld instance"""
    system = platform.system()
    is_windows = system == "Windows"
    is_linux = system == "Linux"
    is_macos = system == "Darwin"

    gmadbtunneld_dir = resource_filename(__name__, "gmadbtunneld")
    if is_windows:
        adbtunneld_exec = os.path.join(gmadbtunneld_dir, "gmadbtunneld.exe")
    elif is_linux:
        adbtunneld_exec = os.path.join(gmadbtunneld_dir, "gmadbtunneld")
    elif is_macos:
        adbtunneld_exec = os.path.join(gmadbtunneld_dir, "gmadbtunneld.app/Contents/MacOS/gmadbtunneld")

    return GenymotionAdbTunneld(adbtunneld_exec)
