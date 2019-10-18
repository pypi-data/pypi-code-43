import shutil
import os

VISTOMS_NAME_TEMP = 'VISTOMS_Static.html'
VISTOMS_TV_NAME_TEMP = 'VISTOMS_TreeViewer.html'

def copy(vistoms_destination, vistoms_version='Static'):
    """
    Function to copy a version of the visualization package to a new destination.

    :param vistoms_destination: name of the folder to put the visualization package
    :type vistoms_destination: basestring
    :param vistoms_version: version of the visualization package ('Static' or 'TreeViewer')
    :type vistoms_version: basestring
    :return: folder with visualization package
    :rtype: file
    """

    # Set directory and file name of the VISTOMS templates and static files
    vistoms_folder = 'templates'
    if vistoms_version == 'Static':
        vistoms_file = VISTOMS_NAME_TEMP
    elif vistoms_version == 'TreeViewer':
        vistoms_file = VISTOMS_TV_NAME_TEMP
    else:
        raise IOError('Invalid vistoms_version {} provided. Expected Static or TreeViewer.'.format(vistoms_version))
    static_folder = 'static'

    # Get path names
    src_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), vistoms_folder, vistoms_file)
    src_static = os.path.join(os.path.dirname(os.path.abspath(__file__)), static_folder)

    dst = os.path.abspath(vistoms_destination)

    # Remove destination directory and copy files
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src_static, os.path.join(dst, 'static'))
    shutil.copy2(src_html, os.path.join(dst, vistoms_file))

    return
