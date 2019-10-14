#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
import enum


url = "https://staging-api.dance4water.org/api"
dance_url = "https://staging-sql.dance4water.org/resultsdb/"


class AccessLevel(enum.Enum):
    DEMO = 1
    PARTICIPANT = 2
    CONSULTANT = 3
    ADMIN = 4
    SUPERADMIN = 5

def db_name(simulation_id):
    return simulation_id


def run_query(token, scenario_id, query):
    """
    Run a query on the scenario spatialite database. The database supports SQLite and Spatialite commands
    Only read access is supported! To find out which data are stored in the database read the dynamind_table_definitions

    :param token: Access token
    :param scenario_id: scenario id
    :param query: SQL query
    :type token: str
    :type scenario_id: int
    :type query str
    :return: query result
    :rtype: dict
    """

    simulation_id = get_database_id(token, scenario_id)

    data = {'db_name': db_name(simulation_id),
            'query': query}
    r = requests.post(dance_url, data=data)
    if r.status_code == 200:
        result = r.json()
        return result
    raise Exception(f"Unable to run query {r.status_code}")


def add_node(token, node_data):
    headers = {"Authorization": "Bearer " + token}
    return requests.post(url + "/sm_node", headers=headers, json=node_data)

def update_sm_node(token, node_id, node_data):
    headers = {"Authorization": "Bearer " + token}
    return requests.post(url + "/sm_node/" + str(node_id)+ "/versions", headers=headers, json=node_data)


def add_model(token, name, src):
    headers = {"Authorization": "Bearer " + token}
    return requests.post(url + "/models", headers=headers, json={"name": name, "model_src": src})

def get_models(token):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/models/", headers=headers)

def login(username, password):
    """
    Get access token

    :param username: registered user name (email address)
    :param password: top secret password
    :return: access token
    """
    counter = 0
    while True:
        r = requests.post(url + "/user/login/", json={'username': username,
                                                      'password': password})
        counter += 1
        if r.status_code == 200:
            return r.json()["access_token"]
        if counter > 4:
            raise Exception(f"Unable to login status {r.status_code}")

        else:
            time.sleep(2)

def get_database_id(token, scenario_id):
    """
    Returns database ID to run data analysis

    :param token: access token
    :param scenario_1_id: scenario id
    :return: data base id needed for query
    """
    r = get_simulations(token, scenario_id)
    if r.status_code != 200:
        raise Exception(f"Unable to obtain scenarios {r.status_code}")

    sims = r.json()

    for s in sims["simulations"]:
        sim = json.loads(s)
        if sim["simulation_type"] == "PERFORMANCE_ASSESSMENT":
            return sim["id"]



def create_project(token):
    """
    Creates a new project

    :param token: Access token
    :type token: str
    :return: project id
    :rtype: int
    """

    headers = {"Authorization": "Bearer " + token}
    r = requests.post(url + "/projects", headers=headers)

    if r.status_code == 200:
        return r.json()["id"]

    raise Exception(f"Creation of project failed {r.status_code}")


def get_project(token, project):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/projects/" + str(project), headers=headers)


def get_projects(token):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/projects/", headers=headers)


def update_project(token, project, data):
    headers = {"Authorization": "Bearer " + token}
    return requests.put(url + "/projects/" + str(project), headers=headers, json=data)

def get_assessment_models(token):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/assessment_models", headers=headers)


def get_assessment_model(token, model_name):
    """
    Returns assessment model id

    :param token: Access token
    :param model_name: Model Name. Currently supported are Land Surface Temperature and Target
    :type token: str
    :type model_name: str
    :return: model_id
    :rtype: int
    """
    headers = {"Authorization": "Bearer " + token}
    r = requests.get(url + "/assessment_models", headers=headers)

    if not r.status_code == 200:
        raise Exception(f"Could not get assessment model {r.status_code}")

    models = r.json()["assessment_models"]
    model_id = None

    for model in models:
        if model["name"] == model_name:
            model_id = model["id"]
            break

    if model_id is None:
        raise Exception(f"Could not find ' {model_name}")

    return model_id

