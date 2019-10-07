# -*- coding: utf-8 -*-
"""
Mangrove API.
Sets of tools to control Mangrove data.

Functions:
    getCurrentNode: Return the current node object.

    getCurrentGraph: Return the current graph object.

    getCurrentProject: Return the current project object.

    unlock_request: Ask for a Mangrove instance to free a node.

    extractPath: Extract the shape and median color of an image.

    ExeScript: Execute a script.

Classes:
    MgvProject: Stores the project attributes.

    MgvContext: Stores environment sets.

    MgvHud: Script to launch at events.

    MgvPattern: Class of Mangrove graphs.

    MgvGraphTemplate: Default graph to preset new ones.

    MgvGraph: Stores the nodes tree.

    MgvGroup: A colored box that group nodes.

    MgvNode: Mangrove node.

    MgvNodeVersion: A version of a node.

    MgvLink: Link object between nodes.

    MgvVariable: A variable that can be attached to a graph or a node version.

    MgvType: Class of a node.

    MgvTypeVersion: Version of a type.

    MgvTypeFile: An output file of a node.

    MgvAction: An execution script that can be lauched by a node.

    MgvParam: Parameter of a node.
"""
from __future__ import print_function
import json
import math
import os
import random
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import uuid
import importlib
import pickle
import base64
from six import string_types

mgvWrapper = None


def changeWrapper():
    global mgvWrapper
    global choosen_wrapper
    home = os.getenv('HOME') if os.getenv('HOME') else os.getenv('USERPROFILE')
    localSettingsFile = os.path.join(home, 'mangrove1.0', 'settings.info')

    bdd_name, bdd_user, bdd_pwd = '', '', ''
    if os.path.exists(localSettingsFile):
        with open(localSettingsFile) as fid:
            dic = json.load(fid)
            choosen_wrapper = dic['wrapper']['current']
            bdd_name = dic['wrapper'][choosen_wrapper]['host']
            bdd_user = dic['wrapper'][choosen_wrapper]['user']
            bdd_pwd = dic['wrapper'][choosen_wrapper]['pwd']
    else:
        choosen_wrapper = 'mgvWrapperNoServer'
    sys.path.append(os.path.dirname(__file__))
    mgvWrapper = importlib.import_module(choosen_wrapper)
    mgvWrapper.connect(bdd_name, bdd_user, bdd_pwd)
    return mgvWrapper


changeWrapper()


def unlock_request(address, port, path, nodename, user, fromport):
    """Ask for a Mangrove instance to free a node.

    Parameters:
        address (str): IP address of the Mangrove instance.
        port (str): port used by the Mangrove instance.
        path (str): the graph full path i.e. "MyProject:Shots:0001:0001"
        nodename (str): the node name.
        user (str): the user of this Mangrove session.
        fromport (str): the IP address and port of this Mangrove session.

    Return:
        str: "noroute", "notmine", "nochange" or "wait"
    """
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    text = None
    port = int(port)
    try:
        s.settimeout(5)
        s.connect((address, port))
        msg = "*MGVSEPARATOR*".join(["MGVUNLOCK", path, nodename, user, fromport])
        s.send(msg.encode())
        text = s.recv(1024)
    except socket.error as e:
        if e.errno == 113:
            print("ERROR: %s:%s > No route to host !" % (address, port), file=sys.__stderr__)
            return "noroute"
    finally:
        s.close()
    return text


def mgvDicoReplace(d):
    """Recursively replace each variable name by
    its value in a dictionary.

    Parameters:
        d (dict): the dictionary with unevaluated variables.
    Return:
        dict: a new dictionary with replaced variables names.
    """
    dico = dict(d)
    b = True
    c = 0
    while b and c < 100:
        b = False
        for key1 in dico:
            s = dico[key1]
            if '$' in s:
                for key2 in dico:
                    if key2 != key1:
                        if len(key2):
                            s = s.replace("${%s}" % key2, dico[key2])
                            d = dico[key2]
                            if isinstance(d, str):
                                d = d.encode('string-escape')
                            elif isinstance(d, unicode):
                                d = d.encode('unicode-escape')
                            s = re.sub('\$%s(?!\w)' % key2, d, s)
                if s != dico[key1]:
                    dico[key1] = s
                    b = True
                    c += 1
    for key in dico.keys():
        if len(key):
            dico[key] = os.path.expandvars(dico[key])
        else:
            del dico[key]
    return dico


def mgvcopy(src, dst):
    """Copy a file or directory.

    Parameters:
        src (str): source path.
        dst (str): destination path.
    """
    if os.path.islink(src):
        linkto = os.readlink(src)
        if os.path.exists(dst):
            os.remove(dst)
        os.symlink(linkto, dst)
    else:
        if os.path.isdir(src):
            try:
                shutil.copytree(src, dst)
            except (IOError, OSError, shutil.Error) as e:
                print(src, '>', dst, ':', e)
        else:
            shutil.copyfile(src, dst)


def extractPath(image):
    """Extract the shape and median color of an image.

    Parameters:
        image (str): the image path.
    Return:
        list of tuples, color: A list of 2D coordinates and a color.
    """
    from PySide import QtGui
    image = QtGui.QImage(image)
    chemin = []
    W = image.width()
    H = image.height()
    D = pow(W*W+H*H, .5)
    for angle in range(0, 360, 5):
        x2, y2 = W*.5, H*.5
        x1, y1 = math.cos(angle*3.141592/180)*D+x2, math.sin(angle*3.141592/180)*D+y2 
        Nstep = int(D*2)
        for step in range(Nstep):
            step = step*1.0/Nstep
            x = int(x1*(1-step)+x2*step)
            y = int(y1*(1-step)+y2*step)
            if W > x > 0 and H > y > 0:
                alpha = QtGui.QColor.fromRgba(image.pixel(x, y)).alpha()
                if alpha > 0:
                    x, y = (x-x2)*100.0/W, (y-y2)*100.0/W
                    chemin.append([x, y])
                    break
    moy = [0.0, 0.0, 0.0]
    n = 0.0
    for i in range(10000):
        x = int(random.random()*W)
        y = int(random.random()*H)
        
        pix = image.pixel(x, y)
        color = QtGui.QColor.fromRgba(pix).getRgbF()
        if color[3] == 1:
            moy = [moy[0]+color[0], moy[1]+color[1], moy[2]+color[2]]
            n += 1.0
    moy = [moy[0]/n*255, moy[1]/n*255, moy[2]/n*255]
    color = QtGui.QColor(moy[0], moy[1], moy[2]).name()
    return chemin, color


def ExeScript(script, textEdit=None, env=None, line_offset=0):
    """Execute a script and redirect the output
    to a text widget if provided.

    Parameters:
        script (str): the script to execute.
        textEdit (QWidget): the text widget to redirect the output to.
        line_offset (int): if an error occured, offset the line number
            with this value.
    """
    tmpfile = tempfile.NamedTemporaryFile("w", suffix='.py', delete=False)
    tmpfile.write(script)
    tmpfile.close()
    cmd = ["python", "-u", tmpfile.name]
    try:
        def execute(command):
            if not sys.platform.startswith('win'):
                popen = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         universal_newlines=True, stderr=subprocess.PIPE,
                                         preexec_fn=os.setpgrp, env=env)
            else:
                for x in env:
                    v = env[x]
                    del env[x]
                    env[x.encode('utf-8')] = v.encode('utf-8')
                popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         universal_newlines=True, stderr=subprocess.PIPE,
                                         env=env)
            yield 2, popen
            for stdout_line in iter(popen.stdout.readline, ""):
                yield 0, stdout_line
            for stderr_line in iter(popen.stderr.readline, ""):
                yield 1, stderr_line
            popen.stdout.close()
            popen.stderr.close()
            popen.wait()

        for i, output_text in execute(cmd):
            if isinstance(output_text, string_types):
                if not textEdit:
                    if i == 0:
                        print(output_text[:-1], file=sys.__stderr__)
                    else:
                        print(output_text[:-1], file=sys.__stderr__)
                else:
                    if i == 0:
                        textEdit.append('<font color="grey">' + output_text + '</font>')
                    else:
                        output_text = re.sub('(?!line) \d+(?=,)', lambda x: `int(x.group()) - line_offset`, output_text)
                        textEdit.append('<font color="red">' + output_text + '</font>')
            else:
                if textEdit:
                    textEdit.process = output_text
    finally:
        os.remove(tmpfile.name)


def getCurrentNode():
    """Return the current node object, or None if failed."""
    graph = getCurrentGraph()
    if not graph:
        return None
    return graph.getNode(os.getenv("MGVNODENAME"))


def getCurrentGraph():
    """Return the current graph object, or None if failed."""
    proj = getCurrentProject()
    pattern = proj.getPattern(os.getenv("MGVPATTERNNAME"))
    path = os.getenv("MGVGRAPHKEYS").split(':')
    return MgvGraph(pattern=pattern, path=path, name=pattern.convertGraphName(path))


def getCurrentProject():
    """Return the current project object, or None if failed."""
    return MgvProject.Project(name=os.getenv("MGVPROJECTNAME"))


