#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# @copyright Copyright (C) Guichet Entreprises - All Rights Reserved
# 	All Rights Reserved.
# 	Unauthorized copying of this file, via any medium is strictly prohibited
# 	Dissemination of this information or reproduction of this material
# 	is strictly forbidden unless prior written permission is obtained
# 	from Guichet Entreprises.
###############################################################################

###############################################################################
# Template generation for xenon2
###############################################################################

import os
import os.path
import logging
import codecs
import urllib.request
import shutil
from zipfile import ZipFile
import yaml
import gitlab
import pymdtools.common as common
import pymdtools.mdcommon

# -----------------------------------------------------------------------------
def get(destination_folder, name, version=None):
    """ Get the template from gitlab and update template.

    @return the configuration fielname
    """
    logging.info("Get the xenon2 release name=%s version=%s",
                 name, version or "latest")
    project_id = '14250502'
    server = 'https://gitlab.com/'
    conf_filename = 'template_conf.yml'

    destination_folder = common.check_create_folder(destination_folder)
    conf_filename = os.path.join(destination_folder, conf_filename)

    if version is not None and version.lower() == "local":
        return conf_filename

    if version is None or version.lower() == "latest":
        project = gitlab.Gitlab(server).projects.get(project_id)
        release_tag = [release.tag_name for release in project.releases.list()]
        release_tag.sort()
        version = release_tag[-1]
        version = version.replace("v", "")
        logging.info("The latest release is %s", version)

    if os.path.isfile(conf_filename):
        with codecs.open(conf_filename, "r", "utf-8") as ymlfile:
            conf = yaml.load(ymlfile, Loader=yaml.FullLoader)
        current_version = conf['version']
        current_package = None
        if 'package_name' in conf:
            current_package = conf['package_name']
        logging.info('Current_version is %s', current_version)
        logging.info('Current_package_name is %s', current_package)
        if current_version == version and current_package == name:
            logging.info('Already have it')
            return conf_filename

    logging.info('Go for a download')
    project = gitlab.Gitlab(server).projects.get(project_id)
    description_md = project.releases.get("v" + version).description
    links = pymdtools.mdcommon.search_link_in_md_text(description_md)

    url = None
    for link in links:
        if link['name'].startswith(name):
            url = link['url']
    if url is None:
        logging.warning('Cannont find the version %s of %s', version, name)
        raise Exception('Cannont find the version %s of %s' % (version, name))
    url = project.web_url + url

    if os.path.isdir(destination_folder):
        logging.info('Clean folder %s', destination_folder)
        shutil.rmtree(destination_folder)
        common.check_create_folder(destination_folder)

    dest_filename = os.path.join(
        destination_folder, name + "-" + release_tag[-1] + ".zip")
    logging.info('Download %s --> %s', url, dest_filename)
    urllib.request.urlretrieve(url, dest_filename)

    logging.info('Extract %s', dest_filename)
    with ZipFile(dest_filename, 'r') as zip_obj:
        zip_obj.extractall(destination_folder)

    return conf_filename
