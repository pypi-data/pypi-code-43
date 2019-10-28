#
# Copyright (c) 2013-2019 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.


import enum


class ReturnCode(enum.IntEnum):
    success = 0
    warning = 1
    error = -1


class ScanStatus(enum.IntEnum):
    empty = 0
    ready = 10
    uploaded = 20
    launched = 30
    processed = 40
    finished = 50
    flushed = 60
    # cancel
    cancelling = 100
    cancelled = 110
    # errors
    error = 1000
    # Probes 101x
    error_probe_missing = 1010
    error_probe_na = 1011
    # FTP 102x
    error_ftp_upload = 1020

    def is_error(self):
        return self >= self.error


class ScanPriority(enum.IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class ProbeStatus(enum.IntEnum):
    CANCELLED = -2
    ERROR = -1
    GOOD = 0
    BAD = 1
    NEUTRAL = 2


class FileExtStatus(enum.IntEnum):
    ERROR = -1
    GOOD = 0
    BAD = 1


class ProbeCategory(enum.Enum):
    unknown = "unknown"
    antivirus = "antivirus"
    database = "database"
    deferred = "deferred"
    external = "external"
    metadata = "metadata"
    sandbox = "sandbox"
    tests = "tests"
    tools = "tools"


class ArtifactType(enum.IntEnum):
    LOG = 1
    PCAP = 2
    SCREENSHOT = 3
    MEMDUMP = 4
    EXTRACTED = 5
    DISASSEMBLY = 6