class MgvGraphTemplate(object):
    """Mangrove GraphTemplate object.

    A template is a default graph that can be used to prefill
    new graphs created in a pattern.
    The new graph is filled at the first openning attempt,
    therefore it inherits the last modifications of the template.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the template name.
        pattern (MgvPattern): the pattern.
        icon (str): the path of an image used in the UI to
            select a template when openning a new graph.
    """
    code = "GraphTemplate"

    def __init__(self, uuid=None, pattern=None, name='Empty', icon=''):
        self.uuid = uuid
        self.pattern = pattern
        self.name = name
        self.icon = icon

    def __repr__(self):
        return "MgvGraphTemplate %s" % self.name

    def getProject(self):
        return self.pattern.project

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.pattern, self.code, name=self.name, icon=self.icon)
        path = ':'.join([self.pattern.getName(), self.getName(), '*template*'])
        mgvWrapper.createNode(self, "Graph", name=self.name, path=path, template_name='')

    def getName(self):
        """Return the name of the template."""
        return self.name

    def getIcon(self):
        """Return the icon path of the template."""
        return self.icon

    def setName(self, name):
        """Set the name of the template."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def setIcon(self, icon):
        """Return the icon path of the template."""
        self.icon = icon
        mgvWrapper.setNodeAttr(self, icon=icon)

    def _dup(self):
        """Return a new template with the same attributes."""
        new = MgvGraphTemplate(pattern=self.pattern, uuid=self.uuid, name=self.name, icon=self.icon)
        return new

    def getJson(self):
        """Return a dictionary representing the template."""
        return {'code': 'GraphTemplate', 'uuid': self.uuid, 'name': self.name, 'icon': self.icon}


class MgvPattern(object):
    """Mangrove Pattern object.

    A pattern is a class of Mangrove graphs.
    It is used to separate graphs in categories and to specify the path
    of each graph data.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the pattern name.
        project (MgvProject): the project.
        pattern (str): the path of the graphs in this pattern.
        graph_name (str): the name of the graphs in this pattern.
        order (int): used to organize the display order
            of the project patterns.
        templates (list of MgvGraphTemplate): list of available templates
            for this pattern.

    Example of pattern attribute:
        /path/project/Shots/${0}/${0}_${1}
        In this pattern, we design two keys, ${0} and ${1} used
        arbitrary here as sequence and shot. The data of a graph with
        sequence "0100" and shot "1580" will be stored in the folder :
        /path/project/Shots/0100/0100_1580

        Number of keys are not limited and has to be written
        in this format : ${number}
    """
    code = "Pattern"

    def __init__(self, project=None, uuid=None, name='', pattern='/path/${0}/${0}_${1}', graph_name='${0}_${1}',
                 templates=None, order=0):
        self.uuid = uuid
        self.project = project
        self.name = name
        self.pattern = pattern
        self.graph_name = graph_name
        self.order = order
        self.templates = templates if templates is not None else []
        for t in self.templates:
            t.pattern = self

    def __repr__(self):
        return "MgvPattern %s" % self.name

    def getProject(self):
        return self.project

    def create(self):
        """Create the equivalent object in the database.
        Also create templates objects if any.
        """
        self.uuid = mgvWrapper.createNode(self.project, self.code, name=self.name, pattern=self.pattern,
                                          graph_name=self.graph_name, order=self.order)
        for template in self.templates:
            template.create()

    def getName(self):
        """Return the name of the pattern."""
        return self.name

    def setName(self, name):
        """Set the name of the pattern."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def getPattern(self):
        """Return the pattern attribute of the pattern."""
        return self.pattern

    def setPattern(self, pattern):
        """Set the pattern attribute of the pattern."""
        self.pattern = pattern
        mgvWrapper.setNodeAttr(self, pattern=pattern)

    def getGraphName(self):
        """Return the graph_name attribute of the pattern."""
        return self.graph_name

    def setGraphName(self, graph_name):
        """Set the graph_name attribute of the pattern."""
        self.graph_name = graph_name
        mgvWrapper.setNodeAttr(self, graph_name=graph_name)

    def setOrder(self, order):
        """Set the order of the pattern."""
        self.order = order
        mgvWrapper.setNodeAttr(self, order=order)

    def getGraphs(self):
        """Return a dictionary of the graphs with this pattern,
        organized by keys.
        """
        paths = mgvWrapper.getPatternGraphs(self)
        dico = {}
        for path in paths:
            d = dico
            for key in path[:-1]:
                if key not in d:
                    d[key] = {}
                d = d[key]
            d[path[-1]] = path
        return dico

    def graphExists(self, keys):
        """Check if a graph exists in the database.

        Parameters:
            keys (list of str): the graph path from the pattern name
                                     to the last key.
        Return:
            bool: True if the graph exists.
        """
        return mgvWrapper.graphExists(self, keys)

    def convertPath(self, keys):
        """Return the pattern attribute with keys replaced
        by the values provided.
        """
        path = self.pattern
        for i, key in enumerate(keys):
            path = path.replace("${%s}" % i, key)
        return path

    def convertGraphName(self, keys):
        """Return the pattern attribute with keys replaced
        by the values provided.
        """
        name = self.graph_name
        for i, key in enumerate(keys):
            name = name.replace("${%s}" % i, key)
        return name

    def getGraphInfo(self, keys):
        """Get a graph details from its path.

        Parameters:
            keys (list of str): path of the graph from the pattern name to its name.
        Returns
            dict: a dictionary with a uuid value and a template_name value.
        """
        return mgvWrapper.getGraphInfo(self, keys)

    def setGraphTemplate(self, keys, template_name):
        gid = self.getGraphInfo(keys)['uuid']
        mgvWrapper.setNodeAttr({'code': 'Graph', 'uuid': gid, 'project_name': self.project.name},
                               template_name=template_name)

    def deleteGraph(self, keys):
        """Delete a graph in the database and all its hierarchy."""
        mgvWrapper.deleteGraph(self, keys)

    def _dup(self):
        """Return a new pattern with the same attributes."""
        new = MgvPattern(project=self.project, uuid=self.uuid, name=self.name, pattern=self.pattern, order=self.order,
                         graph_name=self.graph_name, templates=[x._dup() for x in self.templates])
        return new

    def getJson(self):
        """Return a dictionary representing the pattern."""
        return {'code': 'Pattern', 'uuid': self.uuid, 'name': self.name, 'pattern': self.pattern, 'order': self.order,
                'templates': [x.getJson() for x in self.templates],
                'graph_name': self.graph_name}


class MgvContext(object):
    """Mangrove Context object.

    A context is attached to a project and store a set of variables and
    their values. Those variables will be set as environment variables
    before a node's execution. Each type of node can specify which
    context to use.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the name of the context.
        value (str): a multiline string.

    Example of value attribute:
        val1=/path/file.ext
        SOFT_VERSION=10.5
    """
    code = "Context"

    def __init__(self, uuid=None, project=None, name='', value=''):
        self.uuid = uuid
        self.project = project
        self.name = name
        self.value = value

    def getProject(self):
        return self.project

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.project, self.code, name=self.name, value=self.value)

    def setName(self, name):
        """Set the name of the context."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def setValue(self, value):
        """Set the value of the context."""
        self.value = value
        mgvWrapper.setNodeAttr(self, value=value)

    def getName(self):
        """Return the name of the context."""
        return self.name

    def getValue(self):
        """Return the value of the context."""
        return self.value

    def _dup(self):
        """Return a new context with the same attributes."""
        return MgvContext(uuid=self.uuid, name=self.name, value=self.value)

    def getJson(self):
        """Return a dictionary representing the context."""
        return {'code': 'Context', 'uuid': self.uuid, 'name': self.getName(), 'value': self.value}


class MgvHud(object):
    """Mangrove Hud object.

    A hud is a script that is executed in a parallel thread at a
    specific event. The script should returns a value displayed in a
    graph Mangrove UI. The script can use the opened graph environment
    vars such as MGVGRAPHNAME.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the name of the hud.
        script (str): the script of the hud.
            This script should return a list of strings.
        event (str): when to execute the script. It can be,
            open: when the graph is opened.
            select: when the selection changes.
            refresh: when the grah is refreshed.
            toggle: when the hud box is toggled.
    """
    code = "Hud"

    def __init__(self, uuid=None, project=None, name='', script='return []', event='open'):
        self.uuid = uuid
        self.project = project
        self.name = name
        self.script = script
        self.event = event

    def getProject(self):
        return self.project

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.project, self.code, name=self.name, script=self.script, event=self.event)

    def setName(self, name):
        """Set the name of the hud."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def setScript(self, script):
        """Set the script of the hud."""
        self.script = script
        mgvWrapper.setNodeAttr(self, script=script)

    def setEvent(self, event):
        """Set the event of the hud."""
        self.event = event
        mgvWrapper.setNodeAttr(self, event=event)

    def getName(self):
        """Return the name of the hud."""
        return self.name

    def getScript(self):
        """Return the script of the hud."""
        return self.script

    def getEvent(self):
        """Return the event of the hud."""
        return self.event

    def _dup(self):
        """Return a new hud with the same attributes."""
        return MgvHud(uuid=self.uuid, name=self.name, script=self.script, event=self.event, project=self.project)

    @classmethod
    def getFromJson(cls, element):
        """Create a hud from a dictionary."""
        return cls(uuid=None, name=element['name'], script=element['script'], event=element['event'])

    def getJson(self):
        """Return a dictionary representing the hud."""
        return {'code': 'Hud', 'uuid': self.uuid, 'name': self.getName(), 'script': self.script, 'event': self.event}


