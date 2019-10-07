# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, division, print_function, unicode_literals)


# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = 'DA395940D76FFEB6A68EA2DB16FC015D'
    
_lr_action_items = {'UINT':([0,2,10,12,19,20,22,23,35,36,38,],[-7,12,-6,19,25,27,29,32,25,25,25,]),'MINUTE':([4,6,8,12,13,19,21,24,25,26,27,28,29,31,32,34,40,],[16,-14,-15,-17,-16,-9,-12,-8,-9,-13,-9,-10,36,37,38,39,-11,]),'COLON':([12,27,],[20,35,]),'$end':([1,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,],[-4,-1,-32,-5,-14,-2,-15,-3,0,-17,-16,-33,-31,-35,-24,-34,-9,-12,-25,-18,-8,-9,-13,-9,-10,-9,-26,-8,-9,-19,-8,-27,-28,-20,-21,-11,-29,-22,-30,-23,]),'SIMPLE_UNIT':([4,6,8,12,13,19,21,24,25,26,27,28,40,],[14,-14,-15,-17,-16,-9,-12,-8,-9,-13,-9,-10,-11,]),'DEGREE':([4,6,8,12,13,19,21,24,25,26,27,28,40,],[15,-14,-15,22,-16,-9,-12,-8,-9,-13,-9,-10,-11,]),'UFLOAT':([0,2,10,12,19,20,22,23,35,36,38,],[-7,13,-6,24,24,24,31,34,24,24,24,]),'HOUR':([4,6,8,12,13,19,21,24,25,26,27,28,40,],[17,-14,-15,23,-16,-9,-12,-8,-9,-13,-9,-10,-11,]),'SECOND':([4,6,8,12,13,19,21,24,25,26,27,28,40,41,42,],[18,-14,-15,-17,-16,-9,-12,-8,-9,-13,-9,-10,-11,43,44,]),'SIGN':([0,],[10,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'ufloat':([12,19,20,22,23,35,36,38,],[21,26,28,30,33,40,41,42,]),'generic':([0,],[4,]),'arcminute':([0,],[1,]),'simple':([0,],[5,]),'sign':([0,],[2,]),'colon':([0,],[6,]),'dms':([0,],[7,]),'hms':([0,],[3,]),'spaced':([0,],[8,]),'angle':([0,],[11,]),'arcsecond':([0,],[9,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> angle","S'",1,None,None,None),
  ('angle -> hms','angle',1,'p_angle','angle_utilities.py',134),
  ('angle -> dms','angle',1,'p_angle','angle_utilities.py',135),
  ('angle -> arcsecond','angle',1,'p_angle','angle_utilities.py',136),
  ('angle -> arcminute','angle',1,'p_angle','angle_utilities.py',137),
  ('angle -> simple','angle',1,'p_angle','angle_utilities.py',138),
  ('sign -> SIGN','sign',1,'p_sign','angle_utilities.py',144),
  ('sign -> <empty>','sign',0,'p_sign','angle_utilities.py',145),
  ('ufloat -> UFLOAT','ufloat',1,'p_ufloat','angle_utilities.py',154),
  ('ufloat -> UINT','ufloat',1,'p_ufloat','angle_utilities.py',155),
  ('colon -> sign UINT COLON ufloat','colon',4,'p_colon','angle_utilities.py',161),
  ('colon -> sign UINT COLON UINT COLON ufloat','colon',6,'p_colon','angle_utilities.py',162),
  ('spaced -> sign UINT ufloat','spaced',3,'p_spaced','angle_utilities.py',171),
  ('spaced -> sign UINT UINT ufloat','spaced',4,'p_spaced','angle_utilities.py',172),
  ('generic -> colon','generic',1,'p_generic','angle_utilities.py',181),
  ('generic -> spaced','generic',1,'p_generic','angle_utilities.py',182),
  ('generic -> sign UFLOAT','generic',2,'p_generic','angle_utilities.py',183),
  ('generic -> sign UINT','generic',2,'p_generic','angle_utilities.py',184),
  ('hms -> sign UINT HOUR','hms',3,'p_hms','angle_utilities.py',193),
  ('hms -> sign UINT HOUR ufloat','hms',4,'p_hms','angle_utilities.py',194),
  ('hms -> sign UINT HOUR UINT MINUTE','hms',5,'p_hms','angle_utilities.py',195),
  ('hms -> sign UINT HOUR UFLOAT MINUTE','hms',5,'p_hms','angle_utilities.py',196),
  ('hms -> sign UINT HOUR UINT MINUTE ufloat','hms',6,'p_hms','angle_utilities.py',197),
  ('hms -> sign UINT HOUR UINT MINUTE ufloat SECOND','hms',7,'p_hms','angle_utilities.py',198),
  ('hms -> generic HOUR','hms',2,'p_hms','angle_utilities.py',199),
  ('dms -> sign UINT DEGREE','dms',3,'p_dms','angle_utilities.py',212),
  ('dms -> sign UINT DEGREE ufloat','dms',4,'p_dms','angle_utilities.py',213),
  ('dms -> sign UINT DEGREE UINT MINUTE','dms',5,'p_dms','angle_utilities.py',214),
  ('dms -> sign UINT DEGREE UFLOAT MINUTE','dms',5,'p_dms','angle_utilities.py',215),
  ('dms -> sign UINT DEGREE UINT MINUTE ufloat','dms',6,'p_dms','angle_utilities.py',216),
  ('dms -> sign UINT DEGREE UINT MINUTE ufloat SECOND','dms',7,'p_dms','angle_utilities.py',217),
  ('dms -> generic DEGREE','dms',2,'p_dms','angle_utilities.py',218),
  ('simple -> generic','simple',1,'p_simple','angle_utilities.py',231),
  ('simple -> generic SIMPLE_UNIT','simple',2,'p_simple','angle_utilities.py',232),
  ('arcsecond -> generic SECOND','arcsecond',2,'p_arcsecond','angle_utilities.py',241),
  ('arcminute -> generic MINUTE','arcminute',2,'p_arcminute','angle_utilities.py',247),
]
