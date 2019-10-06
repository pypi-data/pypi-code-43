import os
import sys
import json
import logging

import requests
import yaml
from IPython.core.display import HTML

from pygments import highlight, lexers, formatters

from mergetb.term import green, gray, red, blue, cyan, orange, neutral


log = logging.getLogger(__name__)

this = sys.modules[__name__]
this.accessToken = ''
this.api = 'api.mergetb.net'


# =============================================================================
# Developer beware
# !!!!!!!!!!!!!!!!
#
# This librabry will always check for valid SSL certs coming from the API. This
# means that for development, you'll need to import the certificate authority
# cert (not the API cert!) that signed the API cert. If you are using the raven
# development environment this cert is at [px0,px1]:/etc/merge/keys/ca.pem. You
# can instruct requests to honor this cert by setting the environment variable
#
#       REQUESTS_CA_BUNDLE=/<path>/<to>/ca.pem
#
# =============================================================================

# Users ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_users():
    """List users"""
    return do_get('users')

def user_info(user):
    """Get user info

    :param user: user to get info for
    """
    return do_get('users/'+user)

def update_user(user, email, mode):
    """Update user info

    :param user: username to update
    :param email: new user email
    :param mode: access mode (one of public, protected, or private)
    """
    if mode not in ['public', 'protected', 'private']:
        return 400  # bad request.

    return do_post('users/'+user, {
        'username': user,
        'email': email,
        'accessMode': mode,
    })

def user_delete(user):
    """Delete a user

    :param user: user to delete
    """
    return do_delete('users/'+user, None)

def user_vtoken(user):
    """Get a users validation token

    :param user: user to fetch token for
    """
    return do_get('users/'+user+'/validation_token')

def user_validate(user, token):
    """Validate a user

    :param user: user to validate
    :param token: token to validate with
    """
    return do_post('users/'+user+'/validation_token', {'token': token})

# Sites ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_sites():
    '''List Sites'''

    response = do_get('sites')

    # dont dump the model in the response
    for site in response:
        if 'model' in site:
            del site['model']

    return response

def get_site(name):
    """Get site data

    :param name: site name
    """

    filename = "{}.json".format(name)
    data = do_get('sites/'+name)
    try:
        with open(filename, "w") as f:
            f.write(data["model"])

        print("wrote model to {}".format(filename))

    except OSError as e:
        print("failed to write model {}".format(e))

    del data['model']
    return data


def new_site(name, fqdn, path):
    """Create a new site

    :param name: new site name
    :param fqdn: new site fully qualified domain name
    :param path: path to file which containes site XIR model (json format)
    """

    try:
        with open(path) as fd:
            # GTL TODO: sanitize input.
            model = fd.read()
    except (OSError, ValueError):
        # log this as warn
        return 500

    return do_put('sites/'+name, {
        'name': name,
        'address': fqdn,
        'model': model
    })

def delete_site(name):
    """Delete a site

    :param name: site name to delete
    """

    return do_delete('sites/'+name, None)

def set_site_cert(name, cert):
    """Set a sites certificate

    :param name: site name
    :param cert: TLS certificate file to set
    """

    with open(cert) as fd:
        data = fd.read()
        return do_post('sites/'+name+'/cert', {
            'cert': data
        })
    return None

def activate_resources(site, resources):
    """Activate a set of resouces

    :param site: site in which to activate resources
    :param resources: resources to activate, comma separated a,b,c
    """

    return do_post('sites/'+site+'/activate', resources.split(","))

def deactivate_resources(site, resources):
    """Deactivate a set of resouces

    :param site: site in which to deactivate resources
    :param resources: resources to deactivate, comma separated a,b,c
    """

    return do_post('sites/'+site+'/deactivate', resources.split(","))


def set_site_wgd_config(name, cert, endpoint):
    """Set a sites wireguard daemon configuration

    :param name: site name
    :param cert: TLS certificate of the wireguard daemon
    :param endpoint: Endpoint of wireguard daemon on the site, in name:port format.
    """

    with open(cert) as fd:
        data = fd.read()
        return do_post('sites/'+name+'/wgdconfig', {
            'cert': data,
            'address': endpoint,
        })
    return None

# Health/Status ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def health():
    '''Show health of Merge API'''
    return do_get('health')

# Account Mangement ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def account_init():
    """Ensure my account is initialized"""
    return do_get('user/init')

def account_delete(name):
    """Delete a user account"""
    return do_delete('users/'+name, None)

# Projects ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_projects():
    '''List Projects user is authorized to view.'''
    return do_get('projects')

def new_project(pid, desc, mode):
    """Define a new project

    :param pid:  new project id
    :param desc: new project description
    :param mode: access mode (one of public, protected, or private)
    """
    return do_put('projects/'+pid, {
        'name': pid,
        'description': desc,
        'accessMode': mode
    })

def update_project(pid, desc, mode):
    """Update a project

    :param pid:  project id
    :param desc: new project description
    :param mode: access mode (one of public, protected, or private)
    """
    return do_post('projects/'+pid, {
        'name': pid,
        'description': desc,
        'accessMode': mode,
    })

def delete_project(pid):
    """Delete a project

    :param pid:  new project id
    """

    return do_delete('projects/'+pid, None)

def project_info(pid):
    """Get information about the given project

    :param pid: project id
    """
    return do_get('projects/'+pid)

def project_experiments(pid):
    """Get project experiments

    :param pid: project id
    """

    return do_get('/projects/'+pid+'/experiments')

def project_members(pid):
    """Get project members

    :param pid: project id
    """

    return do_get('/projects/'+pid+'/members')

def project_member(pid, mid):
    """Get project member

    :param pid: project id
    :param mid: member id
    """

    return do_get('/projects/'+pid+'/members/'+mid)

def project_add_member(pid, mid, role, state):
    """Get project member

    :param pid: project id
    :param mid: member id
    :param role: member role
    :param state: member state
    """

    return do_put('/projects/'+pid+'/members/'+mid, {
        'member': mid,
        'project': pid,
        'role': role,
        'state': state,
    })

def project_update_member(pid, mid, role, state):
    """Get project member

    :param pid: project id
    :param mid: member id
    :param role: member role
    :param state: member state
    """

    return do_post('/projects/'+pid+'/members/'+mid, {
        'member': mid,
        'project': pid,
        'role': role,
        'state': state,
    })

def project_delete_member(pid, mid):
    """Get project member

    :param pid: project id
    :param mid: member id
    """

    return do_delete('/projects/'+pid+'/members/'+mid, None)

# Experiments ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_experiments(pid):
    """List the experiments of a project

    :param pid:  project to which experiments belong
    """

    return do_get('/projects/'+pid+'/experiments')

def new_experiment(pid, eid, desc):
    """Define a new experiment

    :param pid: existing project id
    :param eid: new experiment id
    :param desc: new experiment description
    """

    return do_put('projects/'+pid+'/experiments/'+eid, {
        'name': eid,
        'description': desc
    })

def delete_experiment(pid, eid):
    """Delete an experiment

    :param pid: project id
    :param eid: experiment id
    """

    return do_delete('projects/'+pid+'/experiments/'+eid, None)

def update_experiment(pid, eid, desc):
    """Update an experiments information.

    :param pid:  project id
    :param eid:  experiment id
    :param desc: new project description
    """
    return do_post('/projects/{}/experiments/{}'.format(pid, eid), {
        'name': eid,
        'description': desc,
    })

def push_experiment(pid, eid, xir):
    """Push a new version of the experiment source code

    :param pid: project id
    :param eid: experiment id
    :param src: the experiment model
    """

    return do_post('projects/'+pid+'/experiments/'+eid+'/src', {
        'xir': xir
    })

def pull_experiment(pid, eid, hsh):
    """Pull the specified version of the experiment source code

    :param pid:  project id
    :param eid:  experiment id
    :param hash: experiment version hash
    """

    data = do_get('projects/'+pid+'/experiments/'+eid+'/src/'+hsh)
    s = "{}: {}\n".format(green("pushDate"), data["pushDate"])
    s += "{}: {}\n".format(green("who"), data["who"])
    xir = json.loads(data["xir"])
    s += highlight(
        json.dumps(xir, indent=2),
        lexers.JsonLexer(),
        formatters.Terminal256Formatter(bg="dark")
    )
    return s


def push_experiment_file(pid, eid, path):
    """Push a new version of the experiment source code

    :param pid: project id
    :param eid: experiment id
    :param path: the path to the experiment model file to push
    """
    with open(path) as fd:
        xir = fd.read()
        return do_post('projects/'+pid+'/experiments/'+eid+'/src', {
            'xir': xir
        })
    return None

def experiment_history(pid, eid):
    """Get the experiment version history

    :param pid: project id
    :param eid: experiment id
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/src')

def experiment_info(pid, eid):
    """Get information about the given experiment

    :param pid: project id
    :param eid: experiment id
    """
    return do_get('projects/'+pid+'/experiments/'+eid)

# Realizations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def realize(pid, eid, name, hsh):
    """Realize an experiment.

    On success the resources that underpin the realization will be yours for
    the next 47 seconds. Use accept() on the realization hash id to claim the
    realization until you decide to explicitly release it or the maximum lease
    on the resources runs up. Alternatively use reject() to free the resources
    and destroy the realization immediately.

    :param pid: project id
    :param eid: experiment id
    :param name: realization name
    :param hsh: experiment version hash
    """

    return do_put_get('projects/'+pid+'/experiments/'+eid+'/realizations/'+name, {
        'name': name,
        'hash': hsh
    })


def list_realizations(pid, eid):
    """List the realizations associated with an experiment

    :param pid: project id
    :param eid: experiment id
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/realizations')

def get_realization(pid, eid, name):
    """Get the details of a realization.

    Returns a json object with the nitty gritty.

    :param pid: project id
    :param ied: experiment id
    :param name: realization name
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/realizations/'+name)


def accept_realization(pid, eid, name):
    """Accept a realization.

    Upon accepting a realization, the resources are yours until you explicitly
    let them go or the lease runs out on any resource in the realization,
    whichever comes first.

    :param pid: project id
    :param eid: experiment id
    :param name: realization name
    """

    return do_post(
        'projects/'+pid+'/experiments/'+eid+'/realizations/'+name+'/act',
        {'action': 'accept'}
    )

def reject_realization(pid, eid, name):
    """Reject a realization.

    Reject a realization, short circuiting the 47 second timeout. Only a
    realization in the pending state may be rejected. Realizations that
    have been accepted can be destroyed through unrealize()

    :param pid: project id
    :param eid: experiment id
    :param name: realization name
    """

    return do_post(
        'projects/'+pid+'/experiments/'+eid+'/realizations/'+name+'/act',
        {'action': 'reject'}
    )

def delete_realization(pid, eid, name):
    """Delete a realization.

    This will free all resources associated with a realization. If there is an
    active materialization associated with the realization, it will be
    clobbered.

    :param pid: project id
    :param eid: experiment id
    :param name: realization name
    """

    return do_delete('projects/'+pid+'/experiments/'+eid+'/realizations/'+name, None)


# Materializations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_materialization(pid, eid, rid):
    """Get a materialization's information

    Fetch the nitty gritty.

    :param pid: project id
    :param eid: experiment id
    :param rid: realization id
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
                  '/materialization')

def materialization_status(pid, eid, rid):
    """Get the status of a materialization

    :param pid: project id
    :param eid: experiment id
    :param rid: realization id
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
                  '/materialization/status')

def materialization_status_table(pid, eid, rid):
    """Get the status of a materialization as table suitable for displaying

    :param pid: project id
    :param eid: experiment id
    :param rid: realization id
    """

    resp = do_get('projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
                  '/materialization/status')

    if not isinstance(resp, dict):
        return resp

    st = resp.get('status')
    if st is None:
        return resp

    sts = st.get('siteTasks')
    if sts is None:
        return resp

    result = ""
    for site, tasklist in sts.items():

        result += blue(site) + "\n"

        table = [[
            gray("kind"),
            gray("name"),
            gray("status"),
            gray("error"),
        ]]

        tasks = tasklist.get('tasks')
        if tasks is None:
            continue

        for t in tasks:
            state = t.get('complete', False)
            error = t.get('error', False)
            if state:
                statestr = green('complete')
            else:
                statestr = orange('pending')

            if error:
                statestr = red('failed')

            table.append([
                neutral(t.get('kind', '?')),
                neutral(t.get('name', '?')),
                statestr,
                neutral(t.get('error', '')),
            ])

        result += format_table(table)

    return result

def materialize(pid, eid, rid):
    """Materialize a realization.

    This will start the process of turning your experiment into a ticking
    breathing monster. The nodes will be brought online and imaged, and the
    your networks synthesized and isolated.

    :param pid: project id
    :param eid: experiment id
    :param rid: realization id
    """

    res = do_put(
        'projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
        '/materialization',
        {}
    )
    return res


def dematerialize(pid, eid, rid):
    """Dematerialize a realization.

    This will tear all the resources in a materialization down to a zero state.
    This does not relinquish the resources, they are still yours, so you can
    materialize again if so desired.

    :param pid: project id
    :param eid: experiment id
    :param name: realiztaion id
    """

    print("dematerializing %s/%s/%s"%(pid, eid, rid))
    res = do_delete(
        'projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
        '/materialization',
        None
    )
    print("your experiment has vaporized")
    return res

def materialize_attach(pid, eid, rid, key):
    """Attach the given key to the materialization connection.

    :param pid: project id
    :param eid: experiment id
    :param rid: realiztaion id
    :param key: public key as string
    """
    return do_put_get(
        (
            'projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
            '/materialization/attach'
        ),
        {'key': key}
    )

def materialize_detach(pid, eid, rid, key):
    """Remove the given key to the materialization connection.

    :param pid: project id
    :param eid: experiment id
    :param key: public key as string
    """
    return do_delete(
        ('projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
         '/materialization/attach'),
        {'key': key}
    )

# xdcs ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def list_xdcs(pid, eid):
    """List the experiment development containers associated with an experiment

    :param pid: project id
    :param eid: experiment id
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/xdc')

def spawn_xdc(pid, eid, name):
    """Spawn an experiment development contianer

    :param pid: project id
    :param eid: experiment id
    :param name: name of the xdc to spawn
    """
    return do_put('projects/'+pid+'/experiments/'+eid+'/xdc/'+name, None)

def destroy_xdc(pid, eid, name):
    """Destroy an experiment development contianer

    :param pid: project id
    :param eid: experiment id
    :param name: name of the xdc to spawn
    """
    return do_delete('projects/'+pid+'/experiments/'+eid+'/xdc/'+name, None)

def xdc_token(pid, eid, name):
    """Get an experiment development containers Jupyter access token

    :param pid: project id
    :param eid: experiment id
    :param name: name of the xdc to spawn
    """
    return do_get('projects/'+pid+'/experiments/'+eid+'/xdc/'+name+'/token')

def xdc_materialize_attach(pid, eid, xdcid, rid):
    """Create a connection to the given materialziation on the XDC specified.

    :param pid: project id
    :param eid: experiment id
    :param name: name of the xdc
    :param rid: realiztaion id
    """
    return do_put(
        'projects/'+pid+'/experiments/'+eid+'/xdc/'+xdcid+'/connection/'+rid,
        {},
    )

def xdc_materialize_detach(pid, eid, xdcid, rid):
    """Delete a connection to the given materialziation on the XDC specified.

    :param pid: project id
    :param eid: experiment id
    :param name: name of the xdc
    :param rid: realiztaion id
    """
    return do_delete(
        'projects/'+pid+'/experiments/'+eid+'/xdc/'+xdcid+'/connection/'+rid,
        {},
    )

# pubkeys ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def list_pubkeys(uid):
    """Get a users public keys

    :param uid: user id
    """

    return do_get('users/'+uid+'/keys')

def add_pubkey(uid, keyfile):
    """Add a public key for the user

    :param uid: user id
    :keyfile: pubkey file
    """

    with open(keyfile, 'r') as f:
        text = f.read().replace('\n', '')

    return do_put('users/'+uid+'/keys', {
        "key": text,
    })

def delete_pubkey(uid, fingerprint):
    """Delete a public key for the user

    :param uid: user id
    :param fingerprint: md5 ssh key fingerprint
    """

    return do_delete('users/'+uid+'/keys/'+fingerprint, None)

# pools ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def list_pools():
    """List available pools"""

    return do_get('pools')

def pool_info(name):
    """Get pool information"""

    return do_get('pools/'+name)


def new_pool(name, description):
    """Create a new pool

    :param name: new pool name
    :param description: short text describing pool
    """

    return do_put('pools/'+name, {
        'name': name,
        'description': description
    })

def delete_pool(name):
    """Delete a pool

    :param name: pool name to delete
    """

    return do_delete('pools/'+name, None)

def pool_sites(name):
    """List a pool's sites

    :param name: pool name
    """
    return do_get('pools/'+name+'/sites')

def add_pool_site(pool, site):
    """Add a site to a pool

    :param pool: pool name
    :param site: site name
    """

    return do_put('pools/'+pool+'/sites/'+site, {})

def del_pool_site(pool, site):
    """Delete a site from a pool

    :param pool: pool name
    :param site: site name
    """

    return do_delete('pools/'+pool+'/sites/'+site, None)

def activate_pool_site(pool, project):
    """Activate a site within the pool

    :param pool: pool name
    :param site: site name
    """

    return do_post('pools/'+pool+'/sites/'+project, {
        'state': 'active',
    })

def pool_projects(name):
    """List a pool's projects

    :param name: pool name
    """
    return do_get('pools/'+name+'/projects')

def add_pool_project(pool, project):
    """Add a project to a pool

    :param pool: pool name
    :param project: project name
    """

    return do_put('pools/'+pool+'/projects/'+project, {})

def activate_pool_project(pool, project):
    """Activate a project within the pool

    :param pool: pool name
    :param project: project name
    """

    return do_post('pools/'+pool+'/projects/'+project, {
        'state': 'active',
    })

def del_pool_project(pool, project):
    """Delete a project from a pool

    :param pool: pool name
    :param project: project name
    """

    return do_delete('pools/'+pool+'/projects/'+project, None)


# resources ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def list_resources():
    """List available resources"""


    js = do_get('resources')
    if js is None:
        return "no resources"

    by_model = group_resources(js)

    table = [[
        gray("resource"),
        gray("quantity"),
        gray("palloc"),
        gray("valloc"),
        gray("free"),
        gray("partial")
    ]]
    for k, v in by_model.items():
        table.append(
            [neutral(k),
             neutral("%d"%v['count']),
             red("%d"%v['palloc']),
             blue("%d"%v['valloc']),
             green("%d"%v['free']),
             cyan("%d"%v['partial'])]
        )

    s = ""
    widths = [max(map(len, col)) for col in zip(*table)]
    for row in table:
        s += "  ".join((val.ljust(width) for val, width in zip(row, widths))) + "\n"

    return s[:-1]

def format_table(table):
    s = ""
    widths = [max(map(len, col)) for col in zip(*table)]
    for row in table:
        s += "  ".join((val.ljust(width) for val, width in zip(row, widths))) + "\n"

    return s[:-1]

def group_resources(data):

    by_model = {}
    for elem in data:

        # only look at virtually or physically allocable resources
        allocable = False
        for x in elem['props']['resource']['Alloc']:
            if x in (6, 7):
                allocable = True

        if not allocable:
            continue

        palloc = 0
        valloc = 0
        free = 0
        partial = 0
        if elem['allocations'] is not None:
            for a in elem['allocations']:
                if a['kind'] == 1:
                    palloc += 1
                if a['kind'] == 2:
                    valloc += 1
                    partial = 1
        else:
            free = 1


        x = by_model.get(elem['props']['model'])
        if x is None:
            by_model[elem['props']['model']] = {
                'count': 1,
                'palloc': palloc,
                'valloc': valloc,
                'free': free,
                'partial': partial
            }
        else:
            by_model[elem['props']['model']]['count'] = x['count']+1
            by_model[elem['props']['model']]['palloc'] = x['palloc']+palloc
            by_model[elem['props']['model']]['valloc'] = x['valloc']+valloc
            by_model[elem['props']['model']]['free'] = x['free']+free
            by_model[elem['props']['model']]['partial'] = x['partial']+partial

    return by_model


# helpers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def show(thing):
    print(yaml.dump(yaml.load(json.dumps(thing)), default_flow_style=False))

def do_get(path):
    '''GET a path on the merge API and return the results.

    :param path: the path to GET
    '''
    try:
        resp = requests.get(
            'https://'+this.api+'/'+path,
            headers={'authorization': 'Bearer ' + this.accessToken}
        )
    except ConnectionError as e:
        log.critical('Error connection to API: %s', e)
        return None

    if resp.ok:
        try:
            return resp.json()
        except ValueError:
            # Not JSON, so just return the status code.
            pass

    return resp.status_code


def do_put_base(path, payload):
    try:
        if payload:
            resp = requests.put(
                'https://'+this.api+'/'+path,
                headers={'authorization': 'Bearer ' + this.accessToken},
                json=payload
            )
        else:
            resp = requests.put(
                'https://'+this.api+'/'+path,
                headers={'authorization': 'Bearer ' + this.accessToken},
            )
    except ConnectionError as e:
        log.critical('put %s connection error: %s', path, e)
        return "500: internal error"

    return resp

def do_put_get(path, payload):
    resp = do_put_base(path, payload)
    return resp.json()

def do_put(path, payload):
    resp = do_put_base(path, payload)
    if resp.status_code == 200:
        return "ok"

    return "%d: %s"%(resp.status_code, resp.text)

def do_put_file(url, filepath):
    '''Call a Merge API endpoint with PUT and the given payload as the body.

    Errors in JSON payload or reading the filepath will result in a 500 error
    returned.

    :param url: the API endpoint
    :param filepath: The file which contains the message body (in JSON).
                     Invalid JSON will not be sent.
    '''
    try:
        with open(filepath) as fd:
            # GTL TODO: sanitize input.
            payload = json.load(fd)
            return do_put(url, payload)
    except (OSError, ValueError):
        # log this as warn
        pass
    return 500

def do_post_file(url, filepath):
    '''Call a Merge API endpoint with cwPOSTPUT and the given payload as the body.

    Errors in JSON payload or reading the filepath will result in a 500 error
    returned.

    :param url: the API endpoint
    :param filepath: The file which contains the message body (in JSON).
                     Invalid JSON will not be sent.
    '''
    try:
        with open(filepath) as fd:
            # GTL TODO: sanitize input.
            payload = json.load(fd)
            return do_post(url, payload)
    except (OSError, ValueError):
        # log this as warn
        pass
    return 500

def do_post(path, payload):
    resp = requests.post(
        'https://'+this.api+'/'+path,
        headers={'authorization': 'Bearer ' + this.accessToken},
        json=payload,
    )
    return resp.status_code

def do_delete(path, payload):
    if payload:
        resp = requests.delete(
            'https://'+this.api+'/'+path,
            headers={'authorization': 'Bearer ' + this.accessToken},
            json=payload
        )
    else:
        resp = requests.delete(
            'https://'+this.api+'/'+path,
            headers={'authorization': 'Bearer ' + this.accessToken},
        )

    return resp.status_code

def set_token(token):
    """Set the OAuth2 access token used to access the mergetb API"""
    this.accessToken = token

def set_api(api):
    """Set the mergetb API url"""
    this.api = api

def fetch_web_token():
    """For use in Jupyter environment only. If you've logged in via the
    mergetb login page in the browser, this function will fetch and
    set the corresponding oauth access token from the browser.
    """

    js = """
    <script type="text/javascript">
    var tk = localStorage.getItem("accessToken");
    var cmd = "mergetb.set_token('"+tk+"')";
    var kernel = IPython.notebook.kernel;
    kernel.execute(cmd);
    </script>
    """
    return HTML(js)

def fetch_fs_token():
    with open(os.path.expanduser('~')+'/.merge/token', 'r') as f:
        token = f.read()

    set_token(token)

# TODO delete me
# pylint: disable=wrong-import-position,wrong-import-order,ungrouped-imports
from IPython import get_ipython
def init():
    ipython = get_ipython()
    ipython.magic("env REQUESTS_CA_BUNDLE=/home/ry/scratch/pem/ca.pem")
    fetch_fs_token()
    set_api('api.mergetb47.net')
