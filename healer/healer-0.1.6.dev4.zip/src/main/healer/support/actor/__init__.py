

from __future__ import annotations

import pykka

from . import proper

pykka._ref.ActorRef = proper.ProperRef
pykka._actor.ActorRef = proper.ProperRef