class MgvProject(object):
    """Mangrove Project object.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the name of the project.
        types (list of MgvType): available types for this project.
        patterns (list of MgvPattern): patterns of this project.
        contexts (list of MgvContext): contexts of this project.
        huds (list of MgvHud): huds of this project.
        script (str): the first part of every node's execution
            python script.
        batchScripts (dict): a list of MgvBatchScript.
        versions_padding (int): padding of the versions of a node.
        versions_start (int): number of the first version of a node.
    """
    code = "Project"

    def __init__(self, uuid=None, name='', patterns=None, types=None, contexts=None, huds=None, script='',
                 batchScripts=None, versions_padding=3, versions_start=1):
        self.uuid = uuid
        self.name = name
        self.types = types if types is not None else []
        self.patterns = patterns if patterns is not None else []
        self.contexts = contexts if contexts is not None else []
        self.huds = huds if huds is not None else []
        self.script = script
        self.batchScripts = batchScripts if batchScripts is not None else []
        for x in self.patterns + self.contexts + self.huds + self.types:
            x.project = self
        self.versions_padding = versions_padding
        self.versions_start = versions_start

        for pattern in self.patterns:
            pattern.project = self
        for batchScript in self.batchScripts:
            batchScript.project = self

    def __repr__(self):
        return "MgvProject %s" % self.name

    def getProject(self):
        return self

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(None, self.code, name=self.name, script=self.script, lock='',
                                          versions_padding=self.versions_padding, versions_start=self.versions_start)
        for batch in self.batchScripts:
            batch.create()
        for pattern in self.patterns:
            pattern.create()

    def lock(self, user):
        """Try to lock the project to prevent conflictual modifications.

        Parameters:
            user (str): the current user name.
        Return:
            str: The current user name if the project was free,
                 else the user who locked the project.
        """
        return mgvWrapper.lockProject(self, user)

    def unlock(self):
        """Force unlock the project."""
        mgvWrapper.unlockProject(self)

    def getName(self):
        """Return the name of the project."""
        return self.name

    def getContexts(self):
        """Return a list of the contexts of the project."""
        return list(self.contexts)

    def getHuds(self):
        """Return a list of the huds of the project."""
        return list(self.huds)

    def setHuds(self, huds):
        """Delete the project huds and add new ones."""
        for hud in self.huds:
            mgvWrapper.deleteNode(hud)
        self.huds = huds
        for hud in huds:
            hud.create()

    def setName(self, name):
        """Set the name of the project."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def setVersionsPadding(self, versions_padding):
        """Set the padding of the node versions of the project."""
        self.versions_padding = versions_padding
        mgvWrapper.setNodeAttr(self, versions_padding=versions_padding)

    def setVersionsStart(self, versions_start):
        """Set the first version number of the nodes of the project."""
        self.versions_start = versions_start
        mgvWrapper.setNodeAttr(self, versions_start=versions_start)

    def getVersionsPadding(self):
        """Return the padding of the node versions of the project."""
        return self.versions_padding

    def getVersionsStart(self):
        """Return the first version number of the nodes of the project."""
        return self.versions_start

    def setScript(self, script):
        """Set the script of the project."""
        self.script = script
        mgvWrapper.setNodeAttr(self, script=script)

    def getScript(self):
        """Return the script of the project."""
        return self.script

    def getTypes(self):
        """Return a list of the types of the project."""
        return list(self.types)

    def getPatterns(self):
        """Return a list of the patterns of the project."""
        return list(self.patterns)

    def getPattern(self, name):
        """Return a pattern of the project."""
        if name in [x.getName() for x in self.patterns]:
            return [x for x in self.patterns if x.getName() == name][0]
        return None

    @staticmethod
    def Project(name):
        """Get a project object from its name."""
        return mgvWrapper.getProject(name)

    def _dup(self):
        """Return a new project with the same attributes."""
        return MgvProject(name=self.name, uuid=self.uuid, script=self.script, types=[x._dup() for x in self.types],
                          patterns=[x._dup() for x in self.patterns], contexts=[x._dup() for x in self.contexts],
                          huds=[x._dup() for x in self.huds], batchScripts=[x._dup() for x in self.batchScripts],
                          versions_padding=self.versions_padding, versions_start=self.versions_start)

    def readTypes(self):
        """Read or refresh the types of the project."""
        self.types = mgvWrapper.getTypes(self.getName())
        for t in self.types:
            t.project = self

    def readType(self, uuid):
        """Get a type of this project by its uuid."""
        t = mgvWrapper.getType(self.getName(), uuid=uuid)
        t.project = self
        return t

    def delete(self):
        """Delete the database object of this project
        and all its hierarchy.
        """
        mgvWrapper.deleteNode(self)

    def getJson(self):
        """Return a dictionary representing the project."""
        return {'code': 'Project', 'name': self.getName(), 'script': self.script,
                'batchScripts': [x.getJson() for x in self.batchScripts],
                'patterns': [x.getJson() for x in self.patterns], 'huds': [x.getJson() for x in self.huds],
                'contexts': [x.getJson() for x in self.contexts], 'lock': '', 'versions_padding': self.versions_padding,
                'versions_start': self.versions_start}


class MgvGraph(object):
    """Mangrove Graph object.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the name of the graph.
        pattern (MgvPattern): the pattern of the graph.
        template_name (str): the name of the template to use
            at first opening.
        path (list of str): the keys of the graph.
        nodes (list of MgvNode): the nodes of the graph.
        groups (list of MgvGroup): the groups of the graph.
        user (str): a code composed with the current user name
            and a random number separated by "$".
            The random number is used to differenciate
            multiple mangrove sessions with the same user.
        variables (list of MgvVariables): variables of the graph.
    """
    code = "Graph"

    def __init__(self, pattern=None, path=None, uuid=None, template_name='', name='', load=True):
        self.uuid = uuid
        self.pattern = pattern
        self.template_name = template_name
        self.path = path if path is not None else []
        self.nodes = []
        self.groups = []
        self.name = name
        user = os.getenv('USER')
        if not user:
            user = os.getenv("USERNAME")
        self.user = "%s$%s" % (user, int(random.random() * 10000000000))
        self.variables = []

        if load:
            self.refresh()
        else:
            d = mgvWrapper.getGraphInfo(self.pattern, self.path)
            if 'uuid' in d.keys():
                self.uuid = d['uuid']
                self.template_name = d['template_name']

    def __repr__(self):
        return "MgvGraph %s" % self.name

    def getProject(self):
        return self.pattern.project

    def create(self):
        """Create the equivalent object in the database
        Also create node, group and variable objects if any.
        """
        self.uuid = mgvWrapper.createNode(self.pattern, 'Graph', path=':'.join(self.path), name=self.name,
                                          template_name=self.template_name)
        for node in self.nodes:
            node.create()
        for node in self.nodes:
            mgvWrapper.setNodeAttr(node, inputLinks=';'.join([x.linkfrom.uuid for x in node.inputLinks]))
        for group in self.groups:
            group.create()
        for variable in self.variables:
            variable.create()

    def getVars(self):
        """Return a dictionary of the env variables of this graph."""
        dico = {"MGVPROJECTNAME": self.pattern.project.getName(),
                "MGVPATTERNNAME": self.pattern.getName(),
                "MGVGRAPHPATH": self.getWorkDirectory(),
                "MGVGRAPHKEYS": ':'.join(self.path) if
                not isinstance(self.path, string_types) else os.path.splitext(self.path)[0],
                "MGVGRAPHNAME": self.getName(),
                "MGVGRAPHFILEPATH": self.getFilePath()}
        if not isinstance(self.path, string_types):
            for i, key in enumerate(self.path):
                dico['KEY%s' % i] = str(key)
        for var in self.variables:
            if var.active:
                dico[var.name] = str(var.value)
        dico = mgvDicoReplace(dico)
        return dico

    def _fillWithGraphTemplate(self, template):
        """Replace all components of this graph by the templates's."""
        template_graph = MgvGraph(pattern=template.pattern,
                                  path=[template.pattern.getName(), template.getName(), '*template*'], name=template.getName())
        self.nodes = [x._dup(self) for x in template_graph.nodes]
        self.groups = [x._dup(self) for x in template_graph.groups]
        for v in template_graph.variables:
            if v.name not in [x.name for x in self.variables]:
                new_variable = v._dup()
                self.variables.append(new_variable)
                new_variable.parent = self
                new_variable.create()
        for node in self.nodes:
            node.create()
        for group in self.groups:
            group.create()
        self._linksFromString()

    def setEnv(self, name, value):
        """Set a new environment variable for this graph."""
        for v in self.variables:
            if v.name == name:
                v.setValue(value)
                return
        var = MgvVariable(parent=self, name=name, value=value)
        self.variables.append(var)
        var.create()

    def getName(self):
        """Return the name of the graph."""
        return self.name

    def getFullName(self):
        """Return the complete path of the graph from project name
        to last key. i.e. "MyProject:Shots:0001:0001".
        """
        if isinstance(self.path, string_types):
            return os.path.splitext(self.path)[0]
        return ':'.join([self.pattern.project.getName(), self.pattern.getName()]+self.path)

    def setName(self, name):
        """Set the name of the graph."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def getPath(self):
        """Return the keys of the graph.
        """
        if isinstance(self.path, string_types):
            return self.path
        return list(self.path)

    def getWorkDirectory(self):
        """Return the directory of the graph by filling the pattern
        with its keys.
        """
        if isinstance(self.path, string_types):
            return os.path.dirname(self.path)
        if not len(self.path):
            return ''
        return self.pattern.convertPath(self.path)

    def getFilePath(self):
        """Return the path of the mgv file corresponding to the graph,
        in case of no database server is used.
        """
        if isinstance(self.path, string_types):
            return self.path
        path = os.path.join(self.pattern.convertPath(self.path), self.name) + '.mgv'
        return path

    def getVariables(self):
        """Return a list of the variables of the graph."""
        return list(self.variables)

    def getGroups(self):
        """Return a list of the groups of the graph."""
        return list(self.groups)

    def getUser(self):
        """Return the user of the graph."""
        return self.user

    def getNode(self, name):
        """Return a node from its name."""
        for searchingnode in self.nodes:
            if searchingnode.name == name:
                return searchingnode
        return None

    def getNodes(self, name="", type=""):
        """Return graph nodes.

        Examples:
            getNodes()
            getNodes(name="toto")
            getNodes(type="render*")
            getNodes(name="toto*", type="render*")
        """
        if not len(name) and not len(type):
            return list(self.nodes)
        name = name.replace('*', '.*').lower()
        type = type.replace('*', '.*').lower()
        n = []
        for searchingnode in self.nodes:
            if re.match(name, searchingnode.getName().lower()) and\
                    re.match(type, searchingnode.getType().getName().lower()):
                n.append(searchingnode)
        return n

    def _linksToString(self, graphview=None):
        """Replace links between nodes from link objects with
        string name references.
        """
        links = []
        for node in self.nodes:
            links.extend([x for x in node.inputLinks if not isinstance(x, string_types)])
            links.extend([x for x in node.outputLinks if not isinstance(x, string_types)])
            node.inputLinks = [x.linkfrom.uuid if not isinstance(x, string_types) else x for x in node.inputLinks]
            node.outputLinks = [x.linkto.uuid if not isinstance(x, string_types) else x for x in node.outputLinks]
        for link in links:
            if link.item:
                link.item.prepareGeometryChange()
                graphview.scene.removeItem(link.item)
                link.item = None
        if graphview:
            for editor in graphview.editors:
                if isinstance(editor.node, MgvNode):
                    editor.node = editor.node.getName()

    def _linksFromString(self, graphview=None):
        """Replace links from string name references to
        link objects.
        """
        for node in self.nodes:
            for link in list(node.inputLinks):
                if isinstance(link, string_types):
                    found = False
                    for source in self.nodes:
                        if source.uuid == link:
                            MgvLink(source, node)
                            found = True
                            break
                    if not found:
                        node.inputLinks.remove(link)
            for link in list(node.outputLinks):
                if isinstance(link, string_types):
                    found = False
                    for dest in self.nodes:
                        if dest.uuid == link:
                            MgvLink(node, dest)
                            found = True
                            break
                    if not found:
                        node.outputLinks.remove(link)
        if graphview:
            for editor in graphview.editors:
                if isinstance(editor.node, string_types):
                    node = self.getNode(editor.node)
                    if node:
                        editor.node = node
                        editor.checkEditable()
                    else:
                        editor.close()

    def _saveState(self, node_version):
        """Create a snapshot of the graph as a .exe_state file
        in the graph root directory.
        """
        pad = node_version.node.graph.pattern.project.versions_padding
        path = os.path.join(node_version.node.getPath(), ".exec_state_v"+str(node_version.id).zfill(pad))
        rep = os.path.dirname(path)
        if not os.path.exists(rep):
            try:
                os.makedirs(rep)
            except (IOError, OSError):
                print("Can't create %s !" % rep, file=sys.__stderr__)
                if node_version.node.item:
                    node_version.node.item.graphview.gui.notify("Can't create %s !" % rep, 1)
        root = self.getJson()
        root["name"] = self.getName()+"_View"
        for n in root['nodes']:
            n['user'] = '*locked*'

        lines = json.dumps(root, sort_keys=True, indent=4)
        try:
            with open(path, "w") as fid:
                fid.writelines(lines)
        except (IOError, OSError):
            print("Can't create %s !" % path, file=sys.__stderr__)
            if node_version.node.item:
                node_version.node.item.graphview.gui.notify("Can't create %s !" % path, 1)

    def forceNodes(self, nodes, port):
        """Asks to another Mangrove instance to free a node,
        force lock without response.
        """
        toforceOk = []
        replyDico = {}
        for node in nodes:
            add = True
            if len(node.port):
                toaddress, toport = node.port.split(':')
                if not node.port == port:
                    code = "%s:%s" % (toaddress, toport)
                    if code in replyDico:
                        response = replyDico[code]
                    else:
                        response = unlock_request(toaddress, toport, self.getWorkDirectory(), node.getName(), self.getUser(),
                                                  port)
                        replyDico[code] = response
                    if response:
                        if response not in ['noroute', 'notmine']:
                            if node.item:
                                node.item.graphview.gui.requested(node.name, toaddress, toport)
                            add = False
                        else:
                            if not node.item:
                                add = False
            if add:
                toforceOk.append(node)
        return toforceOk

    def refresh(self, graphview=None):
        """Reload all nodes, variables and groups from the database."""
        # On charge la DB de ce graph
        if not isinstance(self.path, string_types):
            root = mgvWrapper.getObjects(self)
            if root is None:
                return
        else:
            with open(self.path, 'r') as fid:
                root = json.load(fid)
        self.uuid = root['uuid']
        if 'template_name' in root:
            self.template_name = root['template_name']
        self._linksToString(graphview)
        # on degage de la scene les nodes pas a nous
        for node in list(self.nodes):
            if node.getUser() != self.user:
                up = mgvWrapper.getNodeAttr(node, "updated")
                if not up or up > node.updated:
                    self.nodes.remove(node)
                    if graphview:
                        node.item.prepareGeometryChange()
                        graphview.scene.removeItem(node.item)
                        for editor in graphview.editors:
                            if editor.node is node:
                                editor.node = node.getName()

        # on ajoute dans la scene les nodes pas a nous
        for element in root['nodes']:
            if element['uuid'] not in [x.uuid for x in self.nodes]:
                MgvNode.getFromJson(element, self)
        # on delete les groupes et les envs
        for group in self.groups:
            if graphview:
                group.item.prepareGeometryChange()
                graphview.scene.removeItem(group.item)
        self.groups = []
        self.variables = []
        # on recupere les groupes et les envs
        for element in root['variables']:
            MgvVariable.getFromJson(element, self)
        for element in root['groups']:
                MgvGroup.getFromJson(element, self)
        self._linksFromString(graphview)

    def getJson(self):
        """Return a dictionary representing the graph."""
        return {'code': 'Graph', 'name': self.getName(), 'path': self.path,
                'template_name': self.template_name, 'nodes': [x.getJson() for x in self.nodes], 'uuid': str(self.uuid),
                'groups': [x.getJson() for x in self.groups], 'variables': [x.getJson() for x in self.variables]}

    @classmethod
    def getFromJson(cls, element, pattern):
        """Create a node from a dictionary."""
        newGraph = cls(uuid=element['uuid'], pattern=pattern, path=element['path'], template_name=element['template_name'],
                       name=element['name'], load=False)
        for childElement in element['variables']:
            MgvVariable.getFromJson(childElement, newGraph)
        for childElement in element['groups']:
            MgvGroup.getFromJson(childElement, newGraph)
        for childElement in element['nodes']:
            MgvNode.getFromJson(childElement, newGraph)

        return newGraph

    def _close(self):
        """Free all nodes."""
        for node in self.nodes:
            if node.getUser() == self.getUser():
                if node.getUser() != "*locked*":
                    node.setUser('free')


class MgvLink(object):
    """Mangrove Link object.
    This object doesn't have a representation object in the database,
    since links a converted to node uuids in the node attributes.

    Attributes:
        linkfrom (MgvNode): source node.
        linkto (MgvNode): destination node.
    """
    def __init__(self, linkfrom, linkto):
        self.linkfrom = linkfrom
        self.linkto = linkto
        self.item = None
        self.linkto._ungotvar()
        found = 0
        for n, output in enumerate(self.linkfrom.outputLinks):
            if isinstance(output, string_types):
                if output == self.linkto.name or output == self.linkto.uuid:
                    self.linkfrom.outputLinks[n] = self
                    found = 1
        if found == 0:
            self.linkfrom.outputLinks.append(self)
        found = 0
        for n, inpt in enumerate(self.linkto.inputLinks):
            if isinstance(inpt, string_types):
                if inpt == self.linkfrom.name or inpt == self.linkfrom.uuid:
                    self.linkto.inputLinks[n] = self
                    found = 1
        if found == 0:
            self.linkto.inputLinks.append(self)

    def __repr__(self):
        return "MgvLink"

    def getProject(self):
        return self.linkfrom.getProject()

    def delete(self):
        """Delete the link."""
        self.linkto._ungotvar()
        if self in self.linkto.inputLinks:
            self.linkto.inputLinks.remove(self)
            mgvWrapper.setNodeAttr(self.linkto, inputLinks=';'.join([x.linkfrom.uuid for x in self.linkto.inputLinks]))
            mgvWrapper.setNodeAttr(self.linkto, updated=time.time())
            self.linkto.updated = time.time()
            mgvWrapper.deleteLink(self.linkfrom, self.linkto)
        if self in self.linkfrom.outputLinks:
            self.linkfrom.outputLinks.remove(self)
        if self.item:
            self.item.delete()


class MgvGroup(object):
    """Mangrove Group object.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the name of the group.
        graph (MgvGraph): the graph of the group.
        nodeuuids (list of str): uuids of the nodes in the group.
        color (str): color of the group, i.e. #FF0000
    """
    code = "Group"

    def __init__(self, uuid=None, graph=None, name="Group", color="#3366BB", nodeuuids=None):
        self.uuid = uuid
        self.item = None
        self.graph = graph
        self.name = name
        self.nodeuuids = nodeuuids if nodeuuids is not None else []
        self.color = color
        self.graph.groups.append(self)

    def getProject(self):
        return self.graph.getProject()

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.graph, self.code, name=self.name, nodeuuids=';'.join(self.nodeuuids),
                                          color=self.color)

    def getNodes(self):
        """Return a list of the nodes of the group."""
        nodes = []
        for node in self.graph.nodes:
            if node.uuid in self.nodeuuids:
                nodes.append(node)
        return nodes

    def addNodes(self, nodes):
        """Add nodes to the group."""
        self.nodeuuids.extend([x.uuid for x in nodes])
        mgvWrapper.setNodeAttr(self, nodeuuids=';'.join(self.nodeuuids))

    def removeNodes(self, nodes):
        """Remove nodes from the group."""
        for node in nodes:
            if node.uuid in self.nodeuuids:
                self.nodeuuids.remove(node.uuid)
                mgvWrapper.setNodeAttr(self, nodeuuids=';'.join(self.nodeuuids))

    def getColor(self):
        """Return the color of the group."""
        return self.color

    def setColor(self, color):
        """Set the color of the group."""
        self.color = color
        mgvWrapper.setNodeAttr(self, color=self.color)

    def setName(self, name):
        """Set the name of the group."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def getName(self):
        """Return the name of the group."""
        return self.name

    def delete(self):
        """Delete the group."""
        self.graph.groups.remove(self)
        mgvWrapper.deleteNode(self)

    def _dup(self, graph):
        """Return a new graph with the same attributes."""
        return MgvGroup(graph=graph, name=self.name, color=self.color, nodeuuids=list(self.nodeuuids))

    @classmethod
    def getFromJson(cls, element, graph):
        """Create a group from a dictionary."""
        new_group = cls(uuid=element['uuid'], graph=graph, name=element['name'], color=element['color'],
                        nodeuuids=element['nodeuuids'].split(';'))
        graph.groups.append(new_group)
        return new_group

    def getJson(self):
        """Return a dictionary representing the group."""
        return {'code': 'Group', 'name': self.getName(), 'color': self.color, 'nodeuuids': ';'.join(self.nodeuuids),
                'uuid': str(self.uuid)}


