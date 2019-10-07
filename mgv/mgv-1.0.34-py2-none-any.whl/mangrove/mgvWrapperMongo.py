from __future__ import print_function
import uuid
import json
import sys
import os
from six import string_types
from pymongo import MongoClient


def connect(name=None, user=None, pwd=None):
    """Called at mangrove startup and used to set up global variables to access to the database.
    In this case the variable db, which stores the mongo connection."""
    global db
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
    client = MongoClient(name, username=user, password=pwd)
    db = client['mangrove']


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
    p = db[project.name].find_one({'_id': project.uuid})
    if p['lock'] in ['', user]:
        p['lock'] = user
        db[project.name].update_one({'_id': project.uuid}, {'$set': {'lock': user}}, upsert=False)
        return user
    return p['lock']


def unlockProject(project):
    """Set project lock property to empty."""
    db[project.name].update_one({'_id': project.uuid}, {'$set': {'lock': ''}}, upsert=False)


def getType(project_name, name=None, uuid=None):
    """Return a MgvType object from the database.

    Uuid or name has to be provided.

    Parameters:
        project_name (str): the name of the project.
        name (str): the name of the type (optional).
        uuid (str): the uuid of the type (optional).
    Return:
        MgvType: the type."""
    import mgvApi
    if not name and not uuid:
        return None
    pid = db[project_name].find_one({'code': 'Project', 'name': project_name}, {"_id": 1})['_id']
    if uuid:
        gt = db[project_name].find_one({'code': 'Type', 'parent': pid, '_id': uuid})
    if name:
        gt = db[project_name].find_one({'code': 'Type', 'parent': pid, 'name': name})

    typeFiles = []
    for gf in db[project_name].find({'code': 'TypeFile', 'parent': gt['_id']}):
        typeFiles.append(mgvApi.MgvTypeFile(uuid=gf['_id'], name=gf['name'], path=gf['path'],
                                            copy=gf['copy']))

    versions = []
    for gv in db[project_name].find({'code': 'TypeVersion', 'parent': gt['_id']}):
        actions = []
        params = []
        for ga in db[project_name].find({'code': 'Action', 'parent': gv['_id']}):
            actions.append(mgvApi.MgvAction(uuid=ga['_id'], menu=ga['menu'], name=ga['name'],
                                            command=ga['command'], warning=ga['warning'],
                                            users=ga['users'], stack=ga['stack'], order=ga['order']))
        for gp in db[project_name].find({'code': 'TypeParameter', 'parent': gv['_id']}):
            param = mgvApi.MgvParam(uuid=gp['_id'], name=gp['name'], type=gp['type'],
                                    enum=gp['enum'], default=gp['default'],
                                    visibility=gp['visibility'], order=gp['order'],
                                    advanced=gp['advanced'])
            if param.type == "int":
                param.default = int(param.default)
            if param.type == "float":
                param.default = float(param.default)
            if param.type == "bool":
                param.default = str(param.default) in ["True", "true", "1"]
            params.append(param)

        v = mgvApi.MgvTypeVersion(uuid=gv['_id'], version_id=gv['id'], actions=actions,
                                  parameters=params, script=gv['script'])
        versions.append(v)

    shapeVector = []
    if len(gt['shapeVector'].strip()):
        shapeVector = [[float(y) for y in x.split(',')] for x in gt['shapeVector'].split(';')]

    if gt['versionActive'] is None:
        gt['versionActive'] = -1

    node_type = mgvApi.MgvType(uuid=gt['_id'], name=gt['name'], category=gt['category'], color=gt['color'],
                               shape=gt['shape'], typeFiles=typeFiles, image=gt['image'], context=gt['context'],
                               help=gt['help'], width=gt['width'], shapeVector=shapeVector, software=gt['software'],
                               linkWith=gt['linkWith'].split(';'), versions=versions, versionActive=gt['versionActive'])
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
    import mgvApi
    if not name and not uuid:
        return None
    pid = db[project_name].find_one({'code': 'Project', 'name': project_name}, {"_id": 1})['_id']
    if uuid:
        gt = db[project_name].find_one({'code': 'Hud', 'parent': pid, '_id': uuid})
    if name:
        gt = db[project_name].find_one({'code': 'Hud', 'parent': pid, 'name': name})

    node_type = mgvApi.MgvHud(uuid=gt['_id'], name=gt['name'], event=gt['event'],
                                 script=gt['script'])
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
    import mgvApi
    if not name and not uuid:
        return None
    pid = db[project_name].find_one({'code': 'Project', 'name': project_name}, {"_id": 1})['_id']
    if uuid:
        gt = db[project_name].find_one({'code': 'BatchScript', 'parent': pid, '_id': uuid})
    if name:
        gt = db[project_name].find_one({'code': 'BatchScript', 'parent': pid, 'name': name})

    node_type = mgvApi.MgvBatchScript(uuid=gt['_id'], name=gt['name'], users=gt['users'],
                                      script=gt['script'], pattern=gt['pattern'], template=gt['template'])
    return node_type


def getTypes(project_name):
    """Returns a list of the project types.

    Parameters:
        project_name (str): the project name.
    Return:
        list of MgvType: a list of the types.
    """
    import mgvApi
    types = []
    pid = db[project_name].find_one({'code': 'Project', 'name': project_name}, {"_id": 1})['_id']
    for gt in db[project_name].find({'code': 'Type', 'parent': pid}):
        typeFiles = []
        for gf in db[project_name].find({'code': 'TypeFile', 'parent': gt['_id']}):
            typeFiles.append(mgvApi.MgvTypeFile(uuid=gf['_id'], name=gf['name'], path=gf['path'],
                                                copy=gf['copy']))

        versions = []
        for gv in db[project_name].find({'code': 'TypeVersion', 'parent': gt['_id']}):
            actions = []
            params = []
            for ga in db[project_name].find({'code': 'Action', 'parent': gv['_id']}):
                actions.append(mgvApi.MgvAction(uuid=ga['_id'], menu=ga['menu'], name=ga['name'],
                                                command=ga['command'], warning=ga['warning'],
                                                users=ga['users'], stack=ga['stack'], order=ga['order']))
            for gp in db[project_name].find({'code': 'TypeParameter', 'parent': gv['_id']}):
                param = mgvApi.MgvParam(uuid=gp['_id'], name=gp['name'], type=gp['type'],
                                        enum=gp['enum'], default=gp['default'],
                                        visibility=gp['visibility'], order=gp['order'],
                                        advanced=gp['advanced'])
                if param.type == "int":
                    param.default = int(param.default)
                if param.type == "float":
                    param.default = float(param.default)
                if param.type == "bool":
                    param.default = str(param.default) in ["True", "true", "1"]
                params.append(param)

            v = mgvApi.MgvTypeVersion(uuid=gv['_id'], version_id=gv['id'], actions=actions,
                                      parameters=params, script=gv['script'])
            versions.append(v)

        shapeVector = []
        if len(gt['shapeVector'].strip()):
            shapeVector = [[float(y) for y in x.split(',')] for x in gt['shapeVector'].split(';')]

        if gt['versionActive'] is None:
            gt['versionActive'] = -1

        node_type = mgvApi.MgvType(uuid=gt['_id'], name=gt['name'], category=gt['category'], color=gt['color'],
                                   shape=gt['shape'], typeFiles=typeFiles, image=gt['image'], context=gt['context'],
                                   help=gt['help'], width=gt['width'], shapeVector=shapeVector, software=gt['software'],
                                   linkWith=gt['linkWith'].split(';'), versions=versions,
                                   versionActive=gt['versionActive'])
        types.append(node_type)

    return types


def getProject(project_name):
    """Returns a MgvProject object from the database from its name."""
    import mgvApi
    gproj = db[project_name].find_one({'code': 'Project', 'name': project_name})
    if gproj:
        pid = gproj['_id']
        name = gproj['name']
        versions_padding = gproj['versions_padding']
        versions_start = gproj['versions_start']
        if not versions_padding:
            versions_padding, versions_start = 3, 0
        script = gproj['script']
        contexts = []
        for gn in db[project_name].find({'code': 'Context', 'parent': pid}):
            conid = gn['_id']
            conname = gn['name']
            convalue = gn['value']
            pypcontext = mgvApi.MgvContext(uuid=conid, name=conname, value=convalue)
            contexts.append(pypcontext)
        batchs = []
        for gn in db[project_name].find({'code': 'BatchScript', 'parent': pid}):
            batid = gn['_id']
            batname = gn['name']
            batscript = gn['script']
            batusers = gn['users']
            batpattern = gn['pattern']
            battemplate = gn['template']
            pypbatch = mgvApi.MgvBatchScript(uuid=batid, name=batname, script=batscript, users=batusers,
                                             pattern=batpattern, template=battemplate)
            batchs.append(pypbatch)
        huds = []
        for gn in db[project_name].find({'code': 'Hud', 'parent': pid}):
            widid = gn['_id']
            widname = gn['name']
            widscript = gn['script']
            widevent = gn['event']
            pyphud = mgvApi.MgvHud(uuid=widid, name=widname, script=widscript, event=widevent)
            huds.append(pyphud)
        types = getTypes(name)

        patterns = []
        for gn in db[project_name].find({'code': 'Pattern', 'parent': pid}):
            patid = gn['_id']
            patname = gn['name']
            pattern = gn['pattern']
            patorder = gn['order']
            graph_name = gn['graph_name']
            templates = []
            for gm in db[project_name].find({'code': 'GraphTemplate', 'parent': patid}):
                temid = gm['_id']
                temname = gm['name']
                temicon = gm['icon']
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
    return db.list_collection_names()


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
    type_uuid = None
    if with_type_named:
        type_uuids = [x.uuid for x in pattern.project.types if x.name == with_type_named]
        if len(type_uuids):
            type_uuid = type_uuids[0]

    result = []
    for a in db[pattern.project.name].find({'code': 'Graph', 'parent': pattern.uuid}):
        if with_node_named:
            with_node_named = with_node_named.replace('*', '.*').replace('?', '.')
            with_node_named = '^' + with_node_named + '$'
            if not db[pattern.project.name].find_one({'code': 'Node', 'parent': a['_id'],
                                                      'name': {'$regex': '(?i)%s(?-i)' % with_node_named}}):
                continue
        if type_uuid:
            if not db[pattern.project.name].find_one({'code': 'Node', 'typeUuid': type_uuid}):
                continue
        result.append(a['path'].split(':'))

    return result


def getGraphInfo(pattern, keys):
    """Get a graph details from its path.

    Parameters:
        pattern (MgvPattern): the pattern.
        keys (list of str): path of the graph from the pattern name to its name.
    Returns
        dict: a dictionary with a uuid value and a template_name value.
    """
    project_name = pattern.project.name
    try:
        pid = db[project_name].find_one({'code': 'Pattern', 'name': pattern.name, 'parent': pattern.project.uuid},
                                        {"_id": 1})['_id']
        g = db[project_name].find_one({'code': 'Graph', 'parent': pid, 'path': ':'.join(keys)},
                                      {'template_name': 1})
        return {'code': 'Graph', 'uuid': g['_id'], 'template_name': g['template_name']}
    except:
        return {}


def getGraphVars(pattern, keys):
    project = pattern.project
    pid = db[project.name].find_one({'code': 'Pattern', 'name': pattern.name, 'parent': project.uuid},
                                    {"_id": 1})['_id']
    gid = db[project.name].find_one({'code': 'Graph', 'parent': pid, 'path': ':'.join(keys)},
                                    {'_id': 1})
    if gid is None:
        return []
    gid = gid['_id']
    result = []
    for v in db[project.name].find({'code': 'Variable', 'parent': gid}):
        v['uuid'] = v['_id']
        del v['_id']
        result.append(v)
    return result


def setGraphVar(pattern, keys, name, newname=None, value=None, active=None):
    project = pattern.project
    pid = db[project.name].find_one({'code': 'Pattern', 'name': pattern.name, 'parent': project.uuid},
                                    {"_id": 1})['_id']
    gid = db[project.name].find_one({'code': 'Graph', 'parent': pid, 'path': ':'.join(keys)},
                                    {'_id': 1})['_id']
    v = db[project.name].find_one({'code': 'Variable', 'name': name, 'parent': gid}, {'_id': 1})
    if v:
        if value is not None:
            db[project.name].update_one({'code': 'Variable', 'name': name, 'parent': gid}, {'$set': {'value': value}})
        if active is not None:
            db[project.name].update_one({'code': 'Variable', 'name': name, 'parent': gid}, {'$set': {'active': active}})
        if newname is not None:
            db[project.name].update_one({'code': 'Variable', 'name': name, 'parent': gid}, {'$set': {'name': newname}})
    else:
        newname = name if newname is None else newname
        value = '' if value is None else value
        active = True if active is None else active
        db[project.name].insert_one({'code': 'Variable', 'name': newname, 'parent': gid, 'value': value, 'active': active})


def graphExists(pattern, keys):
    """Check if a graph exists in the database.

    Parameters:
        pattern (MgvPattern): the pattern.
        keys (list of str): the graph path from the pattern name
                                 to the last key.
    Return:
        bool: True if the graph exists.
    """
    g = db[pattern.project.name].find_one({'code': 'Graph', 'path': ':'.join(keys), 'parent': pattern.uuid})
    if g:
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
    project_name = graph.getProject().name
    graphObject = {'nodes': [], 'variables': [], 'groups': []}
    if graph.path[-1] == '*template*':
        pid = db[project_name].find_one({'code': 'GraphTemplate', 'name': graph.getName(), 'parent': graph.pattern.uuid},
                                        {'_id': 1})['_id']
        g = db[project_name].find_one({'code': 'Graph', 'name': graph.getName(), 'parent': pid}, {'template_name': 1})
    elif graph.uuid:
        g = db[project_name].find_one({'code': 'Graph', '_id': graph.uuid}, {'template_name': 1})
    else:
        g = db[project_name].find_one({'code': 'Graph', 'name': graph.getName(), 'path': ':'.join(graph.path),
                                       'parent': graph.pattern.uuid}, {'template_name': 1})

    if g is None:
        return None
    graphObject['uuid'] = g['_id']
    graphObject['template_name'] = g['template_name']
    graphObject['variables'] = []
    graphObject['groups'] = []
    for data in db[project_name].find({'parent': g['_id']}):
        if data['code'] == 'Variable':
            data['uuid'] = data['_id']
            graphObject['variables'].append(data)
        if data['code'] == 'Group':
            data['uuid'] = g['_id']
            graphObject['groups'].append(data)
        if data['code'] == 'Node':
            data['uuid'] = data['_id']
            graphObject['nodes'].append(data)
            data['versions'] = []
            data['data'] = {}
            for d in db[project_name].find({'code': 'Data', 'parent': data['_id']}):
                d['uuid'] = d['_id']
                data['data'][d['name']] = fromHtml(d['value'])
            for v in db[project_name].find({'code': 'NodeVersion', 'parent': data['_id']}):
                v['uuid'] = v['_id']
                data['versions'].append(v)
                v['parameters'] = {}
                v['data'] = {}
                v['variables'] = []
                for p in db[project_name].find({'parent': v['_id']}):
                    if p['code'] == 'Parameter':
                        p['uuid'] = p['_id']
                        v['parameters'][p['name']] = fromHtml(p['value'])
                    if p['code'] == 'Data':
                        p['uuid'] = p['_id']
                        v['data'][p['name']] = fromHtml(p['value'])
                    if p['code'] == 'Variable':
                        p['uuid'] = p['_id']
                        v['variables'].append(p)
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
        project_name = node['project_name']
    else:
        code = node.code
        uuid = node.uuid
        project_name = node.name if node.code == 'Project' else node.getProject().name

    if not db[project_name].find_one({'code': code, '_id': uuid}):
        print("no node type %s with uuid" % code, uuid, file=sys.__stderr__)
        return False

    db[project_name].update_one({'code': code, '_id': uuid}, {"$set": kwargs})
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
        project_name = node['project_name']
    else:
        code = node.code
        uuid = node.uuid
        project_name = node.name if node.code == 'Project' else node.getProject().name

    obj = db[project_name].find_one({'code': code, '_id': uuid}, {'_id': 0, attr: 1})
    if attr in obj:
        return obj[attr]
    return ''


def createLink(nodeA, nodeB):
    """Create a link between two node objects.

    This function can be empty. Used for optional complex database quieries.

    Parameters:
        nodeA (MgvNode): source node.
        nodeB (MgvNode): destination node.
    """
    return


def deleteLink(nodeA, nodeB):
    """Delete a link between two node objects.

    This function can be empty. Used for optional complex database quieries.

    Parameters:
        nodeA (MgvNode): source node.
        nodeB (MgvNode): destination node.
    """
    return


def setDictionary(father, typeDic, name, value):
    """Set an node data or parameter.

    Parameters:
        father (MgvNode): the node.
        typeDic (str): type of the dictionary ("Parameter" or "Data").
        name (str): name of the entry.
        value (str): value of the entry.
    """
    db[father.getProject().name].update_one({'code': typeDic, 'parent': father.uuid, 'name': name},
                                            {"$set": {"value": toHtml(value)}}, upsert=True)


def delDictionary(father, typeDic, name):
    """Delete an node data or parameter.

    Parameters:
        father (MgvNode): the node.
        typeDic (str): type of the dictionary ("Parameter" or "Data").
        name (str): name of the entry.
    """
    db[father.getProject().name].delete_one({'code': typeDic, 'parent': father.uuid, 'name': name})


def createNode(father, code, **kwargs):
    """Create a mangrove object in the database.

    Parameters:
        father (one of the mangrove classes): the parent mangrove object.
        code (str): the code of the classe, i.e. "Node" or "GraphTemplate".
        kwargs (dict): attributes of the object.
    Return:
        str: a new uuid.
    """
    kwargs['code'] = code
    id = str(uuid.uuid1())
    if 'uuid' not in kwargs.keys() or kwargs['uuid'] is None:
        kwargs['_id'] = id
    else:
        kwargs['_id'] = kwargs['uuid']
        del kwargs['uuid']

    if father:
        kwargs['parent'] = father.uuid
        project_name = father.getProject().name
    else:
        project_name = kwargs['name']
        db[project_name]
    db[project_name].insert_one(kwargs)

    return kwargs['_id']


def deleteNode(node):
    """Delete an object in the database and all its hierarchy."""
    if node.code == 'Project':
        db[node.name].drop()
    else:
        deleteNodeRecurs(node.getProject(), node.uuid)


def deleteNodeRecurs(project, pid):
    """This function isn't called by mangrove and is used
    in the mongo wrapper only."""
    db[project.name].delete_one({'_id': pid})
    children = db[project.name].find({'parent': pid}, {'_id': 1})
    for child in children:
        deleteNodeRecurs(project, child['_id'])


def deleteGraph(pattern, keys):
    """Delete a graph in the database and all its hierarchy."""
    pid = db[pattern.project.name].find_one({'code': 'Pattern', 'name': pattern.name, 'parent': pattern.project.uuid},
                                    {"_id": 1})['_id']
    gid = db[pattern.project.name].find_one({'code': 'Graph', 'parent': pid, 'path': ':'.join(keys)}, {'_id': 1})['_id']
    deleteNodeRecurs(pattern.project, gid)


def setLockType(type, user):
    """Set the lock property of a type with a user name.

    Parameters:
        type (MgvType): the type.
        user (str): the user name.
    """
    db[type.getProject().name].update_one({'code': 'Type', '_id': type.uuid}, {"$set": {"lock": user}})


def getLockType(type):
    """Returns the lock property of a type.

    Parameters:
        type (MgvType): the type.
    Return:
        str: the lock value (user name) of the type.
        None: the type has not been found.
    """
    return db[type.getProject().name].find_one({'code': 'Type', '_id': type.uuid}, {'lock': 1})['lock']


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
    g = db[project.name].find({'code': 'Pattern', 'parent': project.uuid})
    for x in g:
        # delete si pas dans la liste
        if str(x['_id']) not in [str(p.uuid) for p in project.patterns]:
            deleteNodeRecurs(project, x['_id'])

    # pour chaque context de ce projet dans la BDD:
    g = db[project.name].find({'code': 'Context', 'parent': project.uuid})
    for x in g:
        # delete si pas dans la liste
        if str(x['_id']) not in [str(p.uuid) for p in project.contexts]:
            deleteNodeRecurs(project, x['_id'])

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
        g = db[project.name].find({'code': 'GraphTemplate', 'parent': pattern.uuid})
        for x in g:
            # delete si pas dans la liste
            if str(x['_id']) not in [str(t.uuid) for t in pattern.templates]:
                deleteNodeRecurs(project, x['_id'])
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