def set_project_assessment_models(token, project, models):
    headers = {"Authorization": "Bearer " + token}
    return requests.put(url + "/projects/" + str(project) + "/models", headers=headers, json=models)


def create_scenario(token, project, parent, name="initialised model"):
    """
    Creates a new scenario. The provides the shell for the new scenarios. Scenario are derived from the base line
    or any other scenario in the project. To modify the environment workflow may be defined and executed.

    :param token: Access token
    :param project: project id
    :param parent: parent scenario id
    :param name: name of scenario
    :type str
    :type int
    :type int
    :type str
    :return: scenario id
    ":rtype: int
    """
    data = {"project_id": project, "name": name}
    if parent is not None:
        data["parent"] = parent

    headers = {"Authorization": "Bearer " + token}
    r = requests.post(url + "/scenario/", headers=headers, json=data)

    if r.status_code == 200:
        return r.json()["id"]

    raise Exception(f"Unable to create scenario {r.status_code}")


def set_scenario_workflow(token, scenario_id, node_data):
    """
    Set the workflow for a scenario. The workflow is defined by a series of nodes defined by the node_data
    The node_data have following structure

    .. code-block::

        [{
           name: node_id,
           area: geojson_id,
           parameters: {

            parameter.value = 1,
            paramter2.value = 2,

           }
        },
        ...
        ]

    The nodes in the workflow are executed as defined in the data structure

    :param token: Access token
    :param scenario_id: scenario id
    :param node_data: node data see above
    :type token: str
    :type scenario_id: int
    :type node_data: list

    """

    headers = {"Authorization": "Bearer " + token}
    r = requests.post(url + "/scenario/" + str(scenario_id) + "/nodes", headers=headers, json=node_data)
    if r.status_code == 200:
        return

    raise Exception(f"Something went wrong when adding the nodes {r.status_code} {r.json()}")


def get_scenario_workflow_nodes(token):

    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/sm_node/", headers=headers)


def upload_geojson(token, geojson, project_id, name = "casestudyarea"):
    """
    Upload a geojson file and return id

    :param token: Assess token
    :param geojson: geojson file
    :param project_id: project the node will be assigned to
    :param name: added option to set name of geojson file default is set to casestudyarea
    :type token: str
    :type geojson: str
    :type name: str
    :type project_id: int
    :return: geojson id
    :rtype: int
    """
    headers = {"Authorization": "Bearer " + token}

    if 'name' in geojson: del geojson['name']

    r = requests.post(url + "/geojson/", headers=headers,
                         json={"project_id": project_id, "geojson": geojson, "name":name})

    if r.status_code == 200:
        return r.json()["id"]

    raise Exception(f"Unable to upload file {r.status_code}")


def get_region(token, region_name):
    """
    Returns region currently supported is Melbourne

    :param token: access token
    :param region: region id
    :return: region id
    """

    headers = {"Authorization": "Bearer " + token}
    r = requests.get(url + "/regions/", headers=headers)
    if not r.status_code == 200:
        raise Exception(f"Unable to get region {r.status_code}")
    regions = r.json()
    melbourne_region_id = None
    for region in regions:
        if region["name"].lower() == region_name:
            melbourne_region_id = region["id"]
            break

    if melbourne_region_id is None:
        raise Exception(f"Could not find ' {region_name}")

    return melbourne_region_id

def get_regions(token):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/regions/", headers=headers)


def execute_scenario(token, scenario, queue="default"):
    """

    :param token: access token
    :param scenario: id of scenario to be executed
    :param queue: optional parameter to define queue
    :rtype: int
    :rtype: str
    :rtype: str
    """
    headers = {"Authorization": "Bearer " + token}
    return requests.post(f'{url}/scenario/{scenario}/execute?queue={queue}', headers=headers)