class MgvNode(object):
    """Mangrove Node object.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the name of the node.
        graph (MgvGraph): the graph of the node.
        type (MgvType): the type of the node.
        versions (list of MgvNodeVersion): the versions of the node.
        versionActive (MgvNodeVersion): the active version of the node.
            Can be an int in the __init__ function.
        posx (float): the x coordinate of the node.
        posy (float): the y coordinate of the node.
        user (str): a code composed with the name of the user who
            has protected the node and a random number separated by "$".
            The random number is used to differenciate
            multiple mangrove sessions with the same user.
            If the node is free, this value equals "free".
        inputLinks (list of MgvLink): input links.
        outputLinks (list of MgvLink): output links.
        port (str): the address and port of the user who has protected
            the node. i.e. "192.168.0.123:10000"
    """
    code = "Node"

    def __init__(self, graph=None, uuid=None, type='None', name='Noname', inputLinks=None, outputLinks=None,
                 versions=None, versionActive=None, data=None):
        self.uuid = uuid
        self.item = None
        self.graph = graph
        self.type = type
        self.type_name = None
        self.posx = 0
        self.posy = 0
        self.user = graph.user
        self.inputLinks = inputLinks if inputLinks is not None else []
        self.outputLinks = outputLinks if outputLinks is not None else []
        self.versions = versions if versions is not None else []
        self.data = data if data is not None else {}
        self.port = ''
        self.isRunning = False
        self.updated = time.time()

        # Check for duplicate names and rename if necessary ###################
        liste = [x.name for x in self.graph.nodes if x is not self]
        base = name
        i = ''
        while base[-1].isdigit():
            i = base[-1] + i
            base = base[:-1]
        i = int(i) if len(i) else 1
        while name in liste:
            i += 1
            name = '%s%s' % (base, i)
        self.name = name
        #######################################################################
        # If the given type is a name, searching for a type matching this name.
        if isinstance(type, string_types):
            found = None
            for searchingtype in self.graph.pattern.project.types:
                if searchingtype.name == type:
                    found = searchingtype
                    break
            self.type = found
            self.type_name = type
        #######################################################################

        for v in self.versions:
            v.node = self
        self.versionActive = versionActive
        if not len(self.versions):
            v = MgvNodeVersion(node=self)
            self.versions.append(v)
        if versionActive is None:
            self.versionActive = self.versions[-1]
        else:
            if isinstance(versionActive, string_types):
                versionActive = int(versionActive)
            if isinstance(versionActive, int):
                vs = [x for x in self.versions if x.id == versionActive]
                if len(vs):
                    self.versionActive = vs[0]
                else:
                    self.versionActive = self.versions[-1]
        self.graph.nodes.append(self)

    def __repr__(self):
        return "MgvNode %s" % self.name

    def getProject(self):
        return self.graph.getProject()

    def create(self):
        """Create the equivalent object in the database. Also create
        version objects if any, and the directory of the node if a
        typeFile exists in the type.
        """
        inputlinks = ';'.join([x if isinstance(x, string_types) else x.linkfrom.uuid for x in self.inputLinks])
        self.uuid = mgvWrapper.createNode(self.graph, self.code, name=self.name, typeName=self.type.getName(),
                                          typeUuid=self.type.uuid, posx=self.posx, posy=self.posy, user=self.user,
                                          port=self.port, inputLinks=inputlinks,
                                          versionActive=self.versionActive.getId(), output='', updated=time.time())
        self.updated = time.time()
        for v in self.versions:
            v.create()
        for data in self.data.keys():
            self.setData(data, self.data[data])
        if len(self.type.typeFiles):
            rep = self.getPath()
            if '*template*' not in rep and not os.path.exists(rep):
                try:
                    os.makedirs(rep)
                except (IOError, OSError):
                    print("Can't create %s !" % rep, file=sys.__stderr__)
                    if self.item:
                        self.item.graphview.gui.notify("Can't create %s !" % rep, 1)

    def free(self):
        """Free the node."""
        if self.user == self.graph.user:
            self.setUser(user='free')
            return True
        return False

    def catch(self):
        """Return True if the node is protectable."""
        if self.user == self.graph.user:
            return True
        if self.user == "free":
            return True
        return False

    def setParameter(self, key, value):
        """Set a parameter value on the active version of the node."""
        self.versionActive.setParameter(key, value)

    def getParameter(self, key):
        """Return a parameter value on the active version of the node."""
        self.versionActive.getParameter(key)

    def setData(self, name, value):
        """Set a data value."""
        if not isinstance(value, string_types):
            value = str(value)
        self.data[name] = value
        mgvWrapper.setDictionary(self, "Data", name, value)
        mgvWrapper.setNodeAttr(self, updated=time.time())
        self.updated = time.time()

    def getData(self, name):
        """Return a data value."""
        if name in self.data:
            return self.data[name]
        return None

    def removeData(self, name):
        """Remove a data."""
        if name in self.data:
            del self.data[name]
        mgvWrapper.removeData("Variable", self.uuid, name)
        mgvWrapper.setNodeAttr(self, updated=time.time())
        self.updated = time.time()

    def getAllData(self):
        """Return a copy of the data dictionary."""
        return dict(self.data)

    def _gotvar(self):
        """Lock the values of mangrove environment vars.
        Internally used to prevent from redundant computing.
        """
        self.versionActive._gotvar()

    def _ungotvar(self):
        """Unlock the values of mangrove environment vars."""
        self.versionActive._ungotvar()

    def getGraph(self):
        """Return the graph of the node."""
        return self.graph

    def getName(self):
        """Return the name of the node."""
        return self.name

    def getType(self):
        """Return the type of the node."""
        return self.type

    def getPath(self):
        """Return the directory of the node."""
        return os.path.join(self.graph.getWorkDirectory(), self.getName())

    def getUser(self):
        """Return the user name of the node."""
        return self.user

    def getPort(self):
        """Return the address and port of the user
        who has protected the node.
        """
        return self.port

    def setPort(self, port):
        """Set the address and port of the user
        who has protected the node.
        """
        self.port = port

    def getVersions(self):
        """Return the versions of the node."""
        return list(self.versions)

    def getVersion(self, version_id):
        """Return a specific version of the node."""
        if version_id == -1:
            return self.versionActive
        for v in self.versions:
            if v.getId() == version_id:
                return v
        return None

    def getCurrentVersion(self):
        """Return the active version of the node."""
        return self.versionActive

    def getInputNodes(self):
        """Return the input nodes."""
        return [x.linkfrom for x in self.inputLinks if not isinstance(x, string_types)]

    def getOutputNodes(self):
        """Return the output nodes."""
        return [x.linkto for x in self.outputLinks if not isinstance(x, string_types)]

    def setLinkTo(self, node):
        """Create a link from this node to the specified node."""
        link = MgvLink(self, node)
        mgvWrapper.createLink(self, node)
        mgvWrapper.setNodeAttr(node, inputLinks=';'.join([x.linkfrom.uuid for x in node.inputLinks]),
                               updated=time.time())
        node.updated = time.time()
        return link

    def getNextNodes(self):
        """Return all the output nodes, recursively."""
        nodes = [x.linkto for x in self.outputLinks]
        for link in self.outputLinks:
            nodes.extend(link.linkto.getNextNodes())
        return nodes

    def getPrevNodes(self):
        """Return all the input nodes, recursively."""
        nodes = [x.linkfrom for x in self.inputLinks]
        for link in self.inputLinks:
            nodes.extend(link.linkfrom.getPrevNodes())
        return nodes

    def getLinkedGroup(self, checknodes=None):
        """Return all nodes wich versions are connected together."""
        checknodes = checknodes if checknodes is not None else []
        nodes = []
        if self not in checknodes:
            nodes.append(self)
        for o in self.getOutputNodes():
            if o.type and o.type.uuid in self.type.linkWith:
                if o not in nodes+checknodes:
                    nodes.extend(o.getLinkedGroup(nodes+checknodes))
        for i in self.getInputNodes():
            if i.type and self.type.uuid in i.type.linkWith:
                if i not in nodes+checknodes:
                    nodes.extend(i.getLinkedGroup(nodes+checknodes))
        return nodes

    def _checkType(self):
        """Remove obsolete parameters."""
        for version in self.versions:
            for param in list(version.parameters):
                if param not in [x.name for x in self.type.getParameters(version_id=version.typeForceVersion)]:
                    del version.parameters[param]

    def _typeParameters(self):
        """Convert parameters value from string to the type of the
        parameter.
        """
        if not self.type:
            return
        for version in self.versions:
            for paramKey in version.parameters:
                param_value = version.parameters[paramKey]
                for param in self.type.getParameters(version_id=version.typeForceVersion):
                    if param.name == paramKey:
                        if param.type == "int":
                            try:
                                param_value = int(param_value)
                            except ValueError:
                                param_value = 0
                        elif param.type == "float":
                            try:
                                param_value = float(param_value)
                            except ValueError:
                                param_value = 0.0
                        elif param.type == "bool":
                            try:
                                param_value = str(param_value) in ["True", "true", "1"]
                            except ValueError:
                                param_value = False
                        break
                version.parameters[paramKey] = param_value

    def delVersion(self, version):
        """Delete a version by its id or by the version object itself."""
        if isinstance(version, int):
            if version in [x.id for x in self.versions]:
                version = [x for x in self.versions if x.id == version][0]
            else:
                return
        if version in self.versions:
            version._ungotvar()
            version.getVars()
            for typeFile in self.type.typeFiles:
                if typeFile.copy:
                    if os.path.exists(version.dico[typeFile.name]):
                        try:
                            if os.path.isdir(version.dico[typeFile.name]):
                                shutil.rmtree(version.dico[typeFile.name])
                            else:
                                os.remove(version.dico[typeFile.name])
                        except IOError:
                            if self.item:
                                self.item.graphview.gui.notify("Removing %s has failed !" % version.dico[typeFile.name],
                                                               1)
                            else:
                                print("Removing %s has failed !" % version.dico[typeFile.name], file=sys.__stderr__)
            index = self.versions.index(version)
            self.versions.remove(version)
            version.delete()
            if version == self.versionActive:
                if index < len(self.versions)-1:
                    self.setVersion(self.versions[index], propagate=True)
                elif len(self.versions):
                    self.setVersion(self.versions[-1], propagate=True)
                else:
                    v = MgvNodeVersion(node=self)
                    v.create()
                    self.versions = [v]
                    self.setVersion(v, propagate=True)

    def newVersion(self, version_id=None, propagate=True):
        """Create a new version and set it active.

        Parameters:
            version_id (int): force the new id value.
            propagate (bool): if there are nodes with connected versionning,
                              propagate or not this change.
        Return:
            MgvNodeVersion: New version object.
        """
        self._ungotvar()
        new = self.versionActive._dup()
        new.comment = "comment"
        if version_id is None:
            version_id = self.versions[-1].id + 1
        while version_id in [x.id for x in self.versions]:
            version_id += 1
        new.id = version_id
        self.versions.append(new)
        new.create()
        self.setVersion(new, propagate)
        return new

    def setVersion(self, version, propagate=True):
        """Change the active version to the version specified.

        Parameters:
            version (MgvNodeVersion or int): a version object or id of the node.
            propagate (bool): if there are nodes with connected versionning,
                              propagate or not this change.
        """
        if propagate:
            if not isinstance(version, int):
                version = version.id
            nodes = self.getLinkedGroup()
            for node in nodes:
                node.setVersion(version, propagate=False)
            return

        if isinstance(version, int):
            if version in [x.id for x in self.versions]:
                version = [x for x in self.versions if x.id == version][0]
            else:
                self.newVersion(version_id=version, propagate=False)
                return
        if version is self.versionActive:
            return

        dicoOld = {}
        for typeFile in self.type.typeFiles:
            dicoOld[typeFile.name] = self.getVars()[typeFile.name]

        self.versionActive = version
        mgvWrapper.setNodeAttr(self, versionActive=self.versionActive.getId(), updated=time.time())
        self.updated = time.time()
        self._ungotvar()

        if len(self.type.typeFiles):
            dico = self.getVars()
            for typeFile in self.type.typeFiles:
                if typeFile.copy:
                    if os.path.exists(dicoOld[typeFile.name]):
                        if not os.path.exists(dico[typeFile.name]):
                            mgvcopy(dicoOld[typeFile.name], dico[typeFile.name])

        if self.item:
            for editor in self.item.graphview.editors:
                if editor.node == self:
                    editor.readVersions()
                    editor.readValues()
                    editor.readVars()

    def setName(self, name):
        """Set the name of the node."""
        liste = [x.name for x in self.graph.nodes if x is not self]
        base = name
        i = 1
        while name in liste:
            i += 1
            name = "%s%s" % (base, i)
        self.name = name
        self._ungotvar()
        mgvWrapper.setNodeAttr(self, name=name, updated=time.time())
        self.updated = time.time()

    def setUser(self, user, port='', ip=''):
        """Change the current user of the node."""
        if len(port) and len(ip):
            port = ip+':'+port
        self.user = user
        self.port = port
        mgvWrapper.setNodeAttr(self, user=user, port=port, updated=time.time())
        self.updated = time.time()

    def setTypeForceVersion(self, i):
        """Set a specific type version to use with this node.
        Use -1 for the default one.
        """
        self.versionActive.typeForceVersion = i
        mgvWrapper.setNodeAttr(self.versionActive, typeForceVersion=i)
        mgvWrapper.setNodeAttr(self, updated=time.time())
        self.updated = time.time()

    def getTypeForceVersion(self):
        """Return the specific type version used with this node.
        Return -1 for the default one.
        """
        return self.versionActive.typeForceVersion

    def delete(self, remove_files=False):
        """Delete the node.

        Parameters:
            remove_files (bool): True to delete associated files and
                                 directories.
        """
        if remove_files:
            dico = self.getVars()
            path = dico['MGVNODEPATH']
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except (IOError, OSError):
                    if self.item:
                        self.item.graphview.gui.notify("Removing directory of %s has failed !" % self.name, 1)
                    else:
                        print("Removing directory of %s has failed !" % self.name, file=sys.__stderr__)
                    return False

        for link in list(self.outputLinks):
            if not isinstance(link, string_types):
                link.delete()
            else:
                self.outputLinks.remove(link)

        for link in list(self.inputLinks):
            if not isinstance(link, string_types):
                link.delete()
            else:
                self.inputLinks.remove(link)

        if self in self.graph.nodes:
            self.graph.nodes.remove(self)
        if self.item:
            self.item.delete()

        mgvWrapper.deleteNode(self)
        return True

    def setNodePos(self, x, y):
        """Change the coordinates of the node."""
        self.posx = x
        self.posy = y
        mgvWrapper.setNodeAttr(self, posx=x, posy=y, updated=time.time())
        self.updated = time.time()

    def getNodePos(self):
        """Return the coordinates of the node."""
        return self.posx, self.posy

    @classmethod
    def getFromJson(cls, element, graph):
        """Create a node from a dictionary."""
        nodeTypeName = element['typeName']
        nodeTypeUuid = element['typeUuid']
        nodeType = None
        if nodeTypeUuid is not None:
            for typ in graph.pattern.project.types:
                if typ.uuid == nodeTypeUuid:
                    nodeType = typ
                    break

        if nodeType is None:
            for typ in graph.pattern.project.types:
                if typ.name == nodeTypeName:
                    nodeType = typ
                    break
            else:
                nodeType = nodeTypeName

        inputLinks = element['inputLinks'].split(';') if len(element['inputLinks']) else []

        versions = []
        for childElement in element['versions']:
            versions.append(MgvNodeVersion.getFromJson(childElement))
        newNode = cls(uuid=element['uuid'], graph=graph, type=nodeType, name=element['name'], inputLinks=inputLinks,
                      outputLinks=[], versions=versions, versionActive=element['versionActive'])
        
        newNode._typeParameters()
        newNode.port = element['port']
        try:
            newNode.updated = element['updated']
        except:
            pass
        newNode.posx = element['posx']
        newNode.posy = element['posy']
        newNode.user = element['user']
        for dataKey in element['data']:
            newNode.data[dataKey] = element['data'][dataKey]

        return newNode

    def getJson(self):
        """Return a dictionary representing the node."""
        typename = '' if self.type is None else self.type.getName()
        typeuuid = '' if self.type is None else self.type.uuid
        inputLinks = ';'.join([x if isinstance(x, string_types) else x.linkfrom.uuid for x in self.inputLinks])
        return {'code': 'Node', 'name': self.name, 'user': self.user, 'path': self.getPath(),
                'port': self.port, 'uuid': str(self.uuid),
                'graphname': self.graph.name, 'data': [{'name': x, 'value': self.data[x]} for x in self.data],
                'typeName': typename, 'typeUuid': typeuuid, 'versionActive': self.versionActive.id,
                'inputLinks': inputLinks, 'posx': self.posx, 'posy': self.posy,
                'versions': [x.getJson() for x in self.versions]}

    def getInputs(self):
        """Return a list of input nodes's custom outputs converted to
        string.
        """
        mgvInputs = [mgvWrapper.getNodeAttr(x, 'output') for x in self.getInputNodes()]
        mgvInputs = [pickle.loads(x) if x else None for x in mgvInputs]
        return mgvInputs

    def exe(self, actionname=None, textEdit=None):
        """Execute the action of the node. Redirect the output to a text
        widget if provided.
        """
        self.versionActive.exe(actionname=actionname, textEdit=textEdit)

    def getVars(self):
        """Return a dictionary of Mangrove variables, the graph
        variables and the node variables.
        """
        return self.versionActive.getVars()

    def _dup(self, graph):
        """Return a new node with the same attributes."""
        node = MgvNode(graph=graph, uuid=None, type=self.type, name=self.name,
                       inputLinks=[x.linkfrom.name for x in self.inputLinks],
                       outputLinks=[x.linkto.name for x in self.outputLinks],
                       versions=[x._dup() for x in self.versions], versionActive=self.versionActive.id)
        node.posx = self.posx
        node.posy = self.posy
        return node


class MgvVariable(object):
    """Mangrove Variable object

    Attributes:
        uuid (str): unique id in the database.
        name (str): the variable name.
        active (bool): True if the variable has to be used.
        value (str): Value of the variable.
    """
    code = "Variable"

    def __init__(self, uuid=None, active=True, name="", value="", parent=None):
        self.parent = parent
        self.uuid = uuid
        self.active = active
        self.name = name
        self.value = value

    def __repr__(self):
        return "MgvVariable %s" % self.name

    def getProject(self):
        return self.parent.getProject()

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.parent, self.code, name=self.name, active=self.active, value=self.value)
        if self.parent.code == "NodeVersion":
            self.parent.node.updated = time.time()

    def getActive(self):
        """Return the active state of the variable."""
        return self.active

    def getName(self):
        """Return the name of the variable."""
        return self.name

    def getValue(self):
        """Return the value of the variable."""
        return self.value

    def setActive(self, active):
        """Set the active state of the variable."""
        self.active = active
        g = self.parent.node.graph if self.parent.code == "NodeVersion" else self.parent
        mgvWrapper.setNodeAttr(self, active=active)
        if self.parent.code == "NodeVersion":
            mgvWrapper.setNodeAttr(self.parent.node, updated=time.time())
            self.parent.node.updated = time.time()

    def setName(self, name):
        """Set the name of the variable."""
        self.name = name
        g = self.parent.node.graph if self.parent.code == "NodeVersion" else self.parent
        mgvWrapper.setNodeAttr(self, name=name)
        if self.parent.code == "NodeVersion":
            mgvWrapper.setNodeAttr(self.parent.node, updated=time.time())
            self.parent.node.updated = time.time()

    def setValue(self, value):
        """Set the value of the variable."""
        self.value = value
        g = self.parent.node.graph if self.parent.code == "NodeVersion" else self.parent
        mgvWrapper.setNodeAttr(self, value=value)
        if self.parent.code == "NodeVersion":
            mgvWrapper.setNodeAttr(self.parent.node, updated=time.time())
            self.parent.node.updated = time.time()

    def _dup(self):
        """Return a new variable with the same attributes."""
        return MgvVariable(active=self.active, name=self.name, value=self.value, parent=self.parent)

    @classmethod
    def getFromJson(cls, element, parent):
        """Create a Variable from a dictionary"""
        new_var = cls(name=element['name'], active=element['active'],
                      value=element['value'], parent=parent)
        parent.variables.append(new_var)
        return new_var

    def getJson(self):
        """Return a dictionary representing the variable."""
        return {'code': 'Variable', 'name': self.name, 'active': self.active, 'value': self.value,
                'uuid': str(self.uuid)}


