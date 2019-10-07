# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

# list of (predefined) colors
# used as background and text color in calendar-views

from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from sql.functions import Substring
from sqlextension import RegexMatchNoCase



__all__ = ['Colors']
__metaclass__ = PoolMeta


class Colors(ModelSQL, ModelView):
    'colors'
    __name__ = 'employee_timetracking.colors'
    
    name = fields.Char(string=u'Name', required=True)
    rgbcode = fields.Char(string=u'RGB-Code', required=True, size=7)
    
    @classmethod
    def __setup__(cls):
        super(Colors, cls).__setup__()
        tab_col = cls.__table__()
        cls._order.insert(0, ('name', 'ASC'))
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_col, tab_col.name), 
            u'This name is already in use.'),
            ('uniq_color', 
            Unique(tab_col, tab_col.rgbcode), 
            u'This rgb-color is already in use.'),
            ('check_rgb',
            Check(tab_col, 
                RegexMatchNoCase(tab_col.rgbcode, '^#[0-9,a-f]{6}$')),
            u'Invalid Color - syntax: #RRGGBB in hex values'),
            ])

    @classmethod
    def default_name(cls):
        return 'Black'
        
    @classmethod
    def default_rgbcode(cls):
        return '#000000'

# end Colors
