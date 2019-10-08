from __future__ import print_function
import uuid
import json
import os
import time
import shutil

USER = os.getenv('USER')
if not USER:
    USER = os.getenv('USERNAME')


def connect(name=None, user=None, pwd=None):
    """Called at mangrove startup and used to set up global variables to access to the database.
    In this case the variable projects_file_path,which stores the path of the project data file."""
    global projects_file_path
    if name is None:
        home = os.getenv('HOME') if os.getenv('HOME') else os.getenv('USERPROFILE')
        localSettingsFile = os.path.join(home, 'mangrove1.0', 'settings.info')
        name, user, pwd = '', '', ''
        if os.path.exists(localSettingsFile):
            with open(localSettingsFile) as fid:
                dic = json.load(fid)
                choosen_wrapper = dic['wrapper']['current']
                name = dic['wrapper'][choosen_wrapper]['host']
    if not len(name):
        projects_file_path = None
    else:
        projects_file_path = os.path.join(name, 'projects.json')


def wait_lock_file(path):
    """Wait while a file exists.

    Wait 50 milliseconds between each test.
    Give up at the 10th attempt.
    """
    if not path:
        return
    lock_path = path + '_lock'
    c = 0
    while os.path.exists(lock_path) and c < 10:
        c = c + 1
        time.sleep(.5)
    if os.path.exists(lock_path):
        print("File", path, "seems frozen !")


def lock_file(path):
    """Create a lock file.

    Add the suffix "_lock" to the path.
    Il the file already exists, wait.
    Then create a file with this name and write the current user name in it.
    Wait 10 milliseconds and read the file.
    If the name read is the current user, return True, else try again.
    """
    wait_lock_file(path)
    lock_path = path + '_lock'
    with open(lock_path, 'w') as fid:
        fid.write(USER)
    time.sleep(.1)
    with open(lock_path) as fid:
        u = fid.read()
    if u == USER:
        return True
    else:
        lock_file(path)


def unlock_file(path):
    """Delete the lock file."""
    lock_path = path + '_lock'
    os.remove(lock_path)


def getFilePath(node, args=None):
    """Return the file path containing the node data."""
    if not node:
        return projects_file_path

    if node.code in ['Project', 'Pattern', 'Template', 'Context', 'Action', 'TypeParameter', 'Type', 'TypeVersion',
                     'TypeFile', 'Hud', 'BatchScript']:
        return projects_file_path

    elif node.code == 'Graph':
        graph = node
    elif node.code == 'Node':
        graph = node.graph
    elif node.code == 'NodeVersion':
        graph = node.node.graph
    elif node.code == 'Variable':
        graph = node.parent
        if graph.code == 'NodeVersion':
            graph = graph.node.graph

    if graph.path[-1] == '*template*':
        return os.path.join(os.path.dirname(projects_file_path), 'Templates', graph.pattern.project.name,
                            graph.pattern.name, graph.name + '.mgv')
    else:
        return graph.getFilePath()


def getByUuid(dico, uuid):
    """Dive in a dictionary and return an entry with a specific uuid."""
    if isinstance(dico, dict):
        for key in dico:
            if key == 'uuid' and dico[key] == uuid:
                return dico
            out = getByUuid(dico[key], uuid)
            if out:
                return out
    if isinstance(dico, list):
        for x in dico:
            out = getByUuid(x, uuid)
            if out:
                return out
    return None


def removeByUuid(dico, uuid, fromkey=None, parent=None):
    """Dive in a dictionary and delete an entry with a specific uuid."""
    if isinstance(dico, dict):
        for key in dico:
            if key == 'uuid' and dico[key] == uuid:
                if isinstance(parent, dict):
                    del parent[fromkey]
                else:
                    parent.remove(dico)
                return True
            out = removeByUuid(dico[key], uuid, fromkey=key, parent=dico)
            if out:
                return out
    if isinstance(dico, list):
        for x in dico:
            out = removeByUuid(x, uuid, parent=dico)
            if out:
                return out
    return False


def lockProject(project, user):
    """Set project lock property with user name if it's empty.

    Parameters:
        project (MgvProject): the project.
        user (str): the user name.
    Return:
        str: same user name if lock was empty, else lock value.
        """
    lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    lock = root[project.getName()]['lock']

    if lock in ['', user]:
        root[project.getName()]['lock'] = user
        with open(projects_file_path, 'w') as fid:
            fid.write(json.dumps(root, sort_keys=True, indent=4))
        unlock_file(projects_file_path)
        return user
    unlock_file(projects_file_path)
    return lock


def unlockProject(project):
    """Set project lock property to empty."""
    lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    if project.getName() in root:
        root[project.getName()]['lock'] = ''
    with open(projects_file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(projects_file_path)


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

    wait_lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    gt = None
    if uuid:
        gt = getByUuid(root, uuid)
    if name:
        for t in root[project_name]['types']:
            if t['name'] == name:
                gt = t
                break

    typeFiles = []
    for gf in gt['typeFiles']:
        typeFiles.append(mgvApi.MgvTypeFile(uuid=gf['uuid'], name=gf['name'], path=gf['path'],
                                            copy=gf['copy']))

    versions = []
    for gv in gt['versions']:
        actions = []
        params = []
        for ga in gv['actions']:
            actions.append(mgvApi.MgvAction(uuid=ga['uuid'], menu=ga['menu'], name=ga['name'],
                                            command=ga['command'], warning=ga['warning'],
                                            users=ga['users'], stack=ga['stack'], order=ga['order']))
        for gp in gv['parameters']:
            param = mgvApi.MgvParam(uuid=gp['uuid'], name=gp['name'], type=gp['type'],
                                    enum=gp['enum'], default=gp['default'], visibility=gp['visibility'],
                                    order=gp['order'], advanced=gp['advanced'])
            if param.type == "int":
                param.default = int(param.default)
            if param.type == "float":
                param.default = float(param.default)
            if param.type == "bool":
                param.default = str(param.default) in ["True", "true", "1"]
            params.append(param)
        versions.append(mgvApi.MgvTypeVersion(uuid=gv['uuid'], version_id=gv['id'], actions=actions,
                                              parameters=params, script=gv['script']))

    versionActive = -1
    if gt['versionActive'] in [x.id for x in versions]:
        versionActive = gt['versionActive']

    shapeVector = []
    if len(gt['shapeVector'].strip()):
        shapeVector = [[float(y) for y in x.split(',')] for x in gt['shapeVector'].split(';')]

    node_type = mgvApi.MgvType(uuid=gt['uuid'], name=gt['name'], category=gt['category'],
                               color=gt['color'], shape=gt['shape'], image=gt['image'],
                               context=gt['context'], help=gt['help'], width=gt['width'],
                               shapeVector=shapeVector, typeFiles=typeFiles, linkWith=gt['linkWith'].split(';'),
                               versions=versions, versionActive=versionActive, software=gt['software'])

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

    wait_lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    gt = None
    if uuid:
        gt = getByUuid(root, uuid)
    if name:
        for t in root[project_name]['huds']:
            if t['name'] == name:
                gt = t
                break

    node_type = mgvApi.MgvHud(uuid=gt['uuid'], name=gt['name'], event=gt['event'],
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

    wait_lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    gt = None
    if uuid:
        gt = getByUuid(root, uuid)
    if name:
        for t in root[project_name]['batchScripts']:
            if t['name'] == name:
                gt = t
                break

    node_type = mgvApi.MgvBatchScript(uuid=gt['uuid'], name=gt['name'], users=gt['users'],
                                      script=gt['script'], pattern=gt['pattern'], template=gt['template'])

    return node_type


def getTypes(projectName):
    """Returns a list of the project types.

    Parameters:
        projectName (str): the project name.
    Return:
        list of MgvType: a list of the types.
    """
    import mgvApi
    types = []
    wait_lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    if projectName not in root.keys():
        return []
    for gt in root[projectName]['types']:
        typeFiles = []
        for gf in gt['typeFiles']:
            typeFiles.append(mgvApi.MgvTypeFile(uuid=gf['uuid'], name=gf['name'], path=gf['path'],
                                                copy=gf['copy']))

        versions = []
        for gv in gt['versions']:
            actions = []
            params = []
            for ga in gv['actions']:
                actions.append(mgvApi.MgvAction(uuid=ga['uuid'], menu=ga['menu'], name=ga['name'],
                                                command=ga['command'], warning=ga['warning'],
                                                users=ga['users'], stack=ga['stack'], order=ga['order']))
            for gp in gv['parameters']:
                param = mgvApi.MgvParam(uuid=gp['uuid'], name=gp['name'], type=gp['type'],
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
            versions.append(mgvApi.MgvTypeVersion(uuid=gv['uuid'], version_id=gv['id'], actions=actions,
                                                  parameters=params, script=gv['script']))

        shapeVector = []
        if len(gt['shapeVector'].strip()):
            shapeVector = [[float(y) for y in x.split(',')] for x in gt['shapeVector'].split(';')]

        node_type = mgvApi.MgvType(uuid=gt['uuid'], name=gt['name'], category=gt['category'],
                                   color=gt['color'], shape=gt['shape'], typeFiles=typeFiles,
                                   image=gt['image'], context=gt['context'], help=gt['help'],
                                   width=gt['width'], shapeVector=shapeVector,
                                   linkWith=gt['linkWith'].split(';'), versions=versions,
                                   versionActive=gt['versionActive'], software=gt['software'])
        types.append(node_type)
    return types


def getProject(projectName):
    """Returns a MgvProject object from the database from its name."""
    import mgvApi
    wait_lock_file(projects_file_path)
    if not projects_file_path:
        return None
    with open(projects_file_path) as fid:
        root = json.load(fid)
    if projectName not in root.keys():
        return None
    pid = root[projectName]['uuid']
    name = root[projectName]['name']
    versions_padding = root[projectName]['versions_padding']
    versions_start = root[projectName]['versions_start']
    script = root[projectName]['script']
    contexts = []
    for gn in root[projectName]['contexts']:
        conid = gn['uuid']
        conname = gn['name']
        convalue = gn['value']
        pypcontext = mgvApi.MgvContext(uuid=conid, name=conname, value=convalue)
        contexts.append(pypcontext)
    batchs = []
    for gn in root[projectName]['batchScripts']:
        batid = gn['uuid']
        batname = gn['name']
        batscript = gn['script']
        batusers = gn['users']
        batpattern = gn['pattern']
        battemplate = gn['template']
        pypbatch = mgvApi.MgvBatchScript(uuid=batid, name=batname, script=batscript, users=batusers,
                                         pattern=batpattern, template=battemplate)
        batchs.append(pypbatch)
    huds = []
    for gn in root[projectName]['huds']:
        widid = gn['uuid']
        widname = gn['name']
        widscript = gn['script']
        widevent = gn['event']
        pyphud = mgvApi.MgvHud(uuid=widid, name=widname, script=widscript, event=widevent)
        huds.append(pyphud)
    types = getTypes(name)
    patterns = []
    for gn in root[projectName]['patterns']:
        patid = gn['uuid']
        patname = gn['name']
        pattern = gn['pattern']
        patorder = gn['order']
        graph_name = gn['graph_name']
        templates = []
        for gm in gn['templates']:
            temid = gm['uuid']
            temname = gm['name']
            temicon = gm['icon']
            pyptemplate = mgvApi.MgvGraphTemplate(uuid=temid, name=temname, icon=temicon)
            templates.append(pyptemplate)
        pyppattern = mgvApi.MgvPattern(uuid=patid, name=patname, pattern=pattern, templates=templates, order=patorder,
                                       graph_name=graph_name)
        patterns.append(pyppattern)

    p = mgvApi.MgvProject(uuid=pid, name=name, script=script, patterns=patterns, types=types, contexts=contexts,
                          batchScripts=batchs, huds=huds, versions_padding=versions_padding,
                          versions_start=versions_start)
    return p


def getProjectNames():
    """Returns the list of the projects's names."""
    if not projects_file_path:
        return []
    if not os.path.exists(projects_file_path):
        if not os.path.exists(os.path.dirname(projects_file_path)):
            os.makedirs(os.path.dirname(projects_file_path))
        with open(projects_file_path, 'w') as fid:
            fid.write('{}')
    wait_lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    return root.keys()


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
    wait_lock_file(projects_file_path)
    # retourne une liste d'elemets de type: [patternName,key0,..,keyN,shot_name]
    with open(projects_file_path) as fid:
        root = json.load(fid)
    p = getByUuid(root, pattern.uuid)
    if with_node_named is None and with_type_named is None:
        return [x.split(':') for x in p['graphs']]

    result = []
    for x in p['graphs']:
        keys = x.split(':')
        graph_file_path = os.path.join(pattern.convertPath(keys), pattern.convertGraphName(keys)) + '.mgv'
        with open(graph_file_path) as fid:
            root = json.load(fid)
        found = False
        if with_node_named:
            for y in root['nodes']:
                if with_node_named.lower() in y['name'].lower():
                    found = True
        if with_type_named:
            if not with_node_named or found:
                found = False
                for y in root['nodes']:
                    if y['typeName'] == with_type_named:
                        found = True
        if found:
            result.append(x.split(':'))
    return result


def getGraphInfo(pattern, keys):
    """Get a graph details from its path.

    Parameters:
        pattern (MgvPattern): the pattern.
        keys (list of str): path of the graph.
    Returns
        dict: a dictionary with a uuid value and a template_name value.
    """
    wait_lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    pat = [x for x in root[pattern.project.name]['patterns'] if x['name'] == pattern.name][0]
    gr = [x for x in pat['graphs'] if x == ':'.join(keys)]
    if not len(gr):
        return {}
    gr = gr[0]
    file_path = os.path.join(pattern.convertPath(keys), pattern.convertGraphName(keys) + '.mgv')
    wait_lock_file(file_path)
    with open(file_path) as fid:
        root = json.load(fid)

    return {'code': 'Graph', 'uuid': root['uuid'], 'template_name': root['template_name']}


def getGraphVars(pattern, keys):
    file_path = os.path.join(pattern.convertPath(keys), pattern.convertGraphName(keys) + '.mgv')
    if not os.path.exists(file_path):
        return []
    wait_lock_file(file_path)
    with open(file_path) as fid:
        root = json.load(fid)
    return root['variables']


def setGraphVar(pattern, keys, name, newname=None, value=None, active=None):
    file_path = os.path.join(pattern.convertPath(keys), pattern.convertGraphName(keys) + '.mgv')
    lock_file(file_path)
    with open(file_path) as fid:
        root = json.load(fid)
    if name in [x['name'] for x in root['variables']]:
        v = [x['name'] for x in root['variables'] if x['name'] == name][0]
        if value is not None:
            x['value'] = value
        if active is not None:
            x['active'] = active
        if newname is not None:
            x['name'] = newname
    else:
        newname = name if newname is None else newname
        value = '' if value is None else value
        active = True if active is None else active
        root['variables'].append({'name': newname, 'value': value, 'active': active})
    with open(file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(file_path)


def graphExists(pattern, graphpath):
    """Check if a graph exists in the database.

    Parameters:
        pattern (MgvPattern): the pattern.
        graphpath (list of str): the graph path.
    Return:
        bool: True if the graph exists.
    """
    graphpath = ':'.join(graphpath)
    wait_lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    p = getByUuid(root, pattern.uuid)
    for x in p['graphs']:
        if graphpath == x:
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
    if graph.path[-1] == '*template*':
        file_path = os.path.join(os.path.dirname(projects_file_path), 'Templates', graph.pattern.project.name,
                                 graph.pattern.name, graph.name + '.mgv')
    else:
        file_path = graph.getFilePath()
    if os.path.exists(file_path):
        wait_lock_file(file_path)
        with open(file_path) as fid:
            root = json.load(fid)
            return root
    else:
        graph.create()
    return None


def setNodeAttr(node, **kwargs):
    """Set an object attributes.

    Parameters:
        node (Mgv object): the mangrove object.
        kwargs: dictionary to set the object values.
    Return:
        bool: True if object has been set.
    """
    if isinstance(node, dict):
        uuid = node['uuid']
        file_path = node['path']
    else:
        uuid = node.uuid
        file_path = getFilePath(node)

    lock_file(file_path)
    with open(file_path) as fid:
        root = json.load(fid)
    t = getByUuid(root, uuid)
    for key in kwargs:
        t[key] = kwargs[key]
    with open(file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(file_path)
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
        uuid = node['uuid']
    else:
        uuid = node.uuid
    file_path = getFilePath(node)
    wait_lock_file(file_path)
    with open(file_path) as fid:
        root = json.load(fid)
    t = getByUuid(root, uuid)
    if attr in t:
        return t[attr]
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
    file_path = getFilePath(father)
    lock_file(file_path)
    with open(file_path) as fid:
        root = json.load(fid)
    t = getByUuid(root, father.uuid)
    t['parameters'][name] = value
    with open(file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(file_path)


def delDictionary(father, typeDic, name):
    """Delete an node data or parameter.

   Parameters:
       father (MgvNode): the node.
       typeDic (str): type of the dictionary ("Parameter" or "Data").
       name (str): name of the entry.
   """
    file_path = getFilePath(father)
    lock_file(file_path)
    with open(file_path) as fid:
        root = json.load(fid)
    t = getByUuid(root, father.uuid)
    del t['parameters'][name]
    with open(file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(file_path)


def createNode(father, code, **kwargs):
    """Create a mangrove object in the database.

    Parameters:
        father (one of the mangrove classes): the parent mangrove object.
        code (str): the code of the classe, i.e. "Node" or "Template".
        kwargs (dict): attributes of the object.
    Return:
        str: a new uuid.
    """
    id = str(uuid.uuid1())
    if 'uuid' not in kwargs.keys():
        kwargs['uuid'] = id
    elif kwargs['uuid'] is None:
        kwargs['uuid'] = id

    if father and code == 'Graph':
        if kwargs['path'].split(":")[-1] == '*template*':
            file_path = os.path.join(os.path.dirname(projects_file_path), 'Templates', father.getProject().name,
                                     father.name, kwargs['name'] + '.mgv')
        else:
            file_path = os.path.join(father.convertPath(kwargs['path'].split(':')), kwargs['name'] + '.mgv')
    else:
        file_path = getFilePath(father, kwargs)
    if code in ['Project', 'Pattern', 'GraphTemplate', 'Template', 'Context', 'Action', 'TypeParameter', 'Type',
                'TypeVersion', 'TypeFile', 'Hud', 'BatchScript']:
        lock_file(file_path)
        with open(file_path) as fid:
            root = json.load(fid)
        father_element = getByUuid(root, father.uuid) if father else None
        if code == 'Project':
            kwargs['types'] = []
            kwargs['patterns'] = []
            kwargs['contexts'] = []
            kwargs['huds'] = []
            kwargs['batchScripts'] = []
            root[kwargs['name']] = kwargs
        elif code == 'Pattern':
            kwargs['templates'] = []
            kwargs['graphs'] = []
            father_element['patterns'].append(kwargs)
        elif code == 'GraphTemplate' or code == 'Template':
            father_element['templates'].append(kwargs)
        elif code == 'Context':
            father_element['contexts'].append(kwargs)
        elif code == 'Hud':
            father_element['huds'].append(kwargs)
        elif code == 'BatchScript':
            father_element['batchScripts'].append(kwargs)
        elif code == 'Type':
            kwargs['versions'] = []
            kwargs['typeFiles'] = []
            father_element['types'].append(kwargs)
        elif code == 'TypeFile':
            father_element['typeFiles'].append(kwargs)
        elif code == 'TypeVersion':
            kwargs['actions'] = []
            kwargs['parameters'] = []
            father_element['versions'].append(kwargs)
        elif code == 'Action':
            father_element['actions'].append(kwargs)
        elif code == 'TypeParameter':
            father_element['parameters'].append(kwargs)
    else:
        if code == 'Graph':
            graph_dir = os.path.dirname(file_path)
            if not os.path.exists(graph_dir):
                os.makedirs(graph_dir)
            kwargs['nodes'] = []
            kwargs['groups'] = []
            kwargs['variables'] = []
            with open(file_path, 'w') as fid:
                fid.write(json.dumps(kwargs, sort_keys=True, indent=4))
            lock_file(projects_file_path)
            with open(projects_file_path) as fid:
                rootP = json.load(fid)
            if father.code == 'Pattern':
                p = getByUuid(rootP, father.uuid)
            if '*template*' not in kwargs['path']:
                p['graphs'].append(kwargs['path'])
            with open(projects_file_path, 'w') as fid:
                fid.write(json.dumps(rootP, sort_keys=True, indent=4))
            unlock_file(projects_file_path)

        lock_file(file_path)
        with open(file_path) as fid:
            root = json.load(fid)
        father_element = getByUuid(root, father.uuid) if father else None
        if code == 'Node':
            kwargs['versions'] = []
            kwargs['data'] = {}
            father_element['nodes'].append(kwargs)
        if code == 'NodeVersion':
            kwargs['variables'] = []
            kwargs['parameters'] = {}
            kwargs['data'] = {}
            father_element['versions'].append(kwargs)
        if code == 'Group':
            father_element['groups'].append(kwargs)
        if code == 'Variable':
            father_element['variables'].append(kwargs)

    with open(file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(file_path)

    return kwargs['uuid']


def deleteNode(node):
    """Delete an object in the database and all its hierarchy."""
    file_path = getFilePath(node)
    lock_file(file_path)
    with open(file_path) as fid:
        root = json.load(fid)
    removeByUuid(root, node.uuid)
    with open(file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(file_path)
    if node.code == 'Graph' and '*template*' not in node.path:
        lock_file(projects_file_path)
        with open(projects_file_path) as fid:
            rootP = json.load(fid)
        p = getByUuid(rootP, node.pattern.uuid)
        p['graphs'].remove(':'.join(node.path))
        with open(projects_file_path, 'w') as fid:
            fid.write(json.dumps(rootP, sort_keys=True, indent=4))
        unlock_file(projects_file_path)


def deleteGraph(pattern, keys):
    """Delete a graph in the database and all its hierarchy."""
    lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        rootP = json.load(fid)
    p = getByUuid(rootP, pattern.uuid)
    p['graphs'].remove(':'.join(keys))
    with open(projects_file_path, 'w') as fid:
        fid.write(json.dumps(rootP, sort_keys=True, indent=4))
    unlock_file(projects_file_path)



def setLockType(type, user):
    """Set the lock property of a type with a user name.

    Parameters:
        type (MgvType): the type.
        user (str): the user name.
    """
    lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    t = getByUuid(root, type.uuid)
    t['lock'] = user
    with open(projects_file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(projects_file_path)


def getLockType(type):
    """Returns the lock property of a type.

    Parameters:
        type (MgvType): the type.
    Return:
        str: the lock value (user name) of the type.
        None: the type has not been found.
    """
    wait_lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    t = getByUuid(root, type.uuid)
    return t['lock']


def syncProject(project):
    """Copy and replace all the project data, including patterns, contexts and
        templates, to the database."""
    lock_file(projects_file_path)
    with open(projects_file_path) as fid:
        root = json.load(fid)
    # si pas dans la BDD:
    if project.getName() not in root.keys():
        # creation dans la BDD
        root[project.getName()] = project.getJson()
        root[project.getName()]['uuid'] = str(uuid.uuid1())
        root[project.getName()]['contexts'] = []
        root[project.getName()]['patterns'] = []
        root[project.getName()]['huds'] = []
        root[project.getName()]['lock'] = ''
    else:
        # maj des attributs
        root[project.getName()]['name'] = project.name
        root[project.getName()]['script'] = project.script
        root[project.getName()]['versions_padding'] = project.versions_padding
        root[project.getName()]['versions_start'] = project.versions_start

    # pour chaque pattern de ce projet dans la BDD:
    for x in list(root[project.getName()]['patterns']):
        # delete si pas dans la liste
        if x['uuid'] not in [p.uuid for p in project.patterns]:
            root[project.getName()]['patterns'].remove(x)

    # pour chaque context de ce projet dans la BDD:
    for x in list(root[project.getName()]['contexts']):
        # delete si pas dans la liste
        if x['uuid'] not in [c.uuid for c in project.contexts]:
            root[project.getName()]['contexts'].remove(x)

    # pour chaque context:
    for context in project.contexts:
        # si pas dans la BDD:
        if not context.uuid:
            # creation dans la BDD
            c = context.getJson()
            c['uuid'] = str(uuid.uuid1())
            root[project.getName()]['contexts'].append(c)
        else:
            # maj des attributs
            c = [x for x in root[project.getName()]['contexts'] if x['uuid'] == context.uuid][0]
            c['name'] = context.name
            c['value'] = context.value

    # pour chaque pattern:
    for pattern in project.patterns:
        # si pas dans la BDD:
        if not pattern.uuid:
            # creation dans la BDD
            p = pattern.getJson()
            p['uuid'] = str(uuid.uuid1())
            pattern.uuid = p['uuid']
            p['graphs'] = []
            p['templates'] = []
            root[project.getName()]['patterns'].append(p)
        else:
            # maj des attributs
            p = [x for x in root[project.getName()]['patterns'] if x['uuid'] == pattern.uuid][0]
            p['name'] = pattern.name
            p['pattern'] = pattern.pattern
            p['order'] = pattern.order
            p['graph_name'] = pattern.graph_name

        # pour chaque template de ce pattern dans la BDD:
        p = [x for x in root[project.getName()]['patterns'] if x['uuid'] == pattern.uuid]
        if len(p):
            p = p[0]
            for x in list(p['templates']):
                # delete si pas dans la liste
                if x['uuid'] not in [t.uuid for t in pattern.templates]:
                    p['templates'].remove(x)

        # pour chaque template:
        for template in pattern.templates:
            # si pas dans la BDD:
            if not template.uuid:
                # creation dans la BDD
                p = [x for x in root[project.getName()]['patterns'] if x['uuid'] == pattern.uuid][0]
                t = template.getJson()
                t['uuid'] = str(uuid.uuid1())
                p['templates'].append(t)
            else:
                # maj des attributs
                t = [x for x in p['templates'] if x['uuid'] == template.uuid][0]
                t['name'] = template.name
                t['icon'] = template.icon

    with open(projects_file_path, 'w') as fid:
        fid.write(json.dumps(root, sort_keys=True, indent=4))
    unlock_file(projects_file_path)