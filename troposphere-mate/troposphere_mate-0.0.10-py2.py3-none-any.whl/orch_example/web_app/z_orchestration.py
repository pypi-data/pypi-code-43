# -*- coding: utf-8 -*-

from superjson import json
from pathlib_mate import Path
from troposphere_mate.core.orch import Orchestration
from troposphere_mate.core.canned import Canned
from troposphere_mate.orch_example.web_app import t1_vpc, t99_master

orch = Orchestration()
orch.add_master_tier(t99_master.MasterTier)
orch.add_tier(t1_vpc.VPCTier)
orch.set_config_dir(Path(__file__).change(new_basename="config").abspath)

orch.add_execution_plan_file(
    Path(__file__).change(new_basename="plan.json").abspath)
orch.plan(workspace_dir=Path(__file__).change(new_basename="tmp").abspath)