class MgvNodeVersion(object):
    """Mangrove Node Version object.

    Parameters is a dictionary of modified type parameters values.
    When set to default value, the parameter is delete from this
    dictionary.
    Data is a dictionary with custom names and values,
    that you can use as you need, since Mangrove doesn't use it.
    Data will not be converted into environment vars.

    Attributes:
        uuid (str): unique id in the database.
        id (int): version id.
        comment (str): comment of the version.
        lastExec (str): last execution date with the format:
                        "%d/%m/%y %H:%M"
        lastUser (str): user who performed the last execution.
        node (MgvNode): node of the version.
        locked (bool): True if this version's editing is forbidden in
                       the UI.
        variables (list of MgvVariable): variables of the version.
        parameters (dict): dictionary of the parameters name and
                           values.
        data (dict): dictionary of the data name and values.
        typeForceVersion (int): use this specific version of the type,
                                or -1 if the default one.
    """
    code = "NodeVersion"

    def __init__(self, uuid=None, node=None, version_id=None, variables=None, parameters=None, comment="comment",
                 lastExec='', lastUser='', data=None, typeForceVersion=-1, locked=False):
        self.uuid = uuid
        self.id = version_id
        if not self.id:
            self.id = node.graph.pattern.project.versions_start if node else 0
        self.comment = comment
        self.lastExec = lastExec
        self.lastUser = lastUser
        self.node = node
        self.locked = locked
        self.variables = variables if variables is not None else []
        self.parameters = parameters if parameters is not None else {}
        self.data = data if data is not None else {}
        for v in self.variables:
            v.parent = self
        self.typeForceVersion = typeForceVersion
        self.dico = {}
        self.gotvar = False

    def __repr__(self):
        return "MgvNodeVersion %s" % self.id

    def getProject(self):
        return self.node.getProject()

    def create(self):
        """Create the equivalent object in the database.
        Also create variable, parameter and data objects if any."""
        self.uuid = mgvWrapper.createNode(self.node, self.code, id=self.id, comment=self.comment, lastExec=self.lastExec,
                                          lastUser=self.lastUser, typeForceVersion=self.typeForceVersion,
                                          locked=self.locked, updated=time.time())
        self.node.updated = time.time()
        for variable in self.variables:
            variable.create()
        for parameter in self.parameters.keys():
            self.setParameter(parameter, self.parameters[parameter])
        for data in self.data.keys():
            self.setData(data, self.data[data])

    def lock(self):
        """Lock the version from editong in the UI."""
        self.locked = True
        mgvWrapper.setNodeAttr(self, locked=True)
        mgvWrapper.setNodeAttr(self.node, updated=time.time())
        self.node.updated = time.time()

    def unlock(self):
        """Unlock the version from editong in the UI."""
        self.locked = False
        mgvWrapper.setNodeAttr(self, locked=False)
        mgvWrapper.setNodeAttr(self.node, updated=time.time())
        self.node.updated = time.time()

    def isLocked(self):
        """Return lock state of the version."""
        return self.locked

    def delete(self):
        """Delete the version in the database."""
        mgvWrapper.deleteNode(self)
        mgvWrapper.setNodeAttr(self.node, updated=time.time())
        self.node.updated = time.time()

    def _gotvar(self):
        """Lock the values of mangrove environment vars.
        Internally used to prevent from redundant computing.
        """
        self.gotvar = True

    def _ungotvar(self):
        """Unlock the values of mangrove environment vars."""
        self.gotvar = False
        for node in self.node.getOutputNodes():
            node._ungotvar()

    def setData(self, name, value):
        """Set a data value."""
        if not isinstance(value, string_types):
            value = str(value)
        self.data[name] = value
        mgvWrapper.setDictionary(self, "Data", name, value)
        mgvWrapper.setNodeAttr(self.node, updated=time.time())
        self.node.updated = time.time()

    def getData(self, name):
        """Return a data value."""
        if name in self.data:
            return self.data[name]
        return None

    def removeData(self, name):
        """Remove a data."""
        if name in self.data:
            del self.data[name]
        mgvWrapper.removeData("Variable", self.uuid, name)
        mgvWrapper.setNodeAttr(self.node, updated=time.time())
        self.node.updated = time.time()

    def getAllData(self):
        """Return a copy of the data dictionary."""
        return dict(self.data)

    def getId(self):
        """Return the id of the version."""
        return self.id

    def getComment(self):
        """Return the comment of the version."""
        return self.comment

    def setComment(self, comment):
        """Set the comment of the version."""
        self.comment = comment
        mgvWrapper.setNodeAttr(self, comment=comment)
        mgvWrapper.setNodeAttr(self.node, updated=time.time())
        self.node.updated = time.time()

    def getLastExec(self):
        """Return the last exec time of the version."""
        return self.lastExec

    def setLastExec(self, lastExec, lastUser):
        """Set the last exec time and user of the version."""
        self.lastExec = lastExec
        mgvWrapper.setNodeAttr(self, lastExec=lastExec, lastUser=lastUser)

    def getLastUser(self):
        """Return the exec user of the version."""
        return self.lastUser

    def getParameters(self):
        """Return a parameter dictionary of the version."""
        dico = {}
        for x in self.parameters:
            dico[x] = self.parameters[x]
        return dico

    def getParameter(self, name):
        """Return a parameter value of the version."""
        if name in self.parameters:
            return self.parameters[name]
        if name in [p.name for p in self.node.type.getParameters(self.node.versionActive.typeForceVersion)]:
            return self.node.type.getParameter(name, version_id=self.node.versionActive.typeForceVersion).getDefault()
        return None

    def setParameter(self, name, value):
        """Set a parameter value of the version."""
        self.node._ungotvar()
        if value != self.node.type.getParameter(name, version_id=self.node.versionActive.typeForceVersion).default:
            self.parameters[name] = value
            mgvWrapper.setDictionary(self, "Parameter", name, value)
        else:
            if name in self.parameters:
                del self.parameters[name]
                mgvWrapper.delDictionary(self, "Parameter", name)
        mgvWrapper.setNodeAttr(self.node, updated=time.time())
        self.node.updated = time.time()

    def delParameter(self, name):
        """Delete a parameter of the version."""
        self.node._ungotvar()
        if name in self.parameters:
            del self.parameters[name]
            mgvWrapper.delDictionary(self, "Parameter", name)
            mgvWrapper.setNodeAttr(self.node, updated=time.time())
            self.node.updated = time.time()

    def _dup(self):
        """Return a new nodeVersion with the same attributes."""
        self.node._ungotvar()
        return MgvNodeVersion(node=self.node, comment=self.comment, version_id=self.id,
                              variables=[x._dup() for x in self.variables], parameters=dict(self.parameters),
                              typeForceVersion=self.typeForceVersion)

    def getVars(self):
        """Return a dictionary of Mangrove variables,
        the graph variables and the node variables for this version.
        """
        if self.gotvar:
            return self.dico
        # GRAPH
        self.dico = self.node.graph.getVars()

        # NODE
        pad = self.node.graph.pattern.project.versions_padding
        self.dico["MGVNODEPATH"] = self.node.getPath()
        self.dico["MGVNODENAME"] = self.node.getName()
        self.dico["MGVNODETYPE"] = self.node.type.getName()
        self.dico["MGVNODEVERSION"] = str(self.id).zfill(pad)

        # INPUTS
        inputs_dico = {}
        for node in self.node.getInputNodes():
            for out in node.type.typeFiles:
                if out.name not in inputs_dico:
                    inputs_dico[out.name] = []
                inputs_dico[out.name].append(node.getVars()[out.name])
        inputs_keys = []
        for key in inputs_dico:
            self.dico["MGVINPUTS_%s" % key] = ';'.join(inputs_dico[key])
            inputs_keys.append(key)
        inputs_keys = list(set(inputs_keys))
        self.dico["MGVINPUTS"] = ';'.join(inputs_keys)

        # CONTEXT
        context = [x for x in self.node.graph.pattern.project.contexts if x.name == self.node.type.context]
        if len(context):
            context = context[0]
            for line in context.split('\n'):
                if '=' in line:
                    self.dico[line.split('=')[0].strip()] = line.split('=')[1].strip()

        # TYPE FILES
        for out in self.node.type.typeFiles:
            self.dico[out.name] = out.path

        # VARIABLES
        for var in self.variables:
            if var.active:
                self.dico[var.name] = str(var.value)

        # PARAMETERS
        for param in self.node.type.getParameters(version_id=self.typeForceVersion):
            v = str(self.getParameter(param.getName()))
            if param.type == 'python':
                v = "import sys\nsys.path.append('%s')\n%s" % (os.path.dirname(os.path.abspath(__file__)), v)
            self.dico[param.getName()] = str(v)

        # REPLACE VALUES
        self.dico = mgvDicoReplace(self.dico)
        self.gotvar = True
        return self.dico

    def getOutput(self):
        """Get the custom output python object,
        or return a new one if none.
        """
        out = mgvWrapper.getNodeAttr(self, 'output')
        if not out:
            dico = self.getVars()
            inputs = [x.versionActive.getOutput() for x in self.node.getInputNodes()]
            out = {'value': '', 'inputs': inputs, 'name': self.node.getName(), 'type': self.node.type.getName(),
                   'version': self.id, 'date': '', 'user': '', 'action': '', 'files': {}}
            for f in self.node.type.typeFiles:
                out['files'][f.name] = dico[f.name]
        else:
            out = pickle.loads(out)
        return out

    def compileScripts(self, action=None):
        """Compile The project head script, the type head script and the
        action script. Add Exceptions, the creation of the mgvInputs
        object and the export of the mgvOutput object at the end.
        """
        dico = self.getVars()
        files = ', '.join(["'%s': '%s'" % (x.name, dico[x.name]) for x in self.node.type.typeFiles])
        inputs = [x.versionActive.getOutput() for x in self.node.getInputNodes()]
        inputs = '"""%s"""' % pickle.dumps(inputs).replace('\\n', '\\\\n')
        projHead = '\n'.join([' ' * 4 + x for x in self.node.graph.getProject().getScript().split('\n')])
        typeHead = '\n'.join([' ' * 4 + x for x in self.node.type.getScript(
            version_id=self.typeForceVersion).split('\n')])
        if action:
            script = '\n'.join([' ' * 4 + x for x in action.command.split('\n')])
        else:
            script = ' ' * 4 + 'pass'
        if not len(projHead.strip()):
            projHead = ' ' * 4 + 'pass'
        if not len(typeHead.strip()):
            typeHead = ' ' * 4 + 'pass'
        if not len(script.strip()):
            script = ' ' * 4 + 'pass'
        script = """try:
%s
except Exception as e:
    print("ERROR IN PROJECT HEAD", file=sys.__stderr__)
    print(traceback.format_exc(), file=sys.__stderr__)
try:
%s
except Exception as e:
    print("ERROR IN TYPE HEAD", file=sys.__stderr__)
    print(traceback.format_exc(), file=sys.__stderr__)
try:
%s
except Exception as e:
    print(traceback.format_exc(), file=sys.__stderr__)
""" % (projHead, typeHead, script)
        script = '\n'.join([' ' * 4 + x for x in script.split('\n')])
        scriptfull = """from __future__ import print_function
import os, sys, pickle, traceback
sys.path.append('%s')
import %s as mgvWrapper
mgvWrapper.connect()
mgvOutput = {}
mgvInputs = %s
mgvInputs = pickle.loads(mgvInputs)
try:
%s
except Exception as e:
    print(traceback.format_exc(), file=sys.__stderr__)
finally:
    out = {'value': None, 'inputs': mgvInputs, 'name': '%s', 'type': '%s', 'version': %s, 'date': '%s', 'user': '%s',
          'action': '%s', 'files': {%s}}
    try:
        out['value'] = mgvOutput
    except:
        pass
    out = pickle.dumps(out)
    mgvWrapper.setNodeAttr({'project_name': os.getenv('MGVPROJECTNAME'), 'path': os.getenv('MGVGRAPHFILEPATH'), 'code': 'NodeVersion', 'uuid': '%s'},
                           output=out)
""" % (os.path.dirname(os.path.abspath(__file__)), choosen_wrapper, inputs, script, self.node.getName(),
       self.node.getType().getName(), self.id, time.strftime("%d/%m/%y %H:%M", time.gmtime()),
       self.node.graph.getUser().split('$')[0], action.getName() if action else '', files, self.uuid)
        # offset = scriptfull[:scriptfull.find(script)].count('\n')
        return scriptfull

    def exe(self, actionname=None, textEdit=None):
        """Execute the action of the node. Redirect the output to a text
        widget if provided.
        """
        action = None
        for ac in self.node.type.getActions(version_id=self.typeForceVersion):
            if ac.getName() == actionname:
                action = ac
                break
        dico = self.getVars()
        script = self.compileScripts(action)
        for x in os.environ.keys():
            dico[x] = os.environ[x]
        dico = mgvDicoReplace(dico)
        for p in self.node.type.typeFiles:
            path = os.path.dirname(dico[p.name])
            if not os.path.exists(path):
                os.makedirs(path)
        if action is not None:
            self.setLastExec(time.strftime("%d/%m/%y %H:%M", time.gmtime()), self.node.user.split("$")[0])
            self.node.graph._saveState(self)
        ExeScript(script, textEdit, env=dico)

    @classmethod
    def getFromJson(cls, element):
        """Create a node from a dictionary."""
        newVersion = cls(uuid=element['uuid'], version_id=element['id'], comment=element['comment'],
                         lastExec=element['lastExec'], lastUser=element['lastUser'],
                         variables=[], parameters={},
                         typeForceVersion=element['typeForceVersion'], locked=element['locked'])
        for childElement in element['variables']:
            MgvVariable.getFromJson(childElement, newVersion)
        for paramKey in element['parameters']:
            newVersion.parameters[paramKey] = element['parameters'][paramKey]
        for dataKey in element['data']:
            newVersion.data[dataKey] = element['data'][dataKey]
        return newVersion

    def getJson(self):
        """Return a dictionary representing the nodeVersion."""
        parameters = {}
        for param in self.parameters:
            value = self.parameters[param]
            lp = [p for p in self.node.type.getParameters(version_id=self.node.versionActive.typeForceVersion)
                  if p.name == param]
            if len(lp):
                typeParam = lp[0]
                if not isinstance(value, string_types):
                    value = str(value)
                if typeParam.default != value and typeParam.visibility:
                    parameters[param] = value

        return {'code': 'NodeVersion', 'id': self.id, 'comment': self.comment, 'lastExec': self.lastExec,
                'lastUser': self.lastUser, 'typeForceVersion': self.typeForceVersion, 'parameters': parameters,
                'locked': self.locked, 'variables': [x.getJson() for x in self.variables], 'uuid': str(self.uuid),
                'data': [{'name': x, 'value': self.data[x]} for x in self.data]}


class MgvAction(object):
    """Mangrove Action object.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the action name.
        menu (str): name of menu path to the action.
                    i.e. "MyNodes" or "MyNodes|menuA|submenuB"
        warning (str): message in a dialog window to confirm the action,
                       or empty if no confirmation is needed.
        command (str): the python script of the action.
        users (str): list of users who can see this action separated by
                     "," or empty for all users.
        stack (bool): True if next action has to wait this one to finish
                      in the action stack.
        order (int): used to organize the display order of the type
                     actions.
    """
    code = "Action"

    def __init__(self, uuid=None, version=None, name='', menu='', command='', warning='', users='', stack=True, order=0):
        self.uuid = uuid
        self.version = version
        self.menu = menu
        self.name = name
        self.command = command
        self.warning = warning
        self.users = users
        self.stack = stack
        self.order = order

    def __repr__(self):
        return "MgvAction %s" % self.name

    def getProject(self):
        return self.version.getProject()

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.version, self.code, menu=self.menu, name=self.name,
                                          command=self.command, warning=self.warning, users=self.users,
                                          stack=self.stack, order=self.order)

    def getName(self):
        """Return the name of the action."""
        return self.name

    def setName(self, name):
        """Set the name of the action."""
        self.name = name

    def _dup(self):
        """Return a new action with the same attributes."""
        return MgvAction(uuid=self.uuid, version=self.version, name=self.name, menu=self.menu, command=self.command,
                         warning=self.warning, users=self.users, stack=self.stack, order=self.order)

    def getJson(self):
        """Return a dictionary representing the action."""
        return {'code': 'Action', 'menu': self.menu, 'name': self.name, 'command': self.command,
                'warning': self.warning, 'users': self.users, 'stack': self.stack, 'order': self.order,
                'uuid': str(self.uuid)}


class MgvParam(object):
    """Mangrove Type Paramater object.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the parameter name.
        type (str): data type. Can be "bool", "int", "float", "string",
                    "text", "python", "file" or "enum".
        enum (str): enum values separated by ";".
        default (str): default value.
        visibility (bool): True if this parameter is visible in the node
                           editor.
        advanced (bool): True if this parameter should be in the node
                         editor's advanced section.
        order (int): used to organize the display order of the type
                     parameters.
    """
    code = "TypeParameter"

    def __init__(self, uuid=None, version=None, name='', type='int', enum='', default=0, visibility=True, order=0,
                 advanced=False):
        self.uuid = uuid
        self.version = version
        self.name = name
        self.type = type
        self.enum = enum
        self.default = default
        self.visibility = visibility
        self.advanced = advanced
        self.order = order

    def __repr__(self):
        return "MgvParam %s" % self.name

    def getProject(self):
        return self.version.getProject()

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.version, self.code, name=self.name, type=self.type, enum=self.enum,
                                          default=self.default, visibility=self.visibility, order=self.order,
                                          advanced=self.advanced)

    def getName(self):
        """Return the name of the parameter."""
        return self.name

    def getType(self):
        """Return the type of the parameter."""
        return self.type

    def getEnum(self):
        """Return the enum values of the parameter."""
        return self.enum

    def getDefault(self):
        """Return the default values of the parameter."""
        return self.default

    def getVisibility(self):
        """Return the visibility state of the parameter."""
        return self.visibility

    def setName(self, name):
        """Set the name of the parameter."""
        self.name = name

    def setType(self, type):
        """Set the type of the parameter."""
        self.type = type

    def setEnum(self, enum):
        """Set the enum values of the parameter."""
        self.enum = enum

    def setDefault(self, default):
        """Set the default value of the parameter."""
        self.default = default

    def setVisibility(self, visibility):
        """Set the visibility state of the parameter."""
        self.visibility = visibility

    def _dup(self):
        """Return a new typeParameter with the same attributes."""
        return MgvParam(uuid=self.uuid, version=self.version, name=self.name, type=self.type, enum=self.enum,
                        default=self.default, visibility=self.visibility, order=self.order, advanced=self.advanced)

    def getJson(self):
        """Return a dictionary representing the typeParameter."""
        return {'code': 'TypeParameter', 'name': self.name, 'type': self.type, 'enum': self.enum,
                'default': self.default, 'visibility': self.visibility, 'order': self.order, 'advanced': self.advanced,
                'uuid': str(self.uuid)}


