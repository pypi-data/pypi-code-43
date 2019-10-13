#!/usr/bin/env python
# coding: utf-8
import re
import types
import datetime
from dateutil.relativedelta import relativedelta
import calendar

date_pattern = re.compile(r'^(?P<value>\d{4}-\d{2}-\d{2})$')
context_pattern = re.compile(r'@[^ ]+ {0,1}')
project_pattern = re.compile(r'\+[^ ]+ {0,1}')
priority_pattern = re.compile(r'[A-Z]')
repeat_pattern = re.compile(r'\d+[y,d,m,w]')

def check_space(fn):
    def _fn(arg):
        if not isinstance(arg, str):
            return False
        if len(arg.split()) > 1:
            return False
        return fn(arg)
    return _fn

@check_space
def validDate(value):
    if (date_pattern.match(value)):
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
            return True
        except:
            pass
    return False

@check_space
def validContext(value):
    if (context_pattern.match(value)):
        return True
    return False

@check_space
def validProject(value):
    if (project_pattern.match(value)):
        return True
    return False

@check_space
def validPriority(value):
    if (priority_pattern.match(value)) and len(value)==1 :
        return True
    return False

@check_space
def validDone(value):
    if value == 'x':
        return True
    return False

@check_space
def validDue(value):
    if value.startswith('due:'):
        if validDate(value.split(':')[1]):
            return True
    return False

@check_space
def validRepeat(value):
    if value.startswith('repeat:'):
        if (repeat_pattern.match(value.split(':')[1])) :
            return True
    return False

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def week(dte=None):
    if dte == None:
        dte = now()
    if not validDate(dte):
        raise ValueError("%s is not date with format Y-m-d" % dte)

    return addday(dte, 6-datetime.datetime.strptime(dte, '%Y-%m-%d').weekday())
 
def month(dte=None):
    if dte == None:
        dte = now()
    if not validDate(dte):
        raise ValueError("%s is not date with format Y-m-d" % dte)
    end = datetime.datetime.strptime(dte, '%Y-%m-%d') + relativedelta(day=31)
    return end.strftime("%Y-%m-%d")

def addday(dte=None, days=0):
    if dte == None:
        dte = now()
    if not validDate(dte):
        raise ValueError("%s is not date with format Y-m-d" % dte)
    if not isinstance(days, int):
        raise ValueError("%s is not int" % days)
    start = datetime.datetime.strptime(dte, "%Y-%m-%d")
    end = start + datetime.timedelta(days=days)
    return end.strftime("%Y-%m-%d")
 
def addmonth(dte, months=0):
    sourcedate = datetime.datetime.strptime(dte, "%Y-%m-%d")
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day).strftime("%Y-%m-%d")
 
def addyear(dte, years=0):
    sourcedate = datetime.datetime.strptime(dte, "%Y-%m-%d")
    month = sourcedate.month
    year = sourcedate.year + years
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day).strftime("%Y-%m-%d")