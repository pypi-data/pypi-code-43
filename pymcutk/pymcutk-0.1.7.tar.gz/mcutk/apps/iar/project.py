import os
import glob
from xml.etree import cElementTree as ET

from mcutk.exceptions import ProjectNotFound
from mcutk.apps.projectbase import ProjectBase


class Project(ProjectBase):
    """
    IAR project object

    This class could parser the settings in *.ewp & *.eww.
    """
    PROJECT_EXTENSION = '.ewp'

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        try:
            ewpfile = glob.glob(os.path.join(self.prjdir, "*.ewp").replace("\\", "/"))[0]
            ewwfile = glob.glob(os.path.join(self.prjdir, "*.eww").replace("\\", "/"))[0]
            self.ewp_file = ewpfile
            self.ewp_xml = ET.parse(ewpfile)
        except IndexError:
            raise ProjectNotFound("Could not found IAR project '.ewp'")

        self.eww_file = ewwfile
        self._name = os.path.basename(self.ewp_file).split('.')[0]
        self._conf = self._get_all_configuration()
        self._targets = self._conf.keys()



    def _get_all_configuration(self):
        """Read all configuration from *.ewp file

        Raises:
            IOError -- if *.ewp is not exists, it will raise an IOError.

        Returns:
            dict -- targets configuration
        """
        targets = dict()

        for conf in self.ewp_xml.findall("configuration"):
            output_file = None
            target_name = conf.find("name").text.strip()
            # executable or library, 0: executable, 1: library
            output_type = conf.find("./settings[name='General']/data/option[name='GOutputBinary']/state")\
                                .text.strip()
            if output_type == "0":
                output_dir = conf.find("./settings[name='General']/data/option[name='ExePath']/state")\
                                    .text.strip()
                filename = conf.find("./settings[name='ILINK']/data/option[name='IlinkOutputFile']/state")\
                                    .text.strip()
                output_file = output_dir + '/' + filename
            else:
                output_file = conf.find("./settings[name='IARCHIVE']/data/option[name='IarchiveOutput']/state")\
                                    .text.strip()

            if "$PROJ_FNAME$" in output_file:
                output_file = output_file.replace("$PROJ_FNAME$", self._name)

            if "$PROJ_DIR$" in output_file:
                output_file = output_file.replace("$PROJ_DIR$/", "")

            targets[target_name] = output_file

        return targets


    def get_deps(self):
        """Get project dependecies.

        Return a list of project directory.
        """
        deps = list()
        nodes = self.ewp_xml.findall("configuration/settings[name='ILINK']/data/option[name='IlinkRawBinaryFile']/state")
        for node in nodes:
            if node is not None and node.text:
                p = node.text.strip().replace("$PROJ_DIR$", self.prjdir)
                path = os.path.abspath(p)
                deps.append(path)
        return deps




    @property
    def name(self):
        """Return the application name

        Returns:
            string --- app name
        """
        return self._name