class MgvTypeFile(object):
    """Mangrove TypeFile object.

    A typeFile object stores an output file of a node.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the typeFile name.
        path (str): the path of the output file.
        copy (bool): True if this path has to be copied when the node is
        versioned.
    """
    code = 'TypeFile'

    def __init__(self, uuid=None, type=None, name='OUT1',
                 path='${MGVNODEPATH}/VERSIONS/${MGVGRAPHNAME}_${MGVNODENAME}_v${MGVNODEVERSION}.ext', copy=True):
        self.uuid = uuid
        self.type = type
        self.name = name
        self.path = path
        self.copy = copy

    def __repr__(self):
        return "MgvTypeFile %s" % self.name

    def getProject(self):
        return self.type.getProject()

    def create(self, uuid=None):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.type, self.code, uuid=uuid, name=self.name, path=self.path, copy=self.copy)

    def setName(self, name):
        """Set the name of the typeFile."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def setPath(self, path):
        """Set the path of the typeFile."""
        self.path = path
        mgvWrapper.setNodeAttr(self, path=path)

    def setCopy(self, copy):
        """Set the copy state of the typeFile."""
        self.copy = copy
        mgvWrapper.setNodeAttr(self, copy=copy)

    def _dup(self):
        """Return a new typeFile with the same attributes."""
        return MgvTypeFile(uuid=self.uuid, type=self.type, name=self.name, path=self.path, copy=self.copy)

    def getJson(self):
        """Return a dictionary representing the typeFile."""
        return {'code': 'TypeFile', 'name': self.name, 'path': self.path, 'copy': self.copy, 'uuid': str(self.uuid)}


class MgvType(object):
    """Mangrove Type object.

    Attributes:
        uuid (str): unique id in the database.
        project (MgvProject): the project of the type.
        name (str): the typeFile name.
        category (str): used to arrange types in the UI left panel.
        color (str): the color of a node with this type,
                     with the format "#FF0000".
        shape (str): shape of the node.
                     Can be "Rectangle", "Circle" or "Image".
        width (int): width of the node.
        shapeVector (list of tuples): If the shape is "Image",
            this is the path around the alpha channel
            used to display selection outline.
        image (str): if the shape is "Image", path to that image.
        linkWith (list of str): uuids of types whose node versions
            have to be synchronised if linked after a node of this type.
            Example: It is typeA, you have typeB's uuid in this list.
            If you have a node nodeA of type typeA connected to a node
            nodeB of type typeB, then adding, deleting or changing
            version on nodeA will do as well on node nodeB.
        help (str): tooltip to display on the type in the UI left panel.
        typeFiles (list of MgvTypeFile):
        versions (list of MgvTypeVersion): the versions of the type.
        versionActive (MgvTypeVersion): the active version of the type.
    """
    code = "Type"

    def __init__(self, uuid=None, project=None, category='', name='None', color="#000000", shape='Rectangle',
                 typeFiles=None, shapeVector=None, image='', context='', linkWith=None, help='', width=100,
                 versions=None, versionActive=-1, software = ''):
        self.uuid = uuid
        self.project = project
        self.typeFiles = typeFiles if typeFiles is not None else []
        self.versions = versions if versions is not None else []
        self.versions = sorted(self.versions, key=lambda sort_key: sort_key.id)
        for x in self.versions + self.typeFiles:
            x.type = self
        self.versionActive = None
        self.context = context
        if len(self.versions):
            self.versionActive = [x for x in self.versions if x.id == versionActive]
            if len(self.versionActive):
                self.versionActive = self.versionActive[0]
            else:
                self.versionActive = self.versions[-1]
        else:
            v = MgvTypeVersion(type=self)
            self.versionActive = v
            self.versions.append(v)
        self.category = category
        self.name = name
        self.color = color
        self.shape = shape
        self.software = software
        self.shapeVector = shapeVector if shapeVector is not None else []
        self.image = image
        self.linkWith = linkWith if linkWith is not None else []
        self.help = help
        self.width = width

    def __repr__(self):
        return "MgvType %s" % self.name

    def getProject(self):
        return self.project

    def create(self, uuid=None):
        """Create the equivalent object in the database.
        Also create typeFile and version objects if any.
        """
        shapeVector = ';'.join(['%s, %s' % (x[0], x[1]) for x in self.shapeVector])
        self.uuid = mgvWrapper.createNode(self.project, self.code, uuid=uuid, context=self.context,
                                          category=self.category, name=self.name, color=self.color, shape=self.shape,
                                          image=self.image, help=self.help, width=self.width, shapeVector=shapeVector,
                                          lock='', software=self.software, linkWith=';'.join(self.linkWith),
                                          versionActive=self.versionActive.getId())
        for typeFile in self.typeFiles:
            typeFile.create()
        for version in self.versions:
            version.create()

    def getCategory(self):
        """Return the category of the type."""
        return self.category

    def getSoftware(self):
        """Return the software of the type."""
        return self.software

    def getName(self):
        """Return the name of the type."""
        return self.name

    def getColor(self):
        """Return the color of the type."""
        return self.color

    def getShape(self):
        """Return the shape of the type."""
        return self.shape

    def getShapeVector(self):
        """Return the shape path coordinates of the type."""
        return self.shapeVector

    def getImage(self):
        """Return the image path of the type."""
        return str(self.image)

    def getWidth(self):
        """Return the width of the type."""
        return self.width

    def getLinkWith(self):
        """Return the uuids of the types synchronised with this type."""
        return self.linkWith

    def getHelp(self):
        """Return the toolotip of the type."""

        return self.help

    def getScript(self, version_id=-1):
        """Return the script of the active version
        or a specific version of the type.
        """
        if version_id > -1:
            for v in self.versions:
                if v.id == version_id:
                    return v.getScript()
        return self.versionActive.getScript()

    def setCategory(self, category):
        """Set the category of the type."""
        self.category = category

    def setSoftware(self, software):
        """Set the software of the type."""
        self.software = software

    def setName(self, name):
        """Set the name of the type."""
        self.name = name

    def setColor(self, color):
        """Set the color of the type."""
        self.color = color

    def setShape(self, shape):
        """Set the shape of the type."""
        self.shape = shape

    def setImage(self, filePath):
        """Set the image path of the type."""
        with open(filePath, "rb") as image_file:
            self.image = str(base64.b64encode(image_file.read()))

    def setLinkWith(self, typeList):
        """Set the uuids of the types synchronised with this type."""
        self.linkWith = typeList

    def setHelp(self, text):
        """Set the tooltip of the type."""
        self.help = text

    def getActions(self, version_id=-1):
        """Return the actions of the active version
        or a specific version of the type.
        """
        if version_id > -1:
            for v in self.versions:
                if v.id == version_id:
                    return v.getActions()
        return self.versionActive.getActions()

    def getAction(self, name, version_id=-1):
        """Return an action of the active version
        or a specific version of the type.
        """
        if version_id > -1:
            for v in self.versions:
                if v.id == version_id:
                    return v.getAction(name)
        return self.versionActive.getAction(name)

    def getParameters(self, version_id=-1):
        """Return the parameters of the active version
        or a specific version of the type.
        """
        if version_id > -1:
            for v in self.versions:
                if v.id == version_id:
                    return v.getParameters()
        return self.versionActive.getParameters()

    def getParameter(self, name, version_id=-1):
        """Return a parameter of the active version
        or a specific version of the type.
        """
        if version_id > -1:
            for v in self.versions:
                if v.id == version_id:
                    return v.getParameter(name)
        return self.versionActive.getParameter(name)

    def setVersionActive(self, version):
        """Set the active version of the type."""
        if version in self.versions:
            self.versionActive = version
            mgvWrapper.setNodeAttr(self, versionActive=version.id)

    def _copy(self, node_type):
        """Set all the type attributes from another type."""
        self.versions = node_type.versions
        for v in node_type.versions:
            v.type = self
        self.versionActive = node_type.versionActive
        self.category = node_type.category
        self.name = node_type.name
        self.color = node_type.color
        self.shape = node_type.shape
        self.shapeVector = [[x[0], x[1]] for x in node_type.shapeVector]
        self.typeFiles = node_type.typeFiles
        self.image = node_type.image
        self.context = node_type.context
        self.linkWith = list(node_type.linkWith)
        self.help = node_type.help
        self.width = node_type.width
        self.software = node_type.software

    def _dup(self):
        """Return a new type with the same attributes."""
        versions = [x._dup() for x in self.versions]
        typeFiles = [x._dup() for x in self.typeFiles]
        new = MgvType(uuid=self.uuid, project=self.project, name=self.name, category=self.category, shape=self.shape,
                      color=self.color, typeFiles=typeFiles, image=self.image,
                      shapeVector=[[x[0], x[1]] for x in self.shapeVector], context=self.context,
                      linkWith=list(self.linkWith), help=self.help, width=self.width, versions=versions,
                      versionActive=self.versionActive.getId(), software=self.software)
        return new

    @classmethod
    def getFromJson(cls, each_type):
        """Create a type from a dictionary."""
        typeFiles = []
        for t in each_type['typeFiles']:
            typeFile = MgvTypeFile(name=t['name'], path=t['path'], copy=t['copy'])
            typeFiles.append(typeFile)
        versions = []
        for v in each_type['versions']:
            parameters = []
            actions = []
            for p in v['parameters']:
                parameter = MgvParam(name=p['name'], type=p['type'], enum=p['enum'], default=p['default'],
                                     visibility=p['visibility'], order=p['order'], advanced=p['advanced'])
                parameters.append(parameter)
            for a in v['actions']:
                action = MgvAction(name=a['name'], command=a['command'], warning=a['warning'],
                                   users=a['users'], stack=a['stack'], order=a['order'])
                actions.append(action)
            version = MgvTypeVersion(version_id=v['id'], parameters=parameters, actions=actions, script=v['script'])
            for a in actions:
                a.version = version
            for p in parameters:
                p.version = version
            versions.append(version)
        shapeVector = None
        if len(each_type['shapeVector'].strip()):
            shapeVector = [[float(y) for y in x.split(',')] for x in each_type['shapeVector'].split(';')]
        
        new = cls(uuid=None, category=each_type['category'], name=each_type['name'],
                  color=each_type['color'], shape=each_type['shape'], image=each_type['image'],
                  context=each_type['context'], help=each_type['help'], width=each_type['width'],
                  versionActive=each_type['versionActive'], linkWith=each_type['linkWith'],
                  shapeVector=shapeVector, typeFiles=typeFiles, versions=versions, software=each_type['software'])
        return new

    def getJson(self):
        """Return a dictionary representing the type."""
        shapeVector = ';'.join(['%s, %s' % (x[0], x[1]) for x in self.shapeVector])
        return {'code': 'Type', 'category': self.category, 'name': self.name, 'color': self.color, 'shape': self.shape,
                'image': self.image, 'context': self.context, 'linkWith': ';'.join(self.linkWith),
                'help': self.help, 'width': self.width, 'versionActive': self.versionActive.id,
                'versions': [x.getJson() for x in self.versions], 'uuid': str(self.uuid), 'lock': '',
                'typeFiles': [x.getJson() for x in self.typeFiles], 'shapeVector': shapeVector,
                'software': self.software}


class MgvTypeVersion(object):
    """Mangrove TypeVersion object.

    Attributes:
        uuid (str): unique id in the database.
        id (int): version id.
        actions (list of MgvAction): list of available actions for this
                                     type nodes.
        parameters (list of MgvParam): list of parameters for this type
                                       nodes.
        script (str): the second part of every node's execution python
                      script.
    """
    code = 'TypeVersion'

    def __init__(self, uuid=None, type=None, version_id=0, parameters=None, actions=None, script=''):
        self.uuid = uuid
        self.type = type
        self.id = version_id
        self.actions = sorted(actions, key=lambda x: x.order) if actions is not None else []
        self.parameters = sorted(parameters, key=lambda x: x.order) if parameters is not None else []
        for x in self.actions + self.parameters:
            x.version = self
        self.script = script

    def __repr__(self):
        return "MgvTypeVersion %s" % self.id

    def getProject(self):
        return self.type.getProject()

    def create(self):
        """Create the equivalent object in the database.
        Also create action and typeParameter objects if any."""
        self.uuid = mgvWrapper.createNode(self.type, self.code, id=self.id, script=self.script)
        for action in self.actions:
            action.create()
        for param in self.parameters:
            param.create()

    def getId(self):
        """Return the id of the version."""
        return self.id

    def getActions(self):
        """Return the actions of the version."""
        return self.actions

    def getAction(self, name):
        """Return an action of the version."""
        for action in self.actions:
            if action.name == name:
                return action
        return None

    def getScript(self):
        """Return the script of the version."""
        return self.script

    def getParameters(self):
        """Return the parameters of the version."""

        return self.parameters

    def getParameter(self, name):
        """Return a parameter of the version."""
        for x in self.parameters:
            if x.getName() == name:
                return x
        return None

    def _copy(self, typeVersion):
        """Set all the version attributes from another version."""
        self.uuid = typeVersion.uuid
        self.id = typeVersion.id
        self.actions = [x._dup() for x in typeVersion.actions]
        self.parameters = [x._dup() for x in typeVersion.parameters]
        self.script = typeVersion.script
        for x in self.actions + self.parameters:
            x.version = self

    def _dup(self):
        """Return a new typeVersion with the same attributes."""
        actions = [x._dup() for x in self.actions]
        parameters = [x._dup() for x in self.parameters]
        new = MgvTypeVersion(uuid=self.uuid, version_id=self.id, actions=actions, parameters=parameters,
                             script=self.script, type=self.type)
        return new

    def getJson(self):
        """Return a dictionary representing the typeVersion."""
        return {'code': 'TypeVersion', 'id': self.id, 'script': self.script, 'uuid': str(self.uuid),
                'actions': [x.getJson() for x in self.actions],
                'parameters': [x.getJson() for x in self.parameters]}


class MgvBatchScript(object):
    """Mangrove Action object.

    Attributes:
        uuid (str): unique id in the database.
        name (str): the batchscript name.
        users (str): list of users who can see this batchscript separated by
                     "," or empty for all users.
        script (str): the script of the hud.
        pattern (str): the pattern name where the batchscript will be visible or 'All Patterns'.
        template (str): the template name where the batchscript will be visible or 'All Templates'.
    """
    code = "BatchScript"

    def __init__(self, uuid=None, project=None, name='', users='', script='', pattern='', template=''):
        self.uuid = uuid
        self.project = project
        self.name = name
        self.users = users
        self.script = script if len(script) else 'def Execute(graph):\n    print(graph.getFullName())'
        self.pattern = pattern
        self.template = template

    def __repr__(self):
        return "MgvBatchScript %s" % self.name

    def getProject(self):
        return self.project

    def create(self):
        """Create the equivalent object in the database."""
        self.uuid = mgvWrapper.createNode(self.project, self.code, name=self.name, users=self.users,
                                          script=self.script, pattern=self.pattern, template=self.template)

    def setName(self, name):
        """Set the name of the batchscript."""
        self.name = name
        mgvWrapper.setNodeAttr(self, name=name)

    def setScript(self, script):
        """Set the script of the batchscript."""
        self.script = script
        mgvWrapper.setNodeAttr(self, script=script)

    def _dup(self):
        """Return a new action with the same attributes."""
        return MgvBatchScript(uuid=self.uuid, project=self.project, name=self.name, users=self.users, script=self.script,
                              pattern=self.pattern, template=self.template)

    def getJson(self):
        """Return a dictionary representing the action."""
        return {'code': 'BatchScript', 'name': self.name, 'users': self.users, 'script': self.script,
                'pattern': self.pattern, 'template': self.template, 'uuid': str(self.uuid)}