def get_geojsons(token, project):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/geojson/" + str(project), headers=headers)


def check_status(token, scenario):
    """
    Return status of current simulation.

    returns:

    .. code-block::

        {
           status: status code (int),
           status_text: status description
        }

        // CREATED = 1
        // BASE_IN_QUEUE = 2
        // BASE_RUNNING = 3
        // BASE_COMPLETE = 4
        // PA_IN_QUEUE = 5
        // PA_RUNNING = 6
        // PA_COMPLETE = 7
        // COMPLETE = 8

    :param token: Access token
    :param scenario: scenario id
    :type token: str
    :type scenario: int
    :return: scenario status
    :rtype: dict

    """
    headers = {"Authorization": "Bearer " + token}
    r= requests.get(url + "/scenario/" + str(scenario) + "/status", headers=headers)
    if r.status_code != 200:
        raise Exception(f"Unable to get status {r.status_code}")
    return r.json()


def get_scenario(token, scenario):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/scenario/" + str(scenario), headers=headers)


def get_simulations(token, scenario):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/scenario/" + str(scenario) + "/simulations", headers=headers)


def upload_dynamind_model(token, name, filename):
    """
    Uploads a new model to the server

    :param token: access token
    :param name: model name
    :param filename: dynamind file
    :type str
    :type str
    :return: model_id
    :rtype: int
    """
    with open(filename, 'r') as file:
        data = file.read().replace('\n', '')

    r = add_model(token, name, data)

    model_id = r.json()["model_id"]

    return model_id


def show_node_versions(token, node_id):
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url + "/sm_node/" + str(node_id), headers=headers)


def create_node(token, filename, model_id=None, access_level=AccessLevel.SUPERADMIN.value):
    """
    Create a new node

    :param token: access token
    :param filename: point to json file containing the node description
    :param model_id: model id in json file will be replaced by this. If not set model_id from json file
    :param access_level: access level of node
    :type str
    :type str
    :type int
    :type int
    :return: node_id
    :rtype: int
    """
    with open(filename) as json_file:
        node_data = json.load(json_file)

    if model_id is not None:
        node_data["models"][0]["id"] = model_id
        node_data["access_level"] = access_level
    r = add_node(token, node_data)

    if r.status_code == 200:
        result = r.json()
        return result["node_id"]
    raise Exception(f"Unable to add node {r.status_code}")


def update_node(token, node_id, filename, model_id=None, access_level=AccessLevel.SUPERADMIN.value):
    """
    Update an existing node

    :param token: access token
    :param node_id: id of node
    :param filename: point to json file containing the node description
    :param model_id: model id in json file will be replaced by this. If not set model_id from json file
    :param access_level: access level of node
    :type str
    :type str
    :type str
    :type int
    :type int
    :return: node_id
    :rtype: int
    """
    with open(filename) as json_file:
        node_data = json.load(json_file)

    if model_id is not None:
        node_data["models"][0]["id"] = model_id
        node_data["access_level"] = access_level
    r = update_sm_node(token, node_id, node_data)

    if r.status_code == 200:
        result = r.json()
        return result["node_version_id"]
    raise Exception(f"Unable to update node {r.status_code}")


def set_node_access_level(token, node_id, access_level):
    """
    Set the access level of the parent node

    :param token: access token
    :param node_id: node id
    :param access_level: access level (see enum)
    :type token: str
    :type node_id: int
    :type access_level: int
    """
    headers = {"Authorization": "Bearer " + token}
    r = requests.post(f"{url}/sm_node/{node_id}", headers=headers, json={"access_level": access_level})
    if r.status_code == 200:
        return
    raise Exception(f"Could not update access level node {r.status_code}")


def deactivate_node(token, node_id):
    """
    Deactivate node

    :param token: access token
    :param node_id: node id
    :type token: str
    :type node_id: int
    """
    headers = {"Authorization": "Bearer " + token}
    r = requests.post(f"{url}/sm_node/{node_id}", headers=headers, json={"active": False})
    if r.status_code == 200:
        return
    raise Exception(f"Could not deactivate node {r.status_code}")


def get_baseline(token, project_id):
    """
    Get a projects baseline scenario id

    :param token: Access token
    :param project_id: Project ID
    :type token: str
    :type project_id: int
    :return: baseline scenario id
    :rtype: int
    """
    r = get_project(token, project_id)
    scenarios = r.json()["scenarios"]
    scene = next(item for item in scenarios if item["parent"] is None)
    baseline_id = scene["id"]
    return baseline_id


def get_city_boundray(token, project_id):
    """
    Return a cities geojson boundary id

    :param token: Access token
    :param project_id: project ID
    :type token: str
    :type project_id: int
    :return: geojson boundary id
    :rtype: int
    """

    r = get_geojsons(token, project_id)
    geojsons = r.json()
    geojson_city_id = geojsons["geojsons"][0]["id"]
    return geojson_city_id


def show_nodes(token):
    """
    Prints list of available nodes

    :param token: Access token
    :type token: str
    """
    r = get_scenario_workflow_nodes(token)
    if not r.status_code == 200:
        raise Exception(f"Could not get scenario workflow nodes")

    smnodes = r.json()["scenario_maker_nodes"]
    for node in smnodes:
        print(node["id"], node["name"])


def get_nodes(token):
    """
    Return list of available nodes

    :param token: Access token
    :type token: str

    :return: returns a dict of all scenario
    :rtype: dict
    """
    r = get_scenario_workflow_nodes(token)
    if not r.status_code == 200:
        raise Exception(f"Could not get scenario workflow nodes")

    smnodes = r.json()["scenario_maker_nodes"]

    return smnodes


def show_scenarios(token, project_id):
    """
    Prints a list of the scenarios in a project

    :param token: Access token
    :param project_id: project id
    :type token: str
    :type project_id: int
    """
    r = get_project(token, project_id)
    if not r.status_code == 200:
        raise Exception(f"Could not get scenario workflow nodes {r.status_code}")

    scenarios = r.json()["scenarios"]
    for s in scenarios:
        print(s["id"], s["status"], s["name"])


def get_scenarios(token, project_id):
    """
    Get a list of scenarios in a project

    :param token: Access token
    :param project_id: project ID
    :type str
    :type int
    :return: returns a dict of all scenario
    :rtype: dict
    """
    r = get_project(token, project_id)
    if not r.status_code == 200:
        raise Exception(f"Could not get scenario workflow nodes {r.status_code}")

    scenarios = r.json()["scenarios"]
    return scenarios


def show_log(token, scenario_id):
    """
    Print scenario log file

    :param token: access token
    :param scenario_id: scenario id
    :type token: str
    :type scenario_id: int
    """
    r = get_simulations(token, scenario_id)

    if not r.status_code == 200:
        raise Exception(f"Could not get scenario log {r.status_code}")

    sims = r.json()

    for s in sims["simulations"]:
        database_id = json.loads(s)["id"]
    for s in sims["simulation_intances"]:
        print(json.loads(s)["id"],  json.loads(s)["progress"], json.loads(s)["heartbeat"], json.loads(s)["log"])

    return database_id


def get_node_id(token, name):
    """
    Return node id to be used in simulation

    :param token: access token
    :param name: node name
    :return: node_id
    :rtype int
    """
    nodes = get_nodes(token)
    for n in nodes:
        if n['name'] == name:
            return n['id']
    raise Exception(f"Node  {name} not found")


