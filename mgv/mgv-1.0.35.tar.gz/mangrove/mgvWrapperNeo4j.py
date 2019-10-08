from __future__ import print_function
import mgvApi
import uuid
import json
import sys
import os
from six import string_types
from py2neo import Graph, Node, Relationship, database


def connect(name=None, user=None, pwd=None):
    """Called at mangrove startup and used to set up global variables to access to the database.
    In this case the variable neograph and selector, which stores the neo4j connection."""
    global neograph, selector
    if name is None:
        home = os.getenv('HOME') if os.getenv('HOME') else os.getenv('USERPROFILE')
        localSettingsFile = os.path.join(home, 'mangrove1.0', 'settings.info')
        name, user, pwd = '', '', ''
        if os.path.exists(localSettingsFile):
            with open(localSettingsFile) as fid:
                dic = json.load(fid)
                choosen_wrapper = dic['wrapper']['current']
                name = dic['wrapper'][choosen_wrapper]['host']
                user = dic['wrapper'][choosen_wrapper]['user']
                pwd = dic['wrapper'][choosen_wrapper]['pwd']
    neograph = Graph(host=name, user=user, password=pwd)
    selector = database.selection.NodeSelector(neograph)


def toHtml(s):
    """Convert string to html formatting."""
    if isinstance(s, string_types):
        return s.replace('"', '&quot;').replace("'", '&apos;').replace("\\", "&#92;")
    return s


def fromHtml(s):
    """Convert string from html formatting."""
    if isinstance(s, string_types):
        return s.replace('&quot;', '"').replace('&apos;', "'").replace("&#92;", "\\")
    return s


def lockProject(project, user):
    """Set project lock property with user name if it's empty.

    Parameters:
        project (MgvProject): the project.
        user (str): the user name.
    Return:
        str: same user name if lock was empty, else lock value.
        """
    g = neograph.run("MATCH (x:Project {uuid:'%s'}) RETURN x.lock" % project.uuid)
    locks = [x['x.lock'] for x in g]
    if all([x in ['', user] for x in locks]):
        neograph.run("MATCH (p:Project {uuid:'%s'}) SET p.lock='%s'" % (project.uuid, user))
        return user
    return locks[0]


def unlockProject(project):
    """Set project lock property to empty."""
    neograph.run("MATCH (p:Project {uuid:'%s'}) SET p.lock=''" % project.uuid)


def getType(project_name, name=None, uuid=None):
    """Return a MgvType object from the database.

    Uuid or name has to be provided.

    Parameters:
        project_name (str): the name of the project.
        name (str): the name of the type (optional).
        uuid (str): the uuid of the type (optional).
    Return:
        MgvType: the type."""
    if not name and not uuid:
        return None
    if uuid:
        gtyp = neograph.run("MATCH (:Project {name:'%s'})-->(x:Type {uuid:'%s'}) RETURN x" % (project_name, uuid)).data()
    elif name:
        gtyp = neograph.run("MATCH (:Project {name:'%s'})-->(x:Type {name:'%s'}) RETURN x" % (project_name, name)).data()
    gt = gtyp[0]

    typeFiles = []
    gfil = neograph.run("MATCH (:Type {uuid:'%s'})-->(x:TypeFile) RETURN x" % gt['x']['uuid']).data()
    for gf in gfil:
        typeFiles.append(mgvApi.MgvTypeFile(uuid=gf['x']['uuid'], name=gf['x']['name'], path=gf['x']['path'],
                                            copy=gf['x']['copy']))

    versions = []
    gver = neograph.run("MATCH (:Type {uuid:'%s'})-->(x:TypeVersion) RETURN x" % gt['x']['uuid']).data()
    for gv in gver:
        actions = []
        params = []
        gact = neograph.run("MATCH (:TypeVersion {uuid:'%s'})-->(x:Action) RETURN x" % gv['x']['uuid']).data()
        for ga in gact:
            actions.append(mgvApi.MgvAction(uuid=ga['x']['uuid'], menu=ga['x']['menu'], name=ga['x']['name'],
                                            command=ga['x']['command'], warning=ga['x']['warning'],
                                            users=ga['x']['users'], stack=ga['x']['stack'], order=ga['x']['order']))
        gpar = neograph.run("MATCH (:TypeVersion {uuid:'%s'})-->(x:TypeParameter) RETURN x" % gv['x']['uuid']).data()
        for gp in gpar:
            param = mgvApi.MgvParam(uuid=gp['x']['uuid'], name=gp['x']['name'], type=gp['x']['type'],
                                    enum=gp['x']['enum'], default=gp['x']['default'], visibility=gp['x']['visibility'],
                                    order=gp['x']['order'], advanced=gp['x']['advanced'])
            if param.type == "int":
                param.default = int(param.default)
            if param.type == "float":
                param.default = float(param.default)
            if param.type == "bool":
                param.default = str(param.default) in ["True", "true", "1"]
            params.append(param)

        v = mgvApi.MgvTypeVersion(uuid=gv['x']['uuid'], version_id=gv['x']['id'], actions=actions,
                                  parameters=params, script=gv['x']['script'])
        versions.append(v)

    versionActive = -1
    if gt['x']['versionActive'] in [x.id for x in versions]:
        versionActive = gt['x']['versionActive']
    
    shapeVector = []
    if len(gt['x']['shapeVector'].strip()):
        shapeVector = [[float(y) for y in x.split(',')] for x in gt['x']['shapeVector'].split(';')]

    node_type = mgvApi.MgvType(uuid=gt['x']['uuid'], name=gt['x']['name'], category=gt['x']['category'],
                               color=gt['x']['color'], shape=gt['x']['shape'], image=gt['x']['image'],
                               context=gt['x']['context'], help=gt['x']['help'], width=gt['x']['width'],
                               shapeVector=shapeVector, typeFiles=typeFiles, linkWith=gt['x']['linkWith'].split(';'),
                               versions=versions, versionActive=versionActive, software=gt['x']['software'])
    return node_type


def getHud(project_name, name=None, uuid=None):
    """Return a MgvHud object from the database.

    Uuid or name has to be provided.

    Parameters:
        project_name (str): the name of the project.
        name (str): the name of the hud (optional).
        uuid (str): the uuid of the hud (optional).
    Return:
        MgvHud: the hud."""
    if not name and not uuid:
        return None
    if uuid:
        gtyp = neograph.run(
            "MATCH (:Project {name:'%s'})-->(x:Hud {uuid:'%s'}) RETURN x" % (project_name, uuid)).data()
    if name:
        gtyp = neograph.run(
            "MATCH (:Project {name:'%s'})-->(x:Hud {name:'%s'}) RETURN x" % (project_name, name)).data()
    gt = gtyp[0]

    node_type = mgvApi.MgvHud(uuid=gt['x']['uuid'], name=gt['x']['name'], event=gt['x']['event'],
                              script=gt['x']['script'])
    return node_type


def getBatchScript(project_name, name=None, uuid=None):
    """Return a MgvBatchScript object from the database.

    Uuid or name has to be provided.

    Parameters:
        project_name (str): the name of the project.
        name (str): the name of the batchScript (optional).
        uuid (str): the uuid of the batchScript (optional).
    Return:
        MgvBatchScript: the batchScript."""
    if not name and not uuid:
        return None
    if uuid:
        gtyp = neograph.run(
            "MATCH (:Project {name:'%s'})-->(x:BatchScript {uuid:'%s'}) RETURN x" % (project_name, uuid)).data()
    if name:
        gtyp = neograph.run(
            "MATCH (:Project {name:'%s'})-->(x:BatchScript {name:'%s'}) RETURN x" % (project_name, name)).data()
    gt = gtyp[0]

    node_type = mgvApi.MgvBatchScript(uuid=gt['x']['uuid'], name=gt['x']['name'], users=gt['x']['users'],
                                      script=gt['x']['script'], pattern=gt['x']['pattern'], template=gt['x']['template'])
    return node_type


def getTypes(projectName):
    """Returns a list of the project types.

    Parameters:
        projectName (str): the project name.
    Return:
        list of MgvType: a list of the types.
    """
    types = []
    gtyp = neograph.run("MATCH (:Project {name:'%s'})-->(x:Type) RETURN x" % projectName).data()
    for gt in gtyp:
        typeFiles = []
        gfil = neograph.run("MATCH (:Type {uuid:'%s'})-->(x:TypeFile) RETURN x" % gt['x']['uuid']).data()
        for gf in gfil:
            typeFiles.append(mgvApi.MgvTypeFile(uuid=gf['x']['uuid'], name=gf['x']['name'], path=gf['x']['path'],
                                                copy=gf['x']['copy']))

        versions = []
        gver = neograph.run("MATCH (:Type {uuid:'%s'})-->(x:TypeVersion) RETURN x" % gt['x']['uuid']).data()
        for gv in gver:
            actions = []
            params = []
            gact = neograph.run("MATCH (:TypeVersion {uuid:'%s'})-->(x:Action) RETURN x" % gv['x']['uuid']).data()
            for ga in gact:
                actions.append(mgvApi.MgvAction(uuid=ga['x']['uuid'], menu=ga['x']['menu'], name=ga['x']['name'],
                                                command=ga['x']['command'], warning=ga['x']['warning'],
                                                users=ga['x']['users'], stack=ga['x']['stack'], order=ga['x']['order']))
            gpar = neograph.run("MATCH (:TypeVersion {uuid:'%s'})-->(x:TypeParameter) RETURN x" %
                                gv['x']['uuid']).data()
            for gp in gpar:
                param = mgvApi.MgvParam(uuid=gp['x']['uuid'], name=gp['x']['name'], type=gp['x']['type'],
                                        enum=gp['x']['enum'], default=gp['x']['default'],
                                        visibility=gp['x']['visibility'], order=gp['x']['order'],
                                        advanced=gp['x']['advanced'])
                if param.type == "int":
                    param.default = int(param.default)
                if param.type == "float":
                    param.default = float(param.default)
                if param.type == "bool":
                    param.default = str(param.default) in ["True", "true", "1"]
                params.append(param)
            v = mgvApi.MgvTypeVersion(uuid=gv['x']['uuid'], version_id=gv['x']['id'], actions=actions,
                                      parameters=params, script=gv['x']['script'])
            versions.append(v)

        shapeVector = []
        if len(gt['x']['shapeVector'].strip()):
            shapeVector = [[float(y) for y in x.split(',')] for x in gt['x']['shapeVector'].split(';')]

        versionActive = -1
        if gt['x']['versionActive'] in [x.id for x in versions]:
            versionActive = gt['x']['versionActive']

        node_type = mgvApi.MgvType(uuid=gt['x']['uuid'], name=gt['x']['name'], category=gt['x']['category'],
                                   color=gt['x']['color'], shape=gt['x']['shape'], image=gt['x']['image'],
                                   context=gt['x']['context'], help=gt['x']['help'], width=gt['x']['width'],
                                   shapeVector=shapeVector, typeFiles=typeFiles,
                                   linkWith=gt['x']['linkWith'].split(';'),
                                   versions=versions, versionActive=versionActive, software=gt['x']['software'])
        types.append(node_type)

    return types


def getProject(projectName):
    """Returns a MgvProject object from the database from its name."""
    gproj = neograph.run("MATCH (x:Project {name:'%s'}) RETURN x" % projectName).data()
    if len(gproj):
        pid = gproj[0]['x']['uuid']
        name = gproj[0]['x']['name']
        versions_padding = gproj[0]['x']['versions_padding']
        versions_start = gproj[0]['x']['versions_start']
        if not versions_padding:
            versions_padding, versions_start = 3, 0
        script = gproj[0]['x']['script']
        contexts = []
        gcon = neograph.run("MATCH (:Project {name:'%s'})-->(y:Context) RETURN y" % name).data()
        for gn in gcon:
            conid = gn['y']['uuid']
            conname = gn['y']['name']
            convalue = gn['y']['value']
            pypcontext = mgvApi.MgvContext(uuid=conid, name=conname, value=convalue)
            contexts.append(pypcontext)
        huds = []
        gwid = neograph.run("MATCH (:Project {name:'%s'})-->(y:Hud) RETURN y" % name).data()
        for gn in gwid:
            widid = gn['y']['uuid']
            widname = gn['y']['name']
            widscript = gn['y']['script']
            widevent = gn['y']['event']
            pyphud = mgvApi.MgvHud(uuid=widid, name=widname, script=widscript, event=widevent)
            huds.append(pyphud)
        batchs = []
        gwid = neograph.run("MATCH (:Project {name:'%s'})-->(y:BatchScript) RETURN y" % name).data()
        for gn in gwid:
            widid = gn['y']['uuid']
            widname = gn['y']['name']
            widscript = gn['y']['script']
            widusers = gn['y']['users']
            widpattern = gn['y']['pattern']
            widtemplate = gn['y']['template']
            pypbatch = mgvApi.MgvBatchScript(uuid=widid, name=widname, script=widscript, users=widusers,
                                             pattern=widpattern, template=widtemplate)
            batchs.append(pypbatch)
        types = getTypes(name)
        patterns = []
        gpat = neograph.run("MATCH (:Project {name:'%s'})-->(y:Pattern) RETURN y" % name).data()
        for gn in gpat:
            patid = gn['y']['uuid']
            patname = gn['y']['name']
            pattern = gn['y']['pattern']
            patorder = gn['y']['order']
            graph_name = gn['y']['graph_name']
            templates = []
            gtem = neograph.run("MATCH (:Pattern {uuid:'%s'})-->(y:GraphTemplate) RETURN y" % patid).data()
            for gm in gtem:
                temid = gm['y']['uuid']
                temname = gm['y']['name']
                temicon = gm['y']['icon']
                pyptemplate = mgvApi.MgvGraphTemplate(uuid=temid, name=temname, icon=temicon)
                templates.append(pyptemplate)
            pyppattern = mgvApi.MgvPattern(uuid=patid, name=patname, pattern=pattern, templates=templates,
                                           order=patorder, graph_name=graph_name)
            patterns.append(pyppattern)

        patterns.sort(key=lambda x: x.order)
        p = mgvApi.MgvProject(uuid=pid, name=name, script=script, patterns=patterns, types=types, contexts=contexts,
                              batchScripts=batchs, huds=huds, versions_padding=versions_padding,
                              versions_start=versions_start)
        return p
    return None


def getProjectNames():
    """Returns the list of the projects's names."""
    g = neograph.run("MATCH (x:Project) RETURN x.name")
    return [x['x.name'] for x in g]


def getPatternGraphs(pattern, with_node_named=None, with_type_named=None):
    """Returns a list of graph paths.

    Parameters:
        pattern (MgvPattern): the pattern of the graphs to return.
        with_node_named (str): only returns graphs that contains
                               a node with this name (optional).
        with_type_named (str): only returns graphs that contains
                               a node with this type name (optional).
    Return:
        list: list of element formed as : [patternName,key0,..,keyN,graph_name].
    """
    plus = ''
    type_uuid = None
    if with_type_named:
        type_uuids = [x.uuid for x in pattern.project.types if x.name == with_type_named]
        if len(type_uuids):
            type_uuid = type_uuids[0]

    if with_node_named and not type_uuid:
        plus = "-->(n:Node) WHERE n.name =~ '%s'" % with_node_named
    if with_node_named and type_uuid:
        plus = "-->(n:Node {typeUuid:'%s'}) WHERE n.name =~ '%s'" % (type_uuid, with_node_named)
    if not with_node_named and type_uuid:
        plus = "-->(:Node {typeUuid:'%s'})" % type_uuid
    cmd = "MATCH p=(x:Pattern {uuid:'%s'})-->(:Graph)%s RETURN p" % (pattern.uuid, plus)
    g = neograph.run(cmd)

    result = []
    for a in g:
        result.append([pattern.name]+[x.end_node()['name'] for x in a['p'] if 'Node' not in x.end_node().labels()])
    return result


def getGraphInfo(pattern, keys):
    """Get a graph details from its path.

    Parameters:
        pattern (MgvPattern): the pattern.
        keys (list of str): path of the graph from the pattern name to its name.
    Returns
        dict: a dictionary with a uuid value and a template_name value.
    """
    cmd = "MATCH (:Project {uuid:'%s'})-->(:Pattern {name:'%s'})-->(x:Graph {path:'%s'}) RETURN x.uuid, x.template_name" % (pattern.project.uuid, pattern.name, ':'.join(keys))
    g = neograph.run(cmd)
    for gn in g:
        return {'code': 'Graph', 'uuid': gn['x.uuid'], 'template_name': gn['x.template_name']}
    return {}


def getGraphVars(pattern, keys):
    g = neograph.run(
        "MATCH p=(:Pattern {uuid:'%s'})-->(x:Graph {path:'%s'}) RETURN x.uuid" % (pattern.uuid, ':'.join(keys)))
    for gn in g:
        v = neograph.run("MATCH (:Graph {uuid:'%s'})-->(x:Variable) RETURN x.name, x.value, x.active" % gn['x.uuid'])
        result = []
        for vn in v:
            result.append({'name': vn['x.name'], 'value': vn['x.value'], 'active': vn['x.active']})
        return result
    return None


def setGraphVar(pattern, keys, name, newname=None, value=None, active=None):
    g = neograph.run(
        "MATCH p=(:Pattern {uuid:'%s'})-->(x:Graph {path:'%s'}) RETURN x.uuid" % (pattern.uuid, ':'.join(keys)))
    for gn in g:
        v = neograph.run("MATCH (:Graph {uuid:'%s'})-->(x:Variable) RETURN x.uuid" % gn['x.uuid'])
        a = False
        for vn in v:
            a = True
            if value is not None:
                neograph.run("MATCH (:Variable {uuid:'%s'}) SET x.value='%s'" % (vn['x.uuid'], value))
            if active is not None:
                neograph.run("MATCH (:Variable {uuid:'%s'}) SET x.active='%s'" % (vn['x.uuid'], active))
            if newname is not None:
                neograph.run("MATCH (:Variable {uuid:'%s'}) SET x.name='%s'" % (vn['x.uuid'], name))
        if not a:
            newname = name if newname is None else newname
            value = '' if value is None else value
            active = True if active is None else active

            x = Node('Variable', name=newname, value=value, active=active)
            f = selector.select('Graph', uuid=gn['x.uuid'])
            f = list(f)[0]
            neograph.create(x)
            neograph.create(Relationship(f, "GraphToVariable", x))
            neograph.push(x)


def graphExists(pattern, graphpath):
    """Check if a graph exists in the database.

    Parameters:
        pattern (MgvPattern): the pattern.
        graphname (str): the graph name.
        graphpath (list of str): the graph path from the pattern name
                                 to the last key.
    Return:
        bool: True if the graph exists.
    """
    g = neograph.run("MATCH p=(:Pattern {uuid:'%s'})-->(x:Graph {path:'%s'}) RETURN x.uuid" % (
            pattern.uuid, graphpath))
    while g.forward():
        return True
    return False


def getObjects(graph):
    """Returns the elements of a graph.

    The graph is found in the database by its uuid if not None.
    By its path in other case.

    Parameters:
        graph (MgvGraph): the graph.
    Return:
        dict: A complete dictionary representing the graph
              and all its elements.
        None: The graph has not been found.
    """

    updates = {x.uuid: x.updated for x in graph.nodes}
    graphObject = {'nodes': [], 'variables': [], 'groups': []}
    if graph.path[-1] == '*template*':
        g = neograph.run(
            "MATCH p=(:Pattern {uuid:'%s'})-->(:GraphTemplate {name:'%s'})-->(x:Graph {name:'%s'}) RETURN x.uuid,x.templatePath,x.template_name" % (
            graph.pattern.uuid, graph.getName(), graph.getName()))
    elif graph.uuid:
        g = neograph.run("MATCH p=(x:Graph {uuid:'%s'}) RETURN x.uuid,x.templatePath,x.template_name" % graph.uuid)
    else:
        g = neograph.run(
            "MATCH p=(:Pattern {uuid:'%s'})-->(x:Graph {name:'%s', path:'%s'}) RETURN x.uuid,x.templatePath,x.template_name" % (
            graph.pattern.uuid, graph.getName(), ':'.join(graph.path)))
    g.forward()
    graphObject['uuid'] = g.current()['x.uuid']
    graphObject['template_name'] = g.current()['x.template_name']
    if not graphObject['template_name']:
        graphObject['template_name'] = g.current()['x.templatePath']
        if graphObject['template_name']:
            neograph.run("MATCH (g:Graph {uuid:'%s'}) SET g.template_name='%s'" %
                         (graphObject['uuid'], graphObject['template_name']))
        else:
            graphObject['template_name'] = ''

    graphObject['templatePath'] = graphObject['template_name']

    g = neograph.run("MATCH p=(x:Graph {uuid:'%s'})-->() RETURN p" % graphObject['uuid'])
    while g.forward():
        for gn in g.current()['p']:
            a = gn.start_node()
            b = gn.end_node()
            tc = list(gn.types())[-1]
            ta, tb = list(a.labels())[0], list(b.labels())[0]

            if tb == 'Node':
                optim = False
                if b['uuid'] in updates:
                    up = getNodeAttr('Node', b['uuid'], "updated")
                    if up > updates[b['uuid']]:
                        neograph.pull(b)
                    else:
                        optim = True

                newnode = dict(b)
                newnode['versions'] = []
                newnode['data'] = {}
                graphObject['nodes'].append(newnode)
                gg = neograph.run("MATCH p=(x:Node {uuid:'%s'})-->() RETURN p" % b['uuid'])
                while gg.forward():
                    for ggn in gg.current()['p']:
                        b = ggn.end_node()
                        tb = list(b.labels())[0]
                        if not optim:
                            neograph.pull(b)
                        if tb == 'Data':
                            newdata = dict(b)
                            newnode['data'][newdata['name']] = fromHtml(newdata['value'])
                        if tb == "NodeVersion":
                            newversion = dict(b)
                            newversion['parameters'] = {}
                            newversion['variables'] = []
                            newversion['data'] = {}
                            if 'locked' not in newversion:
                                newversion['locked'] = False
                            newnode['versions'].append(newversion)

                            ggg = neograph.run("MATCH p=(x:NodeVersion {uuid:'%s'})-->() RETURN p" % b['uuid'])
                            while ggg.forward():
                                for gggn in ggg.current()['p']:
                                    a = gggn.start_node()
                                    b = gggn.end_node()
                                    tc = list(gggn.types())[-1]
                                    ta, tb = list(a.labels())[0], list(b.labels())[0]
                                    if not optim:
                                        neograph.pull(b)
                                    if tb == 'Parameter':
                                        newparam = dict(b)
                                        newversion['parameters'][newparam['name']] = fromHtml(newparam['value'])
                                    if tc == 'NodeVersionToVariable':
                                        newvar = dict(b)
                                        newversion['variables'].append(newvar)
                                    if tb == 'Data':
                                        newdata = dict(b)
                                        newversion['data'][newdata['name']] = fromHtml(newdata['value'])

            if tc == 'GraphToVariable':
                if not b['name'] in [x['name'] for x in graphObject['variables']]:
                    newvar = dict(b)
                    graphObject['variables'].append(newvar)
            if tb == 'Group':
                newgroup = dict(b)
                graphObject['groups'].append(newgroup)

    if 'uuid' not in graphObject.keys():
        return None
    return graphObject


def setNodeAttr(node, **kwargs):
    """Set an object attributes.

    Parameters:
        node (Mgv object): the mangrove object.
        kwargs: dictionary to set the object values.
    Return:
        bool: True if object has been set.
    """
    if isinstance(node, dict):
        code = node['code']
        uuid = node['uuid']
    else:
        code = node.code
        uuid = node.uuid

    node = list(selector.select(code, uuid=uuid))
    if not len(node):
        print("no node type %s with uuid" % code, uuid, file=sys.__stderr__)
        return False
    node = node[0]
    for key in kwargs:
        node[key] = kwargs[key]
    neograph.push(node)
    return True


def getNodeAttr(node, attr):
    """Returns an object attribute.

    Parameters:
        node (Mgv object): the mangrove object.
        attr (str): the attribute name.
    Return:
        str: The object attribute.
        None: The object has not been found.
    """
    if isinstance(node, dict):
        code = node['code']
        uuid = node['uuid']
    else:
        code = node.code
        uuid = node.uuid

    g = neograph.run("MATCH (x:%s {uuid:'%s'}) RETURN x.%s" % (code, uuid, attr))
    for gn in g:
        return gn['x.%s' % attr]
    return None


def createLink(nodeA, nodeB):
    """Create a link between two node objects.

    This function can be empty. Used for optional complex database quieries.

    Parameters:
        nodeA (MgvNode): source node.
        nodeB (MgvNode): destination node.
    """
    a = list(selector.select(nodeA.code, uuid=nodeA.uuid))[0]
    b = list(selector.select(nodeB.code, uuid=nodeB.uuid))[0]
    r = Relationship(a, "Link", b)
    neograph.create(r)
    neograph.push(r)


def deleteLink(nodeA, nodeB):
    """Delete a link between two node objects.

    This function can be empty. Used for optional complex database quieries.

    Parameters:
        nodeA (MgvNode): source node.
        nodeB (MgvNode): destination node.
    """
    neograph.run("MATCH (:%s {uuid:'%s'})-[a]->(:%s {uuid:'%s'}) DETACH DELETE a" % (nodeA.code, nodeA.uuid, nodeB.code, nodeB.uuid))


def setDictionary(father, typeDic, name, value):
    """Set an node data or parameter.
    
    Parameters:
        father (MgvNode): the node.
        typeDic (str): type of the dictionary ("Parameter" or "Data").
        name (str): name of the entry.
        value (str): value of the entry.
    """
    c = neograph.run("MATCH (:%s {uuid:'%s'})-->(a:%s {name:'%s'}) SET a.value='%s'" % (father.code, father.uuid,
                                                                                        typeDic, name,
                                                                                        toHtml(value))).stats()
    if c['properties_set'] == 0:
        x = Node(typeDic, name=name, value=value)
        f = selector.select(father.code, uuid=father.uuid)
        f = list(f)[0]
        neograph.create(x)
        neograph.create(Relationship(f, "%sTo%s" % (father.code, typeDic), x))
        neograph.push(x)


def delDictionary(father, typeDic, name):
    """Delete an node data or parameter.

    Parameters:
        father (MgvNode): the node.
        typeDic (str): type of the dictionary ("Parameter" or "Data").
        name (str): name of the entry.
    """
    neograph.run("MATCH (:%s {uuid:'%s'})-->(a:%s {name:'%s'}) DETACH DELETE a" % (father.code, father.uuid, typeDic,
                                                                                   name)).stats()


def createNode(father, code, **kwargs):
    """Create a mangrove object in the database.
    
    Parameters:
        father (one of the mangrove classes): the parent mangrove object.
        code (str): the code of the classe, i.e. "Node" or "GraphTemplate".
        kwargs (dict): attributes of the object.
    Return:
        str: a new uuid.
    """
    id = str(uuid.uuid1())
    if 'uuid' not in kwargs.keys() or kwargs['uuid'] is None:
        kwargs['uuid'] = id
    if code == 'Node':
        n = Node(code, kwargs['typeName'], **kwargs)
    else:
        n = Node(code, **kwargs)
    if father:
        f = selector.select(father.code, uuid=father.uuid)
        f = list(f)[0]
        code = father.code+'To'+code
        neograph.create(Relationship(f, code, n))
    neograph.create(n)
    neograph.push(n)

    return kwargs['uuid']


def deleteNode(node):
    """Delete an object in the database and all its hierarchy."""
    neograph.run("MATCH (:%s {uuid:'%s'})-[*]->(a) DETACH DELETE a" % (node.code, node.uuid))
    neograph.run("MATCH (a:%s {uuid:'%s'}) DETACH DELETE a" % (node.code, node.uuid))


def deleteGraph(pattern, keys):
    """Delete a graph in the database and all its hierarchy."""
    neograph.run(
        "MATCH (:Pattern {uuid:'%s'})-->(:Graph {path:'%s'})-[*]->(a) DETACH DELETE a" % (pattern.uuid, ':'.join(keys)))
    neograph.run("MATCH (:Pattern {uuid:'%s'})-->(a:Graph {path:'%s'}) DETACH DELETE a" % (pattern.uuid, ':'.join(keys)))



def setLockType(type, user):
    """Set the lock property of a type with a user name.

    Parameters:
        type (MgvType): the type.
        user (str): the user name.
    """
    neograph.run("MATCH (x:Type {uuid:'%s'}) SET x.lock='%s'" % (type.uuid, user))


def getLockType(type):
    """Returns the lock property of a type.

    Parameters:
        type (MgvType): the type.
    Return:
        str: the lock value (user name) of the type.
        None: the type has not been found.
    """
    g = neograph.run("MATCH (x:Type {uuid:'%s'}) RETURN x.lock" % type.uuid)
    for gn in g:
        return gn['x.lock']
    return None


def syncProject(project):
    """Copy and replace all the project data, including patterns, contexts and
    templates, to the database."""
    # si pas dans la BDD:
    if not project.uuid:
        # creation dans la BDD
        project.create()
    else:
        # maj des attributs
        project.setName(project.getName())
        project.setVersionsPadding(project.getVersionsPadding())
        project.setVersionsStart(project.getVersionsStart())
        project.setScript(project.getScript())

    # pour chaque pattern de ce projet dans la BDD:
    g = neograph.run("MATCH (:Project {uuid:'%s'})-[:ProjectToPattern]->(x) RETURN x.uuid" % project.uuid)
    for x in g:
        # delete si pas dans la liste
        if str(x['x.uuid']) not in [str(p.uuid) for p in project.patterns]:
            neograph.run("MATCH (:Pattern {uuid:'%s'})-[*]->(a) DETACH DELETE a" % x['x.uuid'])
            neograph.run("MATCH (a:Pattern {uuid:'%s'}) DETACH DELETE a" % x['x.uuid'])

    # pour chaque context de ce projet dans la BDD:
    g = neograph.run("MATCH (:Project {uuid:'%s'})-[:ProjectToContext]->(x) RETURN x.uuid" % project.uuid)
    for x in g:
        # delete si pas dans la liste
        if str(x['x.uuid']) not in [str(p.uuid) for p in project.contexts]:
            neograph.run("MATCH (:Context {uuid:'%s'})-[*]->(a) DETACH DELETE a" % x['x.uuid'])
            neograph.run("MATCH (a:Context {uuid:'%s'}) DETACH DELETE a" % x['x.uuid'])

    # pour chaque context:
    for context in project.contexts:
        # si pas dans la BDD:
        if not context.uuid:
            # creation dans la BDD
            context.create()
        else:
            # maj des attributs
            context.setName(context.name)
            context.setValue(context.value)

    # pour chaque pattern:
    for pattern in project.patterns:
        # si pas dans la BDD:
        if not pattern.uuid:
            # creation dans la BDD
            pattern.create()
        else:
            # maj des attributs
            pattern.setName(pattern.name)
            pattern.setPattern(pattern.pattern)
            pattern.setOrder(pattern.order)
            pattern.setGraphName(pattern.graph_name)

        # pour chaque template de ce pattern dans la BDD:
        g = neograph.run("MATCH (:Pattern {uuid:'%s'})-[:PatternToTemplate]->(x) RETURN x.uuid" % pattern.uuid)
        for x in g:
            # delete si pas dans la liste
            if str(x['x.uuid']) not in [str(t.uuid) for t in pattern.templates]:
                neograph.run("MATCH (:GraphTemplate {uuid:'%s'})-[*]->(a) DETACH DELETE a" % x['x.uuid'])
                neograph.run("MATCH (a:GraphTemplate {uuid:'%s'}) DETACH DELETE a" % x['x.uuid'])
        # pour chaque template:
        for template in pattern.templates:
            # si pas dans la BDD:
            if not template.uuid:
                # creation dans la BDD
                template.create()
            else:
                # maj des attributs
                template.setName(template.name)
                template.setIcon(template.icon)
