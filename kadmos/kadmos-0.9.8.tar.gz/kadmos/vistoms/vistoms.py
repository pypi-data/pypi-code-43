# Imports
from __future__ import absolute_import, division, print_function
import ast
import fnmatch
import json
import logging
import os
import shutil
import sys
import tempfile
import time
import uuid
import webbrowser
import xml.etree.ElementTree as ET
import zipfile
from copy import deepcopy
from datetime import datetime
from shutil import copyfile

import numpy as np

import networkx as nx
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from six import string_types

from kadmos.cmdows.cmdows import find_cmdows_file
from kadmos.graph import load, FundamentalProblemGraph, KadmosGraph, RepositoryConnectivityGraph
from kadmos.graph.mixin_vistoms import retrieve_session_folder

app = Flask(__name__)

# Folder and file settings
SESSIONS_CATALOG_FOLDER = r'D:\websites\vistoms_interface\sessions_catalog'
SESSIONS_FOLDER_SERVER = r'D:\websites\vistoms_interface\session_files'
TEMP_FILE = 'tmp'


# Interface function
########################################################################################################################
def interface(debug=True, tempdir=None):

    # Initial settings
    app = Flask(__name__)
    if debug:
        app.debug = True
    if tempdir:
        tempfile.tempdir = tempdir

    # Index
    @app.route("/")
    def index(error=None, message=None, selection=False):
        # Check if error or message is send
        if request.values.get('error', False) and error is None:
            error = request.values['error']
        if request.values.get('message', False) and message is None:
            message = request.values['message']
        # Render index
        return render_template('index.html', error=error, message=message, selection=selection, page='start')

    # Start of a local VISTOMS session (used in KADMOS scripts and command line creation of VISTOMS)
    @app.route('/start_vistoms_local')
    def start_vistoms_local():
        """
           Function opens local VISTOMS instance when it is called from vistoms_start() or python vistoms.py
        """

        # Get directory with sessions
        sessions_dir = SESSIONS_CATALOG_FOLDER

        # Create directory if it does not exist
        if not os.path.exists(SESSIONS_CATALOG_FOLDER):
            os.makedirs(SESSIONS_CATALOG_FOLDER)

        # Get random uuid for session
        session_id = str(uuid.uuid4())

        # Add the json file of the session to the sessions directory
        session_details = dict(folder=sessions_dir,
                               creation_date=str(datetime.now()))
        with open(os.path.join(sessions_dir, session_id+'.json'), 'w') as outfile:
            json.dump(session_details, outfile)

        return render_template('VISTOMS.html', new=0, interfaceMode='local', sessionId=session_id)

    # Start of a server VISTOMS session (used on mdo-system-interface.agile-project.eu)
    @app.route('/start_vistoms_server_session')
    def start_vistoms_server_session():
        """
           Function opens local VISTOMS session instance when it is called from the VISTOMS web interface.
        """

        # Get directory with sessions
        sessions_dir = SESSIONS_CATALOG_FOLDER

        # Create directory if it does not exist
        if not os.path.exists(SESSIONS_CATALOG_FOLDER):
            os.makedirs(SESSIONS_CATALOG_FOLDER)

        # Get random uuid for session
        session_id = str(uuid.uuid4())

        # Add the json file of the session to the sessions directory
        session_details = dict(folder=os.path.join(SESSIONS_FOLDER_SERVER, session_id),
                               creation_date=str(datetime.now()))
        with open(os.path.join(sessions_dir, session_id + '.json'), 'w') as outfile:
            json.dump(session_details, outfile)

        os.makedirs(os.path.join(SESSIONS_FOLDER_SERVER, session_id))

        # Wait for directory to exist
        attempts = 0
        while True:
            if os.path.isdir(os.path.join(SESSIONS_FOLDER_SERVER, session_id)):
                break
            time.sleep(1)
            attempts += 1
            if attempts > 20:
                raise ReferenceError('Could not create new session directory on server.')

        return render_template('VISTOMS.html', new=0, interfaceMode='server', sessionId=session_id)

    # Download an example file
    @app.route('/downloads/<path:file_name>')
    def download_file(file_name):
        vistoms_folder = os.path.split(__file__)[0]
        file_path = os.path.join(vistoms_folder, 'downloads', file_name)
        return send_file(file_path, as_attachment=True)

    # Info
    @app.route('/info')
    def info():
        return render_template('info.html', page='info')

    # Acknowledgements
    @app.route('/acknowledgements')
    def acknowledgements():
        return render_template('acknowledgements.html', page='acknowledgements')

    @app.route('/kadmos_upload_files', methods=['GET', 'POST'])
    def kadmos_upload_files():
        """
            Function uploads a file to the temp folder and returns the graph information to VISTOMS

            :return: VISTOMS json data with graph information
        """
        try:
            if request.method == 'POST':
                # get request form
                fileType = request.form['fileType']
                newGraphID = request.form['newGraphID']
                session_id = request.form['sessionId']
                uploaded_files = request.files.getlist("file[]")

                session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

                # check if the post request has the file part
                if 'file[]' not in request.files:
                    return "ERROR: No file part!"

                newVistomsDataArray = []

                if fileType == 'Database':
                    if len(uploaded_files) > 1:
                        return "ERROR: You can upload only one ZIP-file!"
                    file = {}
                    for aFile in uploaded_files:
                        file = aFile
                    if file.filename.rsplit('.', 1)[1].lower() != "zip":
                        return "ERROR: Wrong file type! Please use a valid zip file"

                    database_dir = ""
                    if fileType == 'Database':
                        database_dir = os.path.join(session_folder, 'database_tmp')
                        zip_ref = zipfile.ZipFile(file, 'r')
                        zip_ref.extractall(database_dir)
                        zip_ref.close()
                        file_list = []
                        database_listdir = os.listdir(database_dir)

                        # Handle case where the database is stored as a subfolder in de zip archive (as done on MacOS)
                        actual_database_dir = database_dir
                        if len(database_listdir) == 1 or '__MACOSX' in database_listdir:
                            if '__MACOSX' in database_listdir:
                                database_listdir.remove('__MACOSX')
                            if os.path.isdir(os.path.join(database_dir, database_listdir[0])):
                                actual_database_dir = os.path.join(database_dir, database_listdir[0])
                        for file in os.listdir(actual_database_dir):
                            file_list.append(os.path.join(actual_database_dir, file))

                        cmdows_file = find_cmdows_file(file_list)
                        graphFileName = cmdows_file

                        loaded_graph = load(graphFileName, file_check_critical=False)
                        if isinstance(loaded_graph, tuple):
                            graph = loaded_graph[0]
                            mpg = loaded_graph[1]
                        else:
                            graph = loaded_graph
                            mpg = None

                        if "name" not in graph.graph:
                            graph.graph["name"] = os.path.split(os.path.splitext(graphFileName)[0].replace("_", "."))[1]
                        # Remove the uploaded file (and if existing, database directory) from the temp folder
                        os.remove(graphFileName)
                        if os.path.exists(database_dir):
                            shutil.rmtree(database_dir)

                        # save the graph as kdms file in temp folder
                        graph.save(os.path.join(session_folder, TEMP_FILE + '_' + newGraphID + '.kdms'),
                                   file_type='kdms',
                                   graph_check_critical=False, mpg=mpg)
                        # Increase graphID by 1
                        newGraphID = str(int(newGraphID) + 1)

                        # Use function order for VISTOMS if it is available in the graph information
                        function_order = None
                        if graph.graph_has_nested_attributes('problem_formulation',
                                                             'function_order') and mpg == None:
                            function_order = graph.graph['problem_formulation']['function_order']

                        # Add the graph with the updated function order to VISTOMS
                        newVistomsDataArray.append(graph.vistoms_add_json(graph_id=newGraphID, function_order=function_order,
                                                                mpg=mpg))
                else:
                    file_names = []
                    for file in uploaded_files:
                        file_names.append(file.filename)
                    for file in uploaded_files:
                        if "_mpg" in file.filename:
                            # Do nothing if it is an _mpg file
                            continue
                        else:
                            dgFile = file
                            # Check if the right filetypes were chosen
                            if fileType == 'CMDOWS file' and dgFile.filename.rsplit('.', 1)[1].lower() != "xml":
                                return "ERROR: Wrong file type! Please use a valid CMDOWS file"
                            elif fileType == 'KDMS file(s)' and dgFile.filename.rsplit('.', 1)[1].lower() != "kdms":
                                return "ERROR: Wrong file type! Please use a valid KDMS file"

                            graph_file = os.path.join(session_folder, dgFile.filename)
                            dgFile.save(os.path.join(session_folder, dgFile.filename))

                            loaded_graph = load(graph_file, file_check_critical=False)
                            if isinstance(loaded_graph, tuple):
                                graph = loaded_graph[0]
                                mpg = loaded_graph[1]
                            else:
                                mpgFileName = os.path.split(os.path.splitext(dgFile.filename)[0])[1]+'_mpg.kdms'
                                if mpgFileName in file_names:
                                    index = file_names.index(mpgFileName)
                                    uploaded_files[index].save(os.path.join(session_folder, mpgFileName))
                                    graph = loaded_graph
                                    mpg = load(os.path.join(session_folder, mpgFileName), file_check_critical=False)
                                    os.remove(os.path.join(session_folder, mpgFileName))
                                else:
                                    graph= loaded_graph
                                    mpg = None

                            if "name" not in graph.graph:
                                graph.graph["name"] = os.path.splitext(dgFile.filename)[0].replace("_", ".")

                            # Remove the uploaded file (and if existing, database directory) from the temp folder
                            os.remove(graph_file)

                            # save the graph as kdms file in temp folder
                            graph.save(os.path.join(session_folder, TEMP_FILE + '_' + newGraphID + '.kdms'),
                                       file_type='kdms',
                                       graph_check_critical=False, mpg=mpg)
                            # Use function order for VISTOMS if it is available in the graph information
                            function_order = None
                            if graph.graph_has_nested_attributes('problem_formulation',
                                                                 'function_order') and mpg == None:
                                function_order = graph.graph['problem_formulation']['function_order']

                            # Add the graph with the updated function order to VISTOMS
                            newVistomsDataArray.append(graph.vistoms_add_json(graph_id=newGraphID, function_order=function_order,
                                                                    mpg=mpg))
                            # Increase graphID by 1
                            newGraphID = str(int(newGraphID) + 1).zfill(2)

                return jsonify(newVistomsDataArray)

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_create_new_graph', methods=['POST'])
    def kadmos_create_new_graph():
        try:
            # Get request form
            graph_name = request.form['graph_name']
            graph_description = request.form['graph_description']
            graphID = request.form['graphID']
            session_id = request.form['sessionId']

            # Open cmdows template file and load it as graph
            cmdows_template = os.path.join(os.path.split(__file__)[0], 'templates', 'cmdows_template.xml')
            graph_template = load(cmdows_template, check_list=['consistent_root', 'invalid_leaf_elements'])
            graph_template = RepositoryConnectivityGraph(graph_template)

            # Allocate graph name, description and id
            graph_template.graph['name'] = graph_name
            graph_template.graph['description'] = graph_description
            graph_template.graph['id'] = graphID

            # Delete dummy design competence
            graph_template.remove_node('dummy')

            # Retrieve session folder
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save empty graph as kdms file
            graph_template.save(os.path.join(session_folder, 'tmp_' + graphID + '.kdms'), file_type='kdms',
                                graph_check_critical=False, mpg=None)

            # Add graph to vistoms data
            newVistomsData = graph_template.vistoms_add_json(mpg=None, graph_id=graphID)

            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_export_graphs', methods=['POST'])
    def kadmos_export_graphs():
        """
           Function exports all graphs to a folder as CMDOWS or KDMS files

           :param path: the path of the folder, the files are exported to
           :return: path
        """
        try:
            # Get request form
            fileNames_str = request.form['fileNames_str']
            graphIDs_str = request.form['graphIDs_str']
            fileType = request.form['fileType']
            session_id = request.form['sessionId']

            graphIDs = json.loads(graphIDs_str)
            fileNames = json.loads(fileNames_str)
            files = []
            counter = 0
            for graphID in graphIDs:
                fileName = fileNames[counter]
                file_arr = kadmos_export_graph(fileName=fileName, graphID=graphID, fileType=fileType, session_id=session_id)
                for file in file_arr:
                    files.append(file)
                counter += 1

            return jsonify(files)

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_download/<path:filename>/<path:session_id>')
    def kadmos_download(filename, session_id):
        try:
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)
            return send_from_directory(directory=session_folder, filename=filename)

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_remove_obsolete_files', methods=['POST'])
    def kadmos_remove_obsolete_files():
        try:
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)
            for file in os.listdir(session_folder):
                if "tmp_" not in file and os.path.splitext(file)[1] != '.json':  # JSON file should also be kept!
                    os.remove(os.path.join(session_folder, file))
            return ""

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    def kadmos_export_graph(fileName, graphID, fileType, session_id):
        """
           Function exports the current graph to a CMDOWS or kdms file

           :param file: a CMDOWS or kdms file that goes into the user's download folder
           :return: file
        """
        try:
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            files = []
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(session_folder, mpgFileName)):
                graph = load(os.path.join(session_folder, graphFileName), file_check_critical=False)
                mpg = load(os.path.join(session_folder, mpgFileName), file_check_critical=False)
            else:
                graph = load(os.path.join(session_folder, graphFileName), file_check_critical=False)
                mpg = None

            # Add problem function roles if they are not already existing
            if isinstance(graph, FundamentalProblemGraph):
                if 'function_order' not in graph.graph['problem_formulation']:
                    graph.add_nested_attribute(['problem_formulation', 'function_order'], None)
                if 'mdao_architecture' not in graph.graph['problem_formulation']:
                    graph.add_nested_attribute(['problem_formulation', 'mdao_architecture'], 'undefined')
                if 'allow_unconverged_couplings' not in graph.graph['problem_formulation']:
                    graph.add_nested_attribute(['problem_formulation', 'allow_unconverged_couplings'], False)
                graph.add_function_problem_roles()

            # Save as kdms file
            if fileType == "kdms":
                graph.save(os.path.join(session_folder, fileName), file_type=fileType,
                           graph_check_critical=False,
                           mpg=mpg)
                file = fileName + ".kdms"
                files.append(file)
                if mpg is not None:
                    mpgfile = fileName + "_mpg.kdms"
                    files.append(mpgfile)
            # Save as CMDOWS file
            elif fileType == "cmdows":
                graph.save(os.path.join(session_folder, fileName), file_type=fileType,
                           graph_check_critical=False, mpg=mpg, pretty_print=True)
                file = fileName+".xml"
                files.append(file)
            else:
                return "ERROR: Wrong file type!!!"

            return files

        except Exception as e:
            return "ERROR: {}.".format(e.message)
            # Logs the error appropriately.

    @app.route('/kadmos_save_vistoms_graph', methods=['POST'])
    def kadmos_save_vistoms_graph():
        """
           Function saves current graph as new VISTOMS graph and returns it to the VISTOMS package
           in the browser

           :return: the graph compressed as VISTOMS data
        """
        try:
            # get request form
            graphID = request.form['graphID']
            newGraphName = request.form['newGraphName']
            newGraphDesc = request.form['newGraphDesc']
            newGraphID = request.form['newGraphID']
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')

            tmpDir = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(tmpDir, mpgFileName)):
                graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
                mpg = load(os.path.join(tmpDir, mpgFileName), file_check_critical=False)
            else:
                graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
                mpg = None

            newFileName = TEMP_FILE + '_' + newGraphID + '.kdms'
            graph.graph['name'] = newGraphName
            graph.graph['description'] = newGraphDesc
            graph.graph['id'] = newGraphID
            graph.save(os.path.join(session_folder, newFileName), file_type="kdms", graph_check_critical=False, mpg=mpg)

            newVistomsData = graph.vistoms_add_json(function_order=function_order, mpg=mpg, graph_id=newGraphID)

            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_delete_graphs', methods=['POST'])
    def kadmos_delete_graphs():
        """
           Function finds all graphs that have been temporarily stored in the temp folder and returns them
           to the VISTOMS package in the browser. This function is always called when the browser is refreshed by the user.

           :return: the graphs compressed as VISTOMS data
        """
        try:
            # get request form
            graphIDs_str = request.form['graphIDs']
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            tmpDir = session_folder
            graphIDs = json.loads(graphIDs_str)
            for graphID in graphIDs:
                graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
                backupGraphFileName = TEMP_FILE + '_' + graphID + '_backup.kdms'
                mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
                backupMpgFileName = TEMP_FILE + '_' + graphID + '_mpg_backup.kdms'
                if os.path.exists(os.path.join(tmpDir, graphFileName)):
                    os.remove(os.path.join(tmpDir, graphFileName))
                if os.path.exists(os.path.join(tmpDir, backupGraphFileName)):
                    os.remove(os.path.join(tmpDir, backupGraphFileName))
                if os.path.exists(os.path.join(tmpDir, mpgFileName)):
                    os.remove(os.path.join(tmpDir, mpgFileName))
                if os.path.exists(os.path.join(tmpDir, backupMpgFileName)):
                    os.remove(os.path.join(tmpDir, backupMpgFileName))

            return kadmos_find_temp_graphs()

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_find_temp_graphs', methods=['POST'])
    def kadmos_find_temp_graphs():
        """
           Function finds all graphs that have been temporarily stored in the temp folder and returns them
           to the VISTOMS package in the browser. This function is always called when the browser is refreshed by the user.

           :return: the graphs compressed as VISTOMS data
        """
        try:
            # First determine session folder
            session_id = request.form['sessionId']
            try:
                session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id, add_usage_stamp=True)
            except:  # If a session is not found, then create an empty instance on the server.
                # Get directory with sessions
                sessions_dir = SESSIONS_CATALOG_FOLDER

                # Add the json file of the session to the sessions directory
                session_details = dict(folder=os.path.join(SESSIONS_FOLDER_SERVER, session_id),
                                       creation_date=str(datetime.now()))
                with open(os.path.join(sessions_dir, session_id + '.json'), 'w') as outfile:
                    json.dump(session_details, outfile)

                os.makedirs(os.path.join(SESSIONS_FOLDER_SERVER, session_id))

                session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id, add_usage_stamp=True)

            # First of all, delete all graphs, that end with a _backup
            delete_backup_graphs(session_folder)

            tmpDir = session_folder
            newVIstomsDataArray = []
            file_list = os.listdir(tmpDir)
            if file_list:
                file_list.sort()
            for file in file_list:
                if file.endswith(".kdms"):
                    fileName = file.split('.')[0].split('_')
                    graphID = fileName[1]
                    if "mpg" not in fileName: # Do not loop through mpg files
                        graphFileName = fileName[0] + "_" + graphID + ".kdms"
                        mpgFileName = fileName[0] + "_" + graphID + "_mpg.kdms"
                        if os.path.exists(os.path.join(tmpDir, mpgFileName)):
                            graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
                            mpg = load(os.path.join(tmpDir, mpgFileName), file_check_critical=False)
                        else:
                            graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
                            mpg = None

                        # Use function order for VISTOMS if it is available in the graph information
                        function_order = None
                        if graph.graph_has_nested_attributes('problem_formulation', 'function_order') and mpg is None:
                            function_order = graph.graph['problem_formulation']['function_order']

                        graph.save(os.path.join(session_folder, graphFileName), file_type="kdms",
                                   graph_check_critical=False, mpg=mpg)

                        newVIstomsDataArray.append(graph.vistoms_add_json(graph_id=graphID,
                                                                          function_order=function_order, mpg=mpg))
            return jsonify(newVIstomsDataArray)

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_revert_step', methods=['POST'])
    def kadmos_revert_step():
        """
           Function to revert the last graph manipulation step by returning the _backup file from the tepm folder
           :return: the graph compressed as VISTOMS data
        """
        try:
            # get request form
            graphID = request.form['graphID']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            tmpDir = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            backupGraphFileName = TEMP_FILE + '_' + graphID + '_backup.kdms'
            backupMpgFileName = TEMP_FILE + '_' + graphID + '_backup_mpg.kdms'

            graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
            backupGraph = load(os.path.join(tmpDir, backupGraphFileName), file_check_critical=False)
            if os.path.exists(os.path.join(tmpDir, mpgFileName)):
                mpg = load(os.path.join(tmpDir, mpgFileName), file_check_critical=False)
                os.remove(os.path.join(tmpDir, mpgFileName))
            else:
                mpg = None

            if os.path.exists(os.path.join(tmpDir, backupMpgFileName)):
                backupMpg = load(os.path.join(tmpDir, backupMpgFileName), file_check_critical=False)
                os.remove(os.path.join(tmpDir, backupMpgFileName))
            else:
                backupMpg = None

            # Switch graph and backup graph (What used to be the backup graph is now the new graph and vice versa)
            graph.save(os.path.join(session_folder, backupGraphFileName), file_type="kdms", graph_check_critical=False,
                       mpg=mpg)
            backupGraph.save(os.path.join(session_folder, graphFileName), file_type="kdms", graph_check_critical=False,
                             mpg=backupMpg)

            # Get function_oder of the backup graph
            function_order = None
            if backupGraph.graph_has_nested_attributes('problem_formulation', 'function_order'):
                function_order = backupGraph.graph['problem_formulation']['function_order']

            newVistomsData = backupGraph.vistoms_add_json(function_order=function_order,  mpg=backupMpg,
                                                          graph_id=graphID)
            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    def savePreviousGraph(graph_id, session_id):
        """
            Function saves the last graph, so you can revert a graph change within VISTOMS

            :param graph: Initial fundamental problem graph (FPG) to start working on the MDAO architecture definition
            :return: New VISTOMS json data with initial FPG
        """
        path = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)
        # current graph and mpg name
        graphFileName = TEMP_FILE + '_' + graph_id + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graph_id + '_mpg.kdms'

        # Save graph as backup file
        backupGraphFileName = TEMP_FILE + '_' + graph_id + '_backup.kdms'
        copyfile(os.path.join(path, graphFileName), os.path.join(path, backupGraphFileName))
        if os.path.exists(os.path.join(path, mpgFileName)):
            # If mpg exists, save it as well
            backupMpgFileName = TEMP_FILE + '_' + graph_id + '_mpg_backup.kdms'
            copyfile(os.path.join(path, mpgFileName), os.path.join(path, backupMpgFileName))

    def delete_backup_graphs(session_folder):
        """
            Function deletes all graphs that end with a _backup
        """
        for file in os.listdir(session_folder):
            if fnmatch.fnmatch(file, '*_backup*'):
                os.remove(os.path.join(session_folder, file))

    ####################################################################################################################
    # Graph inspection functions
    ####################################################################################################################
    @app.route('/kadmos_find_all_nodes', methods=['POST'])
    def kadmos_find_all_nodes():
        """
            Function to get all nodes from certain categories and return them

            :param method: The method for sorting the nodes. Specified by the user from VISTOMS
            :return: New VISTOMS json data with updated design competences
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            category = str(request.form['category'])
            sub_category = str(request.form['sub_category'])
            attr_cond = ast.literal_eval(request.form['attr_cond'])
            attr_include = ast.literal_eval(request.form['attr_include'])
            attr_exclude = ast.literal_eval(request.form['attr_exclude'])
            xPath_include = str(request.form['xPath_include']).split(', ')
            xPath_exclude = str(request.form['xPath_exclude']).split(', ')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

            if attr_cond == []:
                attr_cond = None
            if attr_include == []:
                attr_include = None
            if attr_exclude == []:
                attr_exclude = None
            if xPath_include == [""]:
                xPath_include = None
            if xPath_exclude == [""]:
                xPath_exclude = None

            allNodes = graph.find_all_nodes(category=category, subcategory=sub_category, attr_cond=attr_cond,
                                            attr_include=attr_include, attr_exclude=attr_exclude,
                                            xpath_include=xPath_include, xpath_exclude=xPath_exclude)

            # allNodes_str = ', '.join(str(e) for e in allNodes)
            allNodes_str = json.dumps(allNodes)

            return allNodes_str

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_L1_check', methods=['POST'])
    def kadmos_L1_check():
        """
            Function to perform category a checks on the graph

            :return: Message, whether the check was successful or not
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)

            check_result = graph._check_category_a()

            if check_result[0]:
                return "Check successful!"
            else:
                return "ERROR: Check was not successful. For further information, please consult the python log"

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_L2_check', methods=['POST'])
    def kadmos_L2_check():
        """
            Function to perform category b checks on the graph

            :return: Message, whether the check was successful or not
        """
        try:
            # Get request form
            graphID = request.form['graphID']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)


            check_result = graph._check_category_b()

            if check_result[0]:
                return "Check successful!"
            else:
                return "ERROR: Check was not successful. For further information, please consult the python log"

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_L3_check', methods=['POST'])
    def kadmos_L3_check():
        """
            Function to perform category c checks on the graph

            :return: Message, whether the check was successful or not
        """
        try:
            # Get request form
            graphID = request.form['graphID']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)

            check_result = graph._check_category_c()

            if check_result[0]:
                return "Check successful!"
            else:
                return "ERROR: Check was not successful. For further information, please consult the python log"

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    ####################################################################################################################
    # Upload custom kadmos script
    ####################################################################################################################
    @app.route('/kadmos_run_custom_script', methods=['POST'])
    def kadmos_run_custom_script():
        """
            Generic function to import and execute a custom kadmos script

            :param script_file: the custom kadmos script
            :param graph: the kadmos graph, on which the changes are performed
            :return: newVistomsData: Merged string of the vistoms data and the script string value
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)
            uploaded_files = request.files.getlist("file[]")

            script_file = []
            for aFile in uploaded_files:
                file_type = aFile.filename.rsplit('.', 1)[1].lower()
                if not file_type == "py":
                    return "ERROR: wrong file type \"" + file_type + "\""
                script_file = aFile

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

            # save kadmos script in temp folder
            script_file.save(os.path.join(session_folder, script_file.filename))
            kadmos_file_path = os.path.join(session_folder, script_file.filename)

            # execute script and return graph data (graph, mpg)
            import imp
            script_module = imp.load_source('kadmos_custom_fun_{}', kadmos_file_path)
            graph, mpg = script_module.script(graph, mpg)

            # Get function order for VISTOMS in case of FPG
            function_order = None
            if mpg is None:
                # Get function_oder of the graph after the script has done the manipulations
                if graph.graph_has_nested_attributes('problem_formulation', 'function_order'):
                    function_order = graph.graph['problem_formulation']['function_order']

            # Add modified graph to VISTOMS
            newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            graph.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                       graph_check_critical=False, mpg=mpg)
            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    ####################################################################################################################
    # FPG manipulation functions
    ####################################################################################################################
    @app.route('/kadmos_start_defining_MDO_problem', methods=['POST'])
    def kadmos_start_defining_MDO_problem():
        """
            Function to start an MDO problem

            :param fpg_initial: Initial fundamental problem graph (FPG) to start working on the MDO problem definition
            :return: New VISTOMS json data with initial FPG
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            functionOrder = request.form['currentOrder'].split(',')
            newGraphID = request.form['newGraphID']
            newGraphName = request.form['newGraphName']
            newGraphDesc = request.form['newGraphDesc']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            newFileName = TEMP_FILE + '_' + newGraphID + '.kdms'

            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: Graph is already an MDPG! FPG Cannot be initialized again!"
            else:
                mpg = None

                graph = load(os.path.join(path, graphFileName), file_check_critical=False)

                if isinstance(graph, FundamentalProblemGraph):
                    return "ERROR: Graph is already an FPG and cannot be initialized again!"
                fpg_initial = graph.deepcopy_as(FundamentalProblemGraph)

                fpg_initial.graph['name'] = newGraphName
                fpg_initial.graph['description'] = newGraphDesc
                fpg_initial.graph['problem_formulation'] = dict()
                fpg_initial.graph['problem_formulation']['function_order'] = functionOrder
                fpg_initial.graph['problem_formulation']['mdao_architecture'] = "None"

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg_initial.vistoms_add_json(graph_id=newGraphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg_initial.save(os.path.join(session_folder, newFileName), file_type="kdms",
                                 graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_add_DC_metadata', methods=['POST'])
    def kadmos_add_DC_metadata():
        """
            Function adds metadata to a dc in the graph
            :param graphID: ID of the current graph
            :return: VISTOMS json data with graph information
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            nodeName = request.form['nodeName']
            metadata_str = request.form['metadata_str']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # read json data
            metadata_py = json.loads(metadata_str)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None
            graph.add_dc_general_info(nodeName, description=metadata_py['general_info']['description'],
                                      status=metadata_py['general_info']['status'],
                                      owner_uid=metadata_py['general_info']['owner_uid'],
                                      creator_uid=metadata_py['general_info']['creator_uid'],
                                      operator_uid=metadata_py['general_info']['operator_uid'])
            graph.add_dc_performance_info(nodeName, precision=metadata_py['performance_info']['precision'],
                                          fidelity_level=metadata_py['performance_info']['fidelity_level'],
                                          run_time=metadata_py['performance_info']['run_time'],
                                          verification=metadata_py['performance_info']['verification'])
            graph.add_dc_licensing(nodeName, license_type=metadata_py['licensing']['license_type'],
                                   license_specification=metadata_py['licensing']['license_specification'],
                                   license_info=metadata_py['licensing']['license_info'])
            graph.add_dc_sources(nodeName, repository_link=metadata_py['sources']['repository_link'],
                                 download_link=metadata_py['sources']['download_link'],
                                 references=metadata_py['sources']['references'])

            local_component = metadata_py['execution_details']['local_component']
            if local_component:
                graph.add_dc_execution_details(nodeName, operating_system=metadata_py['execution_details']['operating_system'],
                                               integration_platform=metadata_py['execution_details']['integration_platform'],
                                               command=metadata_py['execution_details']['command'],
                                               description=metadata_py['execution_details']['description'],
                                               software_requirements=metadata_py['execution_details']['software_requirements'],
                                               hardware_requirements=metadata_py['execution_details']['hardware_requirements'])

            remote_component = metadata_py['remote_component_info']['remote_component']
            if remote_component:
                graph.add_dc_remote_component_info(nodeName, single_or_multi_execution=metadata_py['remote_component_info']['single_or_multi_execution'],
                                                   job_name=metadata_py['remote_component_info']['job_name'],
                                                   remote_engineer=metadata_py['remote_component_info']['remote_engineer_uid'],
                                                   notification_message=metadata_py['remote_component_info']['notification_message'],
                                                   data_exchange_dict= {'urlsite': metadata_py['remote_component_info']['urlsite'],'folder': metadata_py['remote_component_info']['folder']})

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Use function order for VISTOMS if it is available in the graph information
            if graph.graph_has_nested_attributes('problem_formulation', 'function_order') and mpg is None:
                graph.graph['problem_formulation']['function_order'] = function_order
            # Save the graph in temp/tmp.kdms
            graph.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                       graph_check_critical=False, mpg=mpg)

            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_add_mathematical_function', methods=['POST'])
    def kadmos_add_mathematical_function():
        """
            Function adds a mathematical function to the graph
            :param graphID: ID of the current graph
            :return: VISTOMS json data with graph information
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'] != '':
                function_order = request.form['currentOrder'].split(',')
            form_data_str = request.form['form_data']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # convert stringified data into python objects/arrays/.. with json.loads function
            form_data_py = json.loads(form_data_str)

            # Get information from form_data_py
            function_node = form_data_py['function_node']
            input_nodes_xPath = form_data_py['input_nodes_xPath'].split(',')
            input_nodes_name = form_data_py['input_nodes_name'].split(',')
            output_node_xPath = form_data_py['output_node_xPath']
            equation = form_data_py['equation']
            language = form_data_py['language']

            # Save previous graph as backup before making the changes to the graph
            savePreviousGraph(graphID, session_id)

            # Load the current graph from the temporary folder
            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot add a design competence to an MPG! Please go back to the RCG to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                # Get input_nodes and output_nodes from request form data
                input_nodes = []
                for idx, xPath in enumerate(input_nodes_xPath):
                    input_node = [xPath, input_nodes_name[idx]]
                    input_nodes.append(input_node)
                output_nodes = [[output_node_xPath, equation, language]]

                # Add the new mathematical function to the graph as a new competence block
                graph.add_mathematical_function(input_nodes=input_nodes, function_node=function_node,
                                                output_nodes=output_nodes)

                # Add the new mathematical function to the function list (function_order)
                if function_order is None:
                    function_order = []
                function_order.append(function_node)

                # The graph with the added mathematical function is now saved as json data for vistoms
                newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Use function order for VISTOMS if it is available in the graph information
                if graph.graph_has_nested_attributes('problem_formulation', 'function_order') and mpg is None:
                    graph.graph['problem_formulation']['function_order'] = function_order
                # Save the graph in temp/tmp.kdms
                graph.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                           graph_check_critical=False, mpg=mpg)

                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_add_design_competence', methods=['POST'])
    def kadmos_add_design_competence():
        """
            Function adds a dc to the graph
            :param graphID: ID of the current graph
            :return: VISTOMS json data with graph information
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            function_node = request.form['function_node'].replace(" ", "")
            input_xml = request.files['input_xml']
            output_xml = request.files['output_xml']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot add a design competence to an MPG! Please go back to the RCG to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                # Here the dc cmdows file is loaded
                # Save the template cmdows file in the tmp folder
                cmdows_template = os.path.join(os.path.split(__file__)[0], 'templates', 'cmdows_template.xml')
                cmdows_file = os.path.join(session_folder, 'cmdows_template.xml')
                # Write the new competence to the CMDOWS template xml file
                tree = ET.parse(cmdows_template)
                root = tree.getroot()
                dc_element = root.find("./executableBlocks/designCompetences/designCompetence")
                dc_element.find("ID").text = function_node
                uid = function_node
                dc_element.set('uID', uid)
                tree.write(cmdows_file)

                # Copy the uploaded input/outut files to the tmp folder
                input_xml_file = os.path.join(session_folder, function_node + '-input.xml')
                output_xml_file = os.path.join(session_folder, function_node + '-output.xml')
                input_xml.save(input_xml_file)
                output_xml.save(output_xml_file)

                # Load design competence with cmdows template file
                graph_dc = load(cmdows_file, check_list=['consistent_root', 'invalid_leaf_elements'])

                os.remove(cmdows_file)
                os.remove(input_xml_file)
                os.remove(output_xml_file)

                # Here the original graph and the new graph including the design competence are merged
                new_graph = KadmosGraph(nx.compose(graph, graph_dc))
                if isinstance(graph, RepositoryConnectivityGraph):
                    new_graph = RepositoryConnectivityGraph(new_graph)
                elif isinstance(graph, FundamentalProblemGraph):
                    new_graph = FundamentalProblemGraph(new_graph)
                else:
                    raise AssertionError("ERROR: Could find graph type!")

                # new_graph.graph['name'] = graph.graph['name']
                # new_graph.graph['id'] = graphID
                # new_graph.graph['description'] = graph.graph['description']

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = new_graph.vistoms_add_json(graph_id=graphID, mpg=mpg)

                # Save the graph in temp/tmp.kdms
                new_graph.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                               graph_check_critical=False, mpg=mpg)

                return newVistomsData

        except Exception as e:
            return "ERROR: {}".format(e)
            # Logs the error appropriately.

    @app.route('/kadmos_edit_contact_infos', methods=['POST'])
    def kadmos_edit_contact_infos():
        """
            Function adds a dc to the graph
            :param graphID: ID of the current graph
            :return: VISTOMS json data with graph information
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            organization = json.loads(request.form['organization'])
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

            # Set the new organization from VISTOMS request
            graph.graph['organization'] = organization

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = graph.vistoms_add_json(graph_id=graphID, mpg=mpg, function_order=function_order)

            # Save the graph in temp/tmp.kdms
            graph.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                       graph_check_critical=False, mpg=mpg)

            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_change_node_pos', methods=['POST'])
    def kadmos_change_node_pos():
        """
            Function to change the position of a node (competence) within the graph

            :param newPos: Initial fundamental problem graph (FPG) to start working on the MDO problem definition
            :return: New VISTOMS json data with initial FPG
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            nodeName = str(request.form['nodeName'])
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            newPos = int(request.form['newPos'])

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot change a competence's position on an existing MPG! Please go back to the " \
                       "FPG or RCG to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                # Change position of a node in th XDSM

                # Get tool list and put the coordinator in the top left corner
                function_order.remove(nodeName)
                function_order.insert(newPos, nodeName)
                if isinstance(graph, FundamentalProblemGraph):
                    graph.graph['problem_formulation']['function_order'] = function_order
                    if 'problem_role' in graph.nodes[function_order[0]]:
                        graph.add_function_problem_roles()

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                graph.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                           graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_delete_node', methods=['POST'])
    def kadmos_delete_node():
        """
            Function deletes a node from the graph and returns the updated graph data to VISTOMS
            :param nodeName: name of the node to be deleted
            :return: VISTOMS json data with graph information
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            nodeName = str(request.form['nodeName'])
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot remove a competence from an existing MPG! Please go back to the FPG or RCG" \
                       " to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                # remove the node from the graph
                graph.remove_function_nodes(nodeName)
                # update function order
                function_order.remove(nodeName)

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Use function order for VISTOMS if it is available in the graph information
                if graph.graph_has_nested_attributes('problem_formulation', 'function_order') and mpg is None:
                    graph.graph['problem_formulation']['function_order'] = function_order
                # Save the graph in temp/tmp.kdms
                graph.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                           graph_check_critical=False, mpg=mpg)

                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_delete_edge', methods=['POST'])
    def kadmos_delete_edge():
        """
            Function deletes an edge from the graph and returns the updated graph data to VISTOMS
            :param nodeName: name of the node that is the input provider of the edge
            :param edgeName: name of the edge to be deleted
            :return: VISTOMS json data with graph information
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            nodeName = str(request.form['nodeName'])
            edgeName = str(request.form['edgeName'])
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

            # remove the edge
            graph.remove_edge(nodeName,edgeName)
            # Add the graph with the updated function order to VISTOMS
            newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            graph.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                       graph_check_critical=False, mpg=mpg)

            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_exclude_DCs', methods=['POST'])
    def kadmos_exclude_DCs():
        """
            Function to exclude design competences as requested by the user from VISTOMS

            :param nodeList: List of competences that shall be excluded
            :return: New VISTOMS json data with excluded design competences deleted
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            nodeList = request.form['nodeList'].split(',')
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot remove a competence from an existing MPG! Please go back to the FPG or RCG " \
                       "to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                fpg = FundamentalProblemGraph(graph)

                # Remove a node from the graph
                for nodeName in nodeList:
                    fpg.remove_function_nodes(nodeName)
                    function_order.remove(nodeName)
                # Assign new function order to problem formulation
                fpg.graph['problem_formulation']['function_order'] = function_order

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_merge_seq_DCs', methods=['POST'])
    def kadmos_merge_seq_DCs():
        """
            Function to merge design competences that run sequentially as requested by the user from VISTOMS

            :param nodeList: List of competences that shall be merged
            :return: New VISTOMS json data with merged design competences
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            nodeList = request.form['nodeList'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to " \
                       "do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None
                new_node = '-'.join(nodeList) + '--seq'

                if isinstance(graph, FundamentalProblemGraph):
                    fpg = graph
                else:
                    fpg = FundamentalProblemGraph(graph)

                fpg = fpg.merge_sequential_functions(nodeList, new_label=new_node)
                # adjust function order
                function_order = [new_node if func == nodeList[0] else func for func in function_order]
                for func in nodeList[1:]:
                    function_order.remove(func)
                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_merge_parallel_DCs', methods=['POST'])
    def kadmos_merge_parallel_DCs():
        """
            Function to merge design competences that run in parallel as requested by the user from VISTOMS

            :param nodeList: List of competences that shall be merged
            :return: New VISTOMS json data with merged design competences
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            nodeList = request.form['nodeList'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to " \
                       "do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                new_node = '-'.join(nodeList) + '--par'

                if isinstance(graph, FundamentalProblemGraph):
                    fpg = graph
                else:
                    fpg = FundamentalProblemGraph(graph)

                fpg = fpg.merge_parallel_functions(nodeList, new_label=new_node)
                # adjust function order
                function_order = [new_node if func == nodeList[0] else func for func in function_order]
                for func in nodeList[1:]:
                    function_order.remove(func)

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_merge_func_mod_DCs', methods=['POST'])
    def kadmos_merge_func_mod_DCs():
        """
            Function to merge design competences that run in different modes as requested by the user from VISTOMS

            :param nodeList: List of competences that shall be merged
            :return: New VISTOMS json data with merged design competences
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            nodeList = request.form['nodeList'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to " \
                       "do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                if isinstance(graph, FundamentalProblemGraph):
                    fpg = graph
                else:
                    fpg = FundamentalProblemGraph(graph)

                base_function = fpg.node[nodeList[0]]['name']
                modes = [str(string[string.find('[') + 1:string.find(']')]) for string in nodeList]
                suffices = [str(string[string.find('_'):string.find('[')]) for string in nodeList]
                new_node = base_function + '-merged[' + str(len(nodeList)) + 'modes]'

                fpg = fpg.merge_function_modes(base_function, modes, new_label=new_node, version='1.0', instance=0,
                                               suffices=suffices)
                # adjust function order
                function_order = [new_node if func == nodeList[0] else func for func in function_order]
                for func in nodeList[1:]:
                    function_order.remove(func)

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_remove_collision', methods=['POST'])
    def kadmos_remove_collision():
        """
            Function to remove collisions coming from specific design competences as requested by the user from VISTOMS

            :param nodeList: List of competences for which collisions should be removed
            :return: New VISTOMS json data with updated design competences
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            nodeList = request.form['nodeList'].split(',')
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to " \
                       "do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None


                if isinstance(graph, FundamentalProblemGraph):
                    fpg = graph
                else:
                    fpg = FundamentalProblemGraph(graph)

                for collision_source in nodeList:
                    fpg.disconnect_problematic_variables_from(collision_source)

                    fpg.graph['problem_formulation']['function_order'] = function_order

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_get_possible_function_order', methods=['POST'])
    def kadmos_get_possible_function_order():
        """
            Function to get a possible function order

            :param method: The method for sorting the nodes. Specified by the user from VISTOMS
            :return: New VISTOMS json data with updated design competences
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            method = request.form['sortingMethod']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to " \
                       "do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                if isinstance(graph, FundamentalProblemGraph):
                    fpg = graph
                else:
                    fpg = FundamentalProblemGraph(graph)

                # Getting the possible function order with the method specified by the user
                function_order = fpg.get_possible_function_order(method)
                fpg.add_nested_attribute(['problem_formulation', 'mdao_architecture'], 'undefined')
                fpg.graph['problem_formulation']['function_order'] = function_order
                if 'problem_role' in fpg.nodes[function_order[0]]:
                    fpg.add_function_problem_roles()

                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)

                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_make_all_variables_valid', methods=['POST'])
    def kadmos_make_all_variables_valid():
        """
            Function to make all variables from the graph valid --> Eliminates colissions

            :return: New VISTOMS json data with updated design competences
        """
        try:
            # get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot do that on an existing MPG! Please go back to the FPG or RCG to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                if isinstance(graph, FundamentalProblemGraph):
                    fpg = graph
                else:
                    fpg = FundamentalProblemGraph(graph)

                fpg.graph['problem_formulation']['function_order'] = function_order

                # Function to check the graph for collisions and holes. Collisions are solved based on the function
                # order and holes will simply be removed.
                fpg.make_all_variables_valid()


                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_add_function_problem_roles', methods=['POST'])
    def kadmos_add_function_problem_roles():
        """
            Function to Add the problem function roles to the graph

            :return: New VISTOMS json data with updated design competences
        """
        try:
            # get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot do that on an existing MPG! Please go back to the FPG or RCG to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                if isinstance(graph, FundamentalProblemGraph):
                    fpg = graph
                else:
                    fpg = FundamentalProblemGraph(graph)

                fpg.graph['problem_formulation']['function_order'] = function_order

                # Add the function problem roles (pre-coupling, coupled, post-coupling)
                fpg.add_function_problem_roles()

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_mark_variable', methods=['POST'])
    def kadmos_mark_variable():
        """
            Function to mark a variable as "special variable" (constraint, objective, design variable, quantity of
            interest)
            :param xPath: xPath of the variable in the XML schema
            :param variableType: type of the variable it shall be marked as
            :return: VISTOMS json data with graph information
        """
        try:
            # get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            variableData_str = request.form['variableData_str']
            # read json data
            variableData_py = json.loads(variableData_str)

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName =  TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName =  TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return 'ERROR: This function can only be performed on an FPG!'
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)
            for data in variableData_py:
                if data['variableType'] == 'designVariable':
                    if data['samples']:
                        samples = data['samples'].split('[,;]')
                    else:
                        samples = []
                    fpg.mark_as_design_variable(data['xPath'], nominal_value=float(data['nominalValue']),
                                                upper_bound=float(data['upperBound']),
                                                lower_bound=float(data['lowerBound']),
                                                samples=samples if samples is not [] else None)
                elif data['variableType'] == 'objective':
                    fpg.mark_as_objective(data['xPath'])
                elif data['variableType'] == 'constraint':
                    fpg.mark_as_constraint(data['xPath'], reference_value=float(data['nominalValue']),
                                           operator=data['operator'])
                elif data['variableType'] == 'quantityOfInterest':
                    fpg.mark_as_qois([data['xPath']])
                else:
                    return "ERROR: Something went wrong in KADMOS!"

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                     graph_check_critical=False, mpg=mpg)

            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_unmark_variable', methods=['POST'])
    def kadmos_unmark_variable():
        """
            Function to unmark a previously marked variable
            :param xPath: xPath of the variable in the XML schema
            :return: VISTOMS json data with graph information
        """
        try:
            # get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            xPath = request.form['xPath']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName =  TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName =  TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return 'ERROR: This function can only be performed on an FPG!'
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            fpg.unmark_variable(xPath)

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'), file_type='kdms',
                     graph_check_critical=False, mpg=mpg)

            return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_remove_unused_outputs', methods=['POST'])
    def kadmos_remove_unused_outputs():
        """
            Function to remove all unused variables that are output to the coordinator

            :return: New VISTOMS json data with updated design competences
        """
        try:
            # get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            cleanUp_str = request.form['cleanUp']
            if cleanUp_str == 'True':
                cleanUp = True
            else:
                cleanUp = False

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot do that on an existing MPG! Please go back to the FPG or RCG to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                if isinstance(graph, FundamentalProblemGraph):
                    fpg = graph
                else:
                    fpg = FundamentalProblemGraph(graph)

                fpg.graph['problem_formulation']['function_order'] = function_order

                # Cleaning of the graph needs to be done in a while loop, to entirely remove all unused elements
                another_run = True
                counter = 0
                while another_run:
                    counter += 1
                    another_run = False
                    # Delete unused variables
                    output_nodes = fpg.find_all_nodes(subcategory='all outputs')
                    for output_node in output_nodes:
                        if 'problem_role' not in fpg.node[output_node]:
                            fpg.remove_node(output_node)
                            another_run = True
                    # Delete unnecessary functions automatically if the user wants to
                    if cleanUp:
                        function_nodes = fpg.find_all_nodes(category='function')
                        for function_node in function_nodes:
                            if not fpg.out_edges(function_node):
                                fpg.remove_function_nodes(function_node)
                                another_run = True

                # Add the function problem roles (pre-coupling, coupled, post-coupling)
                fpg.add_function_problem_roles()

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                fpg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    ########################################################################################################################

    # MDPG manipulation functions
    ########################################################################################################################
    @app.route('/kadmos_start_defining_MDAO_architecture', methods=['POST'])
    def kadmos_start_defining_MDAO_architecture():
        """
            Function to start an MDO problem definition

            :param graph: Initial fundamental problem graph (FPG) to start working on the MDAO architecture definition
            :return: New VISTOMS json data with initial FPG
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            functionOrder = request.form['currentOrder'].split(',')
            newGraphID = request.form['newGraphID']
            newGraphName = request.form['newGraphName']
            newGraphDesc = request.form['newGraphDesc']

            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            newFileName = TEMP_FILE + '_' + newGraphID + '.kdms'

            path = session_folder
            graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
            mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: Graph is already an MDPG! FPG Cannot be initialized again!"
            else:
                mpg = None

                graph = load(os.path.join(path, graphFileName), file_check_critical=False)

                if not isinstance(graph, FundamentalProblemGraph):
                    return "ERROR: Graph is not an FPG yet. Please perform the FPG Manipulation steps first!"

                # check if fpg is well defined
                check_result = graph._check_category_a()
                if check_result[0] != True:
                    return "ERROR: The FPG is not well defined yet. Please perform FPG manipulation steps first and" \
                           " check the graph again!"

                mdg = deepcopy(graph)
                mdg.graph['name'] = newGraphName
                mdg.graph['description'] = newGraphDesc
                mdg.graph['problem_formulation'] = dict()
                mdg.graph['problem_formulation']['function_order'] = functionOrder
                mdg.graph['problem_formulation']['mdao_architecture'] = "None"

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = mdg.vistoms_add_json(function_order=functionOrder, graph_id=newGraphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                mdg.save(os.path.join(session_folder, newFileName), file_type="kdms", graph_check_critical=False,
                         mpg=mpg)

                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.

    @app.route('/kadmos_impose_MDAO_architecture', methods=['POST'])
    def kadmos_impose_MDAO_architecture():
        """
            Function to wrap an MDAO architecture around the MDAO problem

            :param allowUnconvergedCouplings: Bool variable whether unconverged couplings are allowed or not
            :return: New VISTOMS json data with updated MDAO data and process graphs
        """
        try:
            # Get request form
            graphID = request.form['graphID']
            function_order = None
            if request.form['currentOrder'].split(',') != '':
                function_order = request.form['currentOrder'].split(',')
            mdao_architecture = request.form['mdao_architecture']
            doe_settings_py = json.loads(request.form['doe_settings'])
            coupling_decomposition = request.form['coupling_decomposition']
            coupled_functions_groups = json.loads(request.form['coupled_functions_groups'])
            allow_unconverged_couplings_str = request.form['allow_unconverged_couplings']
            if allow_unconverged_couplings_str == 'True':
                allow_unconverged_couplings = True
            else:
                allow_unconverged_couplings = False


            # Check whether the value in each doe setting can be converted to an int, if not leave it a string
            def is_int(s):
                try:
                    float(s)
                    return True
                except ValueError:
                    return False
            # Convert the doe_settings_py to the correct format for KADMOS graph['problem_formulation']['doe_settings']
            doe_settings = {}
            for doe_setting in doe_settings_py:
                value = doe_setting['value']
                if is_int(value):
                    value = int(value)
                doe_settings[doe_setting['name']] = value


            # First determine session folder
            session_id = request.form['sessionId']
            session_folder = retrieve_session_folder(SESSIONS_CATALOG_FOLDER, session_id)

            # Save previous graph as backup before making the changes
            savePreviousGraph(graphID, session_id)

            path = session_folder
            graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
            mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
            if os.path.exists(os.path.join(path, mpgFileName)):
                return "ERROR: You cannot perform this on an existing MPG! Please go back to the FPG to do so."
            else:
                graph = load(os.path.join(path, graphFileName), file_check_critical=False)
                mpg = None

                mdao_definition = mdao_architecture
                if coupling_decomposition == 'Gauss-Seidel':
                    mdao_definition += '-GS'
                elif coupling_decomposition == 'Jacobi':
                    mdao_definition += '-J'
                elif coupling_decomposition == '-':
                    coupling_decomposition = None

                if not isinstance(graph, FundamentalProblemGraph):
                    return "ERROR: Your graph is not an FPG yet. Please perform FPG manipulation steps before " \
                           "imposing an MDAO architecture!"

                fpg = graph

                mdao_definition = mdao_architecture
                if coupling_decomposition == 'Gauss-Seidel':
                    mdao_definition += '-GS'
                elif coupling_decomposition == 'Jacobi':
                    mdao_definition += '-J'
                elif coupling_decomposition == '-':
                    coupling_decomposition = None

                # Define settings of the problem formulation
                fpg.graph['problem_formulation'] = dict()
                fpg.graph['problem_formulation']['function_order'] = function_order
                fpg.graph['problem_formulation']['mdao_architecture'] = mdao_architecture
                fpg.graph['problem_formulation']['convergence_type'] = coupling_decomposition
                fpg.graph['problem_formulation']['allow_unconverged_couplings'] = allow_unconverged_couplings

                if mdao_architecture in ['converged-DOE', 'unconverged-DOE', 'BLISS-2000']:
                    if doe_settings['method'] not in fpg.OPTIONS_DOE_METHODS:
                        return "ERROR: Invalid DOE method selected, please select a DOE method from the dropdown list"
                    fpg.graph['problem_formulation']['doe_settings'] = doe_settings

                if len(coupled_functions_groups) > 0:
                    fpg.graph['problem_formulation']['coupled_functions_groups'] = coupled_functions_groups

                fpg.add_function_problem_roles()

                mdg, mpg = fpg.impose_mdao_architecture()

                mdg.name = str(fpg.name)

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = mdg.vistoms_add_json(graph_id=graphID, mpg=mpg)
                # Save the graph in temp/tmp.kdms
                mdg.save(os.path.join(session_folder, TEMP_FILE + '_' + graphID + '.kdms'),
                         file_type='kdms', graph_check_critical=False, mpg=mpg)
                return newVistomsData

        except Exception as e:
            return "ERROR: " + e.message
            # Logs the error appropriately.
    return app
########################################################################################################################


# Then in the run_vistoms handle the folder and open_vistoms
# arguments as follows:
def run_vistoms(folder=None, write_log=True, open_vistoms=True):
    global SESSIONS_CATALOG_FOLDER
    if open_vistoms:
        # Open VISTOMS when running the app.py in the beginning
        webbrowser.open_new('http://127.0.0.1:5000/start_vistoms_local')

    if write_log:
        # Settings for logging
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    if folder is None:
        # Create temporary directory
        SESSIONS_CATALOG_FOLDER = tempfile.mkdtemp()
    else:
        # Assert given folder
        if not isinstance(folder, string_types):
            raise AssertionError('Folder should be a string.')
        if not os.path.isabs(folder):
            folder = os.path.abspath(folder)
        # If folder does not exist, then create it recursively
        SESSIONS_CATALOG_FOLDER = folder
        if not os.path.isdir(SESSIONS_CATALOG_FOLDER):
            os.makedirs(SESSIONS_CATALOG_FOLDER)
    # Run the app
    app = interface()
    app.run(threaded=True, debug=False)


# In the app.py (or vistoms.py) I would do it like this at
# the end of the file (so you can run it directly from the
# vistoms.py file.
#
# Examples for running vistoms.py are then:
# python vistoms.py
# python vistoms.py -folder C:/Users/aigner/Desktop/vistoms_tmp
# python vistoms.py -open y -folder C:/Users/aigner/Desktop/vistoms_tmp
# python vistoms.py -open y -folder C:/Users/aigner/Desktop/vistoms_tmp -write_log y
if __name__ == '__main__':
    # Get system arguments
    args = sys.argv
    # Check if folder is given in args
    if '-folder' in args:
        folder = os.path.join(args[args.index('-folder') + 1],'')
        assert isinstance(folder, string_types), 'Folder should be a string.'
    else:
        folder = None
    # Check if open_vistoms is given in args
    if '-open' in args:
        open_vistoms = args[args.index('-open') + 1]
        assert open_vistoms.lower() in ['y', 'yes', 'n', 'no']
        if open_vistoms.lower() in ['y', 'yes']:
            open_vistoms = True
        elif open_vistoms.lower() in ['n', 'no']:
            open_vistoms = False
        else:
            raise IOError('Please provide valid argument for -open, either y or n.')
    else:
        open_vistoms = True  # default is to open
    # Check if write_log is given in args
    if '-write_log' in args:
        write_log = args[args.index('-write_log') + 1]
        assert write_log.lower() in ['y', 'yes', 'n', 'no']
        if write_log.lower() in ['y', 'yes']:
            write_log = True
        elif write_log.lower() in ['n', 'no']:
            write_log = False
        else:
            raise IOError('Please provide valid argument for -open, either y or n.')
    else:
        write_log = True
    # Now run the Python VISTOMS method that you have in app.py
    run_vistoms(folder=folder, write_log=write_log, open_vistoms=open_vistoms)