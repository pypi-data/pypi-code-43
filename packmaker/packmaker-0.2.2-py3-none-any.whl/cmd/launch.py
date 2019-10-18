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

import os
import subprocess

from .build import BuildLocal

##############################################################################

launch_script = """#!/bin/sh

WORKDIR="$(dirname ${{0}})"
cd "${{WORKDIR}}"

MAX_RAM="8192M"

JAVA_PARAMETERS="-XX:+UseG1GC -Dsun.rmi.dgc.server.gcInterval=2147483646"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:+UnlockExperimentalVMOptions"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:G1NewSizePercent=20"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:G1ReservePercent=20"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:MaxGCPauseMillis=50"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:G1HeapRegionSize=32M"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -Dfml.readTimeout=180"

CLASSPATH=$(find libraries -name '*.jar' -printf '%p:'|sed 's/:$//')

MINECRAFT_PARAMS="--version 1.12.2 --accessToken 0"
MINECRAFT_PARAMS="${{MINECRAFT_PARAMS}} --username Player --uid 00000000-0000-0000-0000-000000000000"
MINECRAFT_PARAMS="${{MINECRAFT_PARAMS}} --gameDir . --assetsDir ./assets --assetIndex 1.12"
MINECRAFT_PARAMS="${{MINECRAFT_PARAMS}} --tweakClass net.minecraftforge.fml.common.launcher.FMLTweaker"
MINECRAFT_PARAMS="${{MINECRAFT_PARAMS}} --versionType Forge"

MINECRAFT_MAINCLASS="net.minecraft.launchwrapper.Launch"

echo "Starting minecraft client..."
exec java -cp ${{CLASSPATH}} -Xms${{MAX_RAM}} -Xmx${{MAX_RAM}} ${{JAVA_PARAMETERS}} \\
     ${{MINECRAFT_MAINCLASS}} ${{MINECRAFT_PARAMS}}
"""

##############################################################################


class LaunchCommand (BuildLocal):
    """
    Launch a local installation
    """
    name = 'launch'

    def run_command(self, parsed_args):
        super(LaunchCommand, self).run_command(parsed_args)
        self.run_launcher()

    def run_launcher(self):
        filename = os.path.join(self.builder.build_location(), 'start.sh')
        with open(filename, 'w') as launchs:
            launchs.write(launch_script.format())
        os.chmod(filename, 0o755)
        subprocess.run(filename)

##############################################################################
# THE END