def create_assessment_model(token, filename, model_id=None):
    """
    Creates a new assessment model and a default version tagged as 0.0.1
    the data must be of the shape:

    :param token: Access token
    :param filename: filename of json file (see below)
    :param model_id: dynamind model id
    :type token: str
    :type filename: str
    :type model_id: int

    .. code-block::

        {
           name: "some name",
           description: "some desc",

           //optionally add assessment model stage of development
           //1 = ALPHA
           //2 = BETA
           //3 = UNDER DEVELOPMENT
           //default is 3
           stage: 2
           //must specify one of:
           model_id: <model_id> //by default will use the active version of this model
           model_version_id: <model_version_id> //if present will use this model version id
        }

    returns:

    .. code-block::

        {
          assessment_model_id: <the id of the new assessment model>,
          assessment_model_version_id: <id of the new default version>
        }

    """

    with open(filename) as json_file:
        node_data = json.load(json_file)

    if model_id is not None:
        node_data["model_id"] = model_id

    headers = {"Authorization": "Bearer " + token}
    r = requests.post(url + "/assessment_models", headers=headers, json=node_data)

    if r.status_code == 200:
        result = r.json()
        return result["assessment_model_id"]
    raise Exception(f"Unable to create assessment model {r.status_code}")

def update_assessment_model(token, assessment_model_id, filename, model_id):
    """
    Creates a new assessment model and a default version tagged as 0.0.1
    the data must be of the shape:

    :param token: access token
    :param assessment_model_id: assessment model id to be updated
    :param filename: filename of json file (see below)
    :param model_id: dynamind model id
    :type token: str
    :type assessment_model_id: int
    :type filename: str
    :type model_id: int

    .. code-block::

        {
           name: "some name",
           description: "some desc",

           //optionally add assessment model stage of development
           //1 = ALPHA
           //2 = BETA
           //3 = UNDER DEVELOPMENT
           //default is 3
           stage: 2
           //must specify one of:
           model_id: <model_id> //by default will use the active version of this model
           model_version_id: <model_version_id> //if present will use this model version id
        }

    returns:

    .. code-block::

        {
          assessment_model_id: <the id of the new assessment model>,
          assessment_model_version_id: <id of the new default version>
        }

    """
    with open(filename) as json_file:
        node_data = json.load(json_file)

    if model_id is not None:
        node_data["model_id"] = model_id

    headers = {"Authorization": "Bearer " + token}
    print(f"{url}/assessment_models/{assessment_model_id}/versions")
    r = requests.post(f"{url}/assessment_models/{assessment_model_id}/versions", headers=headers, json=node_data)
    if r.status_code == 200:
        result = r.json()
        return result["assessment_model_version_id"]
    raise Exception(f"Unable to update assessment model {r.status_code}")


def get_project_databases(token, project_id, folder=".", scenario_id = None):
    """
    Download project databases. Databases will be downloaded into folder/project_id.zip
    For larger projects it is recommended to defined the scenario_id to be downloaded. Otherwise the download might fail
    :param token: access token
    :param project_id: project id
    :param folder: folder
    :param scenario_id: scenario_id
    :type token: str
    :type project_id: int
    :type folder: str
    :type scenario_id: int
    """


    headers = {"Authorization": "Bearer " + token}
    if scenario_id:
        r = requests.get(f"{url}/projects/{project_id}/data?scenario={scenario_id}", headers=headers)
    else:
        r = requests.get(f"{url}/projects/{project_id}/data", headers=headers)
    if r.status_code == 200:
        if scenario_id:
            open(f"{folder}/{project_id}-{scenario_id}.zip", 'wb').write(r.content)
        else:
            open(f"{folder}/{project_id}.zip", 'wb').write(r.content)
        return
    raise Exception(f"Something went wrong while downloading the folder {r.status_code} {r.json()}")


def get_my_status(token):
    """
    Get user status
    :param token: access token
    :return: dict with project status
    """

    headers = {"Authorization": "Bearer " + token}
    r = requests.get(f"{url}/user/status/", headers=headers)
    if r.status_code == 200:
        return r.json()

    raise Exception(f"Something when downloading status {r.status_code} {r.json()}")
