import os
import glob
from xml.etree import cElementTree as ET
from mcutk.apps.projectbase import ProjectBase


class Project(ProjectBase):
    """
    KDS project object

    This class could parser the settings in .cproject and .project.
    Parameters:
        prjpath: path of .project

    """

    PROJECT_EXTENSION = '.project'

    def __init__(self, prjpath, *args, **kwargs):
        super(Project, self).__init__(prjpath, *args, **kwargs)
        try:
            self.cprjpath = glob.glob(self.prjdir + "/.cproject")[0]
        except Exception:
            raise IOError(".cproject file not found!")

        self._confs = self._get_all_configuration()
        self._targets = self._confs.keys()




    @property
    def name(self):
        """Return the application name

        Returns:
            string --- app name
        """
        xml_root = ET.parse(self.prjpath).getroot()
        app_name = xml_root.find('./name').text.strip()

        return app_name



    def _get_all_configuration(self):
        """read all configuration from .cproject file

        Raises:
            IOError -- if .cproject is not exists, it will raise an IOError.

        Returns:
            dict -- targets configuration
        """
        targets = {}

        xml_root = ET.parse(self.cprjpath).getroot()

        for per_node in xml_root.findall('.//configuration[@buildArtefactType="org.eclipse.cdt.build.core.buildArtefactType.exe"]'):
            target_name = per_node.attrib.get('name').strip()
            output_dir  = target_name
            output_name = self.name + '.' +  per_node.attrib.get('artifactExtension').strip()
            targets[target_name] = (output_dir, output_name)
        return targets



