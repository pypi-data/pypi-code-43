from __future__ import print_function
import os
import zipfile
import shutil
import logging

from xml.etree import cElementTree as ET
from mcutk.util import rmtree

logger = logging.getLogger(__name__)


def install_pack_unzip(packfile, installdir):
    """
    install cmsis pack by unzip method.
        1. read .pdsc and get 'vendor'/'name'/'releaseversion'
        2. extract all files to installdir
    """
    archive = zipfile.ZipFile(packfile, mode='r')
    files = archive.namelist()
    pdscfilename = [item for item in files if item.endswith(".pdsc")][0]
    content = archive.read(pdscfilename)
    tree = ET.fromstring(content)
    vendor = tree.find("vendor").text
    name = tree.find("name").text
    version = tree.find("releases/release").attrib["version"]

    packdir = os.path.join(installdir, vendor, name)
    if os.path.exists(packdir):
        logging.debug(packfile)
        logger.debug("remove %s", packdir)
        rmtree(packdir)

    install_path = os.path.join(installdir, vendor, name, version)
    logging.debug("  Vendor: {0}, Name: {1}, Version: {2}".format(
        vendor, name, version))
    # try several times to make sure the folder is removed
    for _ in range(3):
        try:
            if os.path.exists(install_path):
                print("    deleting exists version...")
                rmtree(install_path)
            break
        except Exception as e:
            print(e)
            print("      failed: try again..")

    os.makedirs(install_path)
    archive.extractall(install_path)
    archive.close()

    if "DFP" in install_path:
        flashalgos = [x.attrib['name']
                      for x in tree.findall('devices/family/device/algorithm')]
        # validate flash algos
        if flashalgos:
            for algo in flashalgos:
                algo_path = os.path.join(install_path, algo)
                if not os.path.exists(algo_path):
                    logging.critical(
                        'Validate FLM failed: Flash Algo "%s" is not exists!', algo_path)
                    return None
        else:
            logging.critical(
                'Validate FLM failed: .pdsc not contains the Flash Algo information!')
            return None

    if os.path.exists(install_path+"/"+pdscfilename):
        logger.debug("install successfully")
        return install_path
    else:
        logger.critical("install failed")
        return None
