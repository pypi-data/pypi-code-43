#! /usr/bin/env python
# -*- coding: utf-8 -*-
import solid
from types import SimpleNamespace
from pathlib import Path

class SPNamespace(SimpleNamespace):
    def include_scad(self, scad_path):
        solid.use(scad_path, dest_namespace_dict=self.__dict__)

def import_all_scad():
    mcad_dir = Path(__file__).parent /'MCAD'
    assert mcad_dir.exists()

    for f in mcad_dir.glob('*.scad'):
        name = f.stem
        n = SPNamespace()
        try:
            n.include_scad(f.absolute())
            globals()[name] = n
        except Exception as e:
            print(f'Unable to load SCAD code at {f.absolute()} with error: {e}')     
    return True   

# NOTE: simply importing solid_mcad does a lot of work; reading & parsing 20+ files,
# then creating Python classes for each module in a scad file. It's expensive,
# but this way you can treat SCAD code as if it were all python with, e.g. 
# from solid_mcad import involute_gears
# gears = involute_gears.test_bevel_gear_pair()
import_all_scad()