#!/usr/bin/env python
# coding: utf-8
import types
from requests.auth import HTTPBasicAuth
import requests
import os
import tempfile

from todotxt.util import validDate, validDue, validContext, validProject, validPriority, validDone, validRepeat, now, addday, addmonth, addyear

def _formatIntervalDate(dtes):
    if dtes == None:
        dtes = ".."
    if '..' not in dtes:
        dtes = "%s..%s" % (dtes, dtes)
    start, end =  dtes.split('..')
    return [validDate(start)==True and start or None , validDate(end)==True and end or None]

def filterTask(id=None, due=None, priority=None, created=None, completed=None, txt=None, done=None):
    due = _formatIntervalDate(due)
    created = _formatIntervalDate(created)
    completed = _formatIntervalDate(completed)
    if not validPriority(priority):
        priority=None
    if not isinstance(done, bool):
        done=None

    def _fn(obj):
        res = True
        if id:
            res = min(res, obj.id == id)
        if due[0] != None and obj.due == None:
            res = False
        if due[1] != None and obj.due == None:
            res = False
        if created[0] != None and obj.created == None:
            res = False
        if created[1] != None and obj.created == None:
            res = False
        if completed[0] != None and obj.completed == None:
            res = False
        if completed[1] != None and obj.completed == None:
            res = False

        if due[0] != None and obj.due != None:
            res = min(res, obj.due >= due[0])
        if due[1] != None and obj.due != None:
            res = min(res, due[1] >= obj.due)
        if created[0] != None and obj.created != None:
            res = min(res, obj.created >= created[0])
        if created[1] != None and obj.created != None:
            res = min(res, created[1] >= obj.created)
        if completed[0] != None and obj.completed != None:
            res = min(res, obj.completed >= completed[0])
        if completed[1] != None and obj.completed != None: 
            res = min(res, completed[1] >= obj.completed)
        if txt:
            for word in txt.split():
                res = min(res, word in obj.txt.split())
        if done != None:
            res = min(res, obj.done == done)   
        return res
    return _fn

class Task(object):

    def __init__(self, txt="", id=None):
        self._done = False
        self._priority = None
        self._created = None
        self._completed = None
        self._txt = ""
        self.id = id
        txts = txt.split()
        if len(txts) > 0:
            if validDone(txts[0]):
                self.done = True
                txts = txts[1:]
            if txts[0].startswith('(') and txts[0].endswith(')') and len(txts[0]) == 3:
                self.priority = txts[0][1]
                txts = txts[1:]
            if validDate(txts[0]):
                if len(txts) > 1 and validDate(txts[1]):
                    self.created = txts[1]
                    self.completed = txts[0]
                    txts = txts[2:]
                else:
                    self.created = txts[0]
                    txts = txts[1:]
            self.txt = ' '.join(txts)
            
    def _check_date(self, value):
        if value == None or validDate(value):
            return value
        raise ValueError("%s is not date" % value)

    @property
    def txt(self):
        return self._txt
    
    @txt.setter
    def txt(self, value):
        self._txt = value.strip()
 
    @property
    def done(self):
        return self._done
    
    @done.setter
    def done(self, value):
        if type(value) == bool:
            self._done = value
        else:
            self._done = validDone(value)

    @property
    def priority(self):
        return self._priority
    
    @priority.setter
    def priority(self, value):
        if value == None:
            self._priority = None
        if validPriority(value):
            self._priority = value
    
    @property
    def created(self):
        return self._created
    
    @created.setter
    def created(self, value):
        self._created = self._check_date(value)   

    @property
    def completed(self):
        return self._completed
    
    @completed.setter
    def completed(self, value):
        self._completed = self._check_date(value)   

    @property
    def due(self):
        dus = [du for du in self.txt.split() if validDue(du)]
        if len(dus):
            return dus[0].split(':')[1]
        return None
    
    @due.setter
    def due(self, value):
        if value == None:
            if self.due != None:
                self.remove("due:%s" % self.due)
        else:
            if validDate(value):
                if self.due:
                    self.remove("due:%s" % self.due)
                self.append("due:%s" % value)    
            else:
                raise ValueError("%s is not date" % value)

    @property
    def projects(self):
        return [pr[1:] for pr in self.txt.split() if validProject(pr) ]
    
    @projects.setter
    def projects(self, value):
        value = [ pr for pr in value if validProject('+%s' % pr)]
        for pr in value:
            if pr not in self.projects:
                self.append('+%s' % pr)
        for pr in self.projects:
            if pr not in value:
                self.remove('+%s' % pr)

    @property
    def contexts(self):
        return [co[1:] for co in self.txt.split() if validContext(co) ]
    
    @contexts.setter
    def contexts(self, value):
        value = [co for co in value if validContext('@%s' % co)]
        for co in value:
            if co not in self.contexts:
                self.append('@%s' % co)
        for co in self.contexts:
            if co not in value:
                self.remove('@%s' % co)

    def append(self, value):
        self.txt = "%s %s" % (self.txt, value)
    
    def remove(self, value):
        self.txt = ' '.join([ elt for elt in self.txt.split() if elt != value])
    
    def __str__(self):
        for_str = []
        if self.done: for_str.append('x')
        if self.priority: for_str.append('(%s)' % self.priority)
        if self.completed and self.created:
            for_str.append(self.completed)
        if self.created: for_str.append(self.created)
        for_str.append(self.txt)        
        return ' '.join(for_str)
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and str(self) == str(other) and self.id == other.id
    
    def __lt__(self, other):
        if self.due == other.due:
            if self.priority == other.priority:
                return (self.created and self.created or '1970-01-01') < (other.created and other.created or '1970-01-01')
            else:
                return (self.priority and self.priority or 'Z') < (other.priority and other.priority or 'Z')
        return (self.due and self.due or '9999-01-01') < (other.due and other.due or '9999-01-01')

    def __le__(self, other):
        if self.due == other.due:
            if self.priority == other.priority:
                return (self.created and self.created or '1970-01-01') <= (other.created and other.created or '1970-01-01')
            else:
                return (self.priority and self.priority or 'Z') <= (other.priority and other.priority or 'Z')
        return (self.due and self.due or '9999-01-01') <= (other.due and other.due or '9999-01-01')

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __gt__(self, other):
        if self.due == other.due:
            if self.priority == other.priority:
                return (self.created and self.created or '1970-01-01') > (other.created and other.created or '1970-01-01')
            else:
                return (self.priority and self.priority or 'Z') > (other.priority and other.priority or 'Z')
        return (self.due and self.due or '9999-01-01') > (other.due and other.due or '99999-01-01')

    def __ge__(self, other):
        if self.due == other.due:
            if self.priority == other.priority:
                return (self.created and self.created or '1970-01-01') >= (other.created and other.created or '1970-01-01')
            else:
                return (self.priority and self.priority or 'Z') >= (other.priority and other.priority or 'Z')
        return (self.due and self.due or '9999-01-01') >= (other.due and other.due or '9999-01-01')

    @property
    def repeat(self):
        repeats = [repeat for repeat in self.txt.split() if validRepeat(repeat)]
        if len(repeats):
            return repeats[0].split(':')[1]
        return None
    
    @repeat.setter
    def repeat(self, value):
        if value == None:
            if self.repeat != None:
                self.remove("repeat:%s" % self.repeat)
        else:
            if validRepeat("repeat:%s" % value):
                if self.repeat:
                    self.remove("repeat:%s" % self.repeat)
                self.append("repeat:%s" % value)    
            else:
                raise ValueError("%s is not repeat format" % value)

    @property
    def next_repeat(self):
        if self.repeat == None:
            return None
        start = now()
        if self.due != None:
            start = self.due
        if self.repeat[-1] == 'd':
            return addday(start, int(self.repeat[:-1]))
        if self.repeat[-1] == 'w':    
            return addday(start, int(self.repeat[:-1])*7)
        if self.repeat[-1] == 'm':
            return addmonth(start, int(self.repeat[:-1]))
        if self.repeat[-1] == 'y':
            return addyear(start, int(self.repeat[:-1]))
 

class Tasks(list):

    def __init__(self, *args):
        list.__init__(self, *args)

    @property
    def _next_id(self):
        return max([-1,]+[task.id for task in self])+1

    def append(self, obj):
        if not isinstance(obj, Task):
            raise ValueError("%s is not Task" % obj)
        if obj.id == None:
            obj.id = self._next_id
        list.append(self, obj)

    def filter(self, id=None, due=None, priority=None, created=None, completed=None, txt=None, done=None):
        return list(filter(filterTask(id, due, priority, created, completed, txt, done), self))
    
    def get_id(self, id):
        try:
            return self.filter(id=id)[0]
        except:
            return None

class TasksFile(Tasks):

    def __init__(self, path, *args):
        Tasks.__init__(self, *args)
        self.path = path
    
    def open(self):
        del self[:]
        self._open(self.path)

    def _open(self, path):
        id = 0
        with open(path, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                if len(line.strip()) > 0:
                    self.append(Task(line.strip(), id))
                    id = id+1

    def _save(self, path):
        with open(path, 'w') as f:
            for task in self:
                f.write(str(task)+'\n')

    def save(self):
        self._save(self.path)

class TasksWebDav(TasksFile):

    def __init__(self, url, user=None, password=None, *args):
        TasksFile.__init__(self, "", *args)
        self.url = url
        self.path = self.url.split('/')[-1]
        if user:
            self.auth = HTTPBasicAuth(user, password)
        else:
            self.auth = None
    
    def open(self):
        del self[:]
        id = 0
        req = requests.get(self.url, auth=self.auth)
        if req.status_code == 404:
            try:
                self.save()            
            except:
                pass
            req = requests.get(self.url, auth=self.auth)
            if req.status_code != 200:
                raise ValueError("%s not found , status request %s" % (self.url, req.status_code))
        with open(os.path.join(tempfile.gettempdir(), self.path), 'w') as f:
            f.write(str(req.text))
        TasksFile._open(self, os.path.join(tempfile.gettempdir(), self.path))



    def save(self):
        TasksFile._save(self, os.path.join(tempfile.gettempdir(), self.path))
        file_data = ""
        with open(os.path.join(tempfile.gettempdir(), self.path)) as fh:
            file_data = fh.read()
        try:
            req = requests.put(self.url, data=file_data, auth=self.auth, headers={'content-type':'text/plain'}, params={'file': self.path}) 
            if req.status_code not in (201, 204):
                raise ValueError(req.status_code)
        except:
            raise ValueError('Error save %s\npath %s\ndata:\n%s' % (self.url, self.path, file_data ))
        