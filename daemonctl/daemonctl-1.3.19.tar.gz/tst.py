#!/usr/bin/env python

import sys
from src import runasdaemon

#runasdaemon.setproctitle("hejsan")
#raw_input()

#runasdaemon.setproctitle( (sys.argv[1]))
#raw_input()

name = sys.argv[1] + "_APA"*10
runasdaemon.setproctitle(name)
raw_input()

