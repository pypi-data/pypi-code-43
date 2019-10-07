# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


# timeaccount.py
WF_ACCOUNT_CREATED = 'c'
WF_ACCOUNT_EXAMINE = 'e'
WF_ACCOUNT_LOCK = 'l'
WF_ACCOUNT_EVALUATED = 'v'

# period.py
WF_PERIOD_CREATED = 'c'
WF_PERIOD_EXAMINE = 'e'
WF_PERIOD_LOCK = 'l'

# breakperiod.py
WF_BREAKPERIOD_CREATED = 'c'
WF_BREAKPERIOD_EXAMINE = 'e'
WF_BREAKPERIOD_LOCK = 'l'


# evaluation
WF_EVALUATION_CREATED = 'c'
WF_EVALUATION_ACTIVE = 'a'
WF_EVALUATION_LOCK = 'l'


sel_weekday = [
        ('0', u'Mon'),
        ('1', u'Tue'),
        ('2', u'Wed'),
        ('3', u'Thu'),
        ('4', u'Fri'),
        ('5', u'Sat'),
        ('6', u'Sun'),
    ]

sel_weekday2 = [
        ('0', u'Sun'),
        ('1', u'Mon'),
        ('2', u'Tue'),
        ('3', u'Wed'),
        ('4', u'Thu'),
        ('5', u'Fri'),
        ('6', u'Sat'),
    ]


# type of vacation day
VACDAY_NONE = '0'
VACDAY_FULL = '1'
VACDAY_HALF = '2'
sel_vacationday = [
        (VACDAY_NONE, u'not a vacation day'),
        (VACDAY_FULL, u'full vacation day'),
        (VACDAY_HALF, u'half vacation day'),
    ]


# account rule - holiday
ACRULE_HOLIDAY_AT = 'a'
ACRULE_HOLIDAY_NOTAT = 'n'
ACRULE_HOLIDAY_NODEF = '-'
sel_accrule_holiday = [
    (ACRULE_HOLIDAY_NODEF, u'-/-'),
    (ACRULE_HOLIDAY_AT, u'is public holiday'),
    (ACRULE_HOLIDAY_NOTAT, u'is not public holiday'),
    ]
dict_accrule_holiday = {}
for i in sel_accrule_holiday:
    (k1, v1) = i
    dict_accrule_holiday[k1] = v1
