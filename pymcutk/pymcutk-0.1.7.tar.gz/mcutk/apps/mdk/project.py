import os
import re
import glob
import logging

from xml.etree import cElementTree as ET
from mcutk.apps.projectbase import ProjectBase
from mcutk.exceptions import ProjectNotFound



class Project(ProjectBase):
    """
    MDK uvsion project object

    This class could parser the settings in *.uvprojx.
    """

    PROJECT_EXTENSION = '.uvprojx'

    OPTIONS_ROOT = 'Targets/Target/TargetOption/'


    BUILD_OPTIONS = {
        'TargetCommonOption/CreateHexFile': '1',
        'TargetCommonOption/BrowseInformation': '0',
        # 'TargetCommonOption/DebugInformation': '0',
        # 'TargetCommonOption/CreateLib': '0',
    }


    DEBUGGERS = {
    'cmsis-dap': {
            'DebugOption/TargetDlls/Driver': 'BIN\\CMSIS_AGDI.dll',
            'Utilities/Flash2': 'BIN\\CMSIS_AGDI.dll',
        },
    'j-link':{
            'DebugOption/TargetDlls/Driver': 'Segger\\JL2CM3.dll',
            'Utilities/Flash2': 'Segger\\JL2CM3.dll',
        }
    }




    DEBUGGING_OPTIONS = {
        'Utilities/Flash1/UpdateFlashBeforeDebugging' : '0',
        'DebugOption/Target/RestoreBreakpoints': '0',
        'DebugOption/Target/RestoreWatchpoints': '0',
        'DebugOption/Target/RestoreMemoryDisplay': '0',
        'DebugOption/Target/RestoreFunctions': '0',
        'DebugOption/Target/RestoreToolbox': '0',
        'DebugOption/Target/RestoreTracepoints': '0',
        'DebugOption/Target/RestoreSysVw': '0',
    }



    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        try:
            if not self.prjpath.endswith(".uvprojx"):
                logging.warning("%s: is not a project file", self.prjpath)
                dirname = os.path.dirname(args[0])
                prjpath = glob.glob(dirname + "/*.uvprojx")[0]
                logging.warning("we have automaticly loaded the file to replace: %s", prjpath)
                self.prjpath = prjpath
        except IndexError:
            raise ProjectNotFound("Not found the project file .uvprojx under project parent directory!")
        # .uvprojx
        self.prjpath = self.prjpath.replace('\\', '/')
        # .uvoptx
        self.prjuvoptx = self.prjpath.replace('.uvprojx', '.uvoptx')
        self._prjxmltree = ET.parse(self.prjpath)
        self._conf = self._configurations()
        self._targets = self._conf.keys()
        # simplify targets: remove project name
        self._simple_targets = [t.replace(self.name, '').strip() for t in self._targets]


    def _configurations(self):
        targets = dict()
        all_targets = self._prjxmltree.findall("Targets/Target")
        for target_node in all_targets:
            target_name = target_node.find("TargetName").text.strip()
            output_dir = target_node.find("TargetOption/TargetCommonOption/OutputDirectory").text.strip()
            output_name = target_node.find("TargetOption/TargetCommonOption/OutputName").text.strip()
            targets[target_name] = output_dir + output_name
        return targets



    def to_dict(self):
        # use simple targets
        return {
            'toolchain': self.idename,
            'targets': self._simple_targets,
            'project': self.prjpath,
            'name': self.name
        }




    @property
    def targetsinfo(self):
        """Returns a dict about the targets data.

        Example:
        {
            "Debug":   "debug_output_dir/output_name",
            "Release": "release_output_dir/output_name",
        }
        """
        return self._conf


    @property
    def name(self):
        """Return the application name

        Returns:
            string --- app name
        """
        return os.path.basename(self.prjpath).split(".")[0]


    def _set_value(self, nodepath, value):
        """Update value for specific nodes."""
        for node in self._prjxmltree.findall(nodepath):
            node.text = value


    def get_flash_driver(self, target):
        nodepath = "./Targets/Target[TargetName='{}']/TargetOption/TargetCommonOption/FlashDriverDll".format(target)
        return self._prjxmltree.find(nodepath).text



    def update_inifile(self, target):
        """Append 'EXIT' command to initializationfile to make sure the debugging exit when flash
        finished. If InitializationFile is not configured, this will set a default file
        'debugging.ini'.
        """
        nodepath = "./Targets/Target[TargetName='{}']/TargetOption/DebugOption/TargetDlls/InitializationFile".format(target)
        root = os.path.dirname(self.prjpath)
        try:
            _update_inifile(self._prjxmltree, root, nodepath)
        except ValueError:
            pass



    def set_build_options(self):
        """Set options to control keil build behaviour.
        1. Disable browse information will speed up the build.
        2. Create hex file.
        """
        for path, value in self.BUILD_OPTIONS.items():
            self._set_value(self.OPTIONS_ROOT + path, value)
        self.save()


    def set_debugging_options(self, target, sn='', debugger_type='cmsis-dap', debugfile=None, action='program'):
        """Set debugging options to enable the automated flash programming by keil.

        Arguments:
            debugger_type -- {str} -- debugger type, avalibe choices are
                'cmsis-dap', 'j-link', default is 'cmsis-dap'.
            action: 'program' or 'erase'
        """
        if not os.path.exists(self.prjuvoptx):
            logging.warning('.uvoptx file is not exists, create new from template!!!!')
            Uvoptx.create_new_from_template(self.prjuvoptx, target)

        optx = Uvoptx(self.prjuvoptx)
        optx.set_debugger(target, debugger_type)
        optx.set_cmsis_serial_number(target, sn, action)
        inifile = optx.update_inifile(target)

        debug_mode = False
        is_to_flash = True

        # exclude xip ini file, which is required as external flash, not for RAM
        if 'flexspi_nor' in target or inifile == None or "xip" in inifile:
            debug_mode = False
            is_to_flash = True

        elif inifile != None:
            debug_mode = True
            is_to_flash = False


        optx.save()

        # check target
        # target = self.map_target(target)
        # update .uvprjx
        self.update_inifile(target)

        for path, value in Project.DEBUGGING_OPTIONS.items():
            if 'UpdateFlashBeforeDebugging' in path:
                value = '1' if is_to_flash else '0'
            self._set_value(self.OPTIONS_ROOT + path, value)

        # Force to update debugger
        for path, value in Project.DEBUGGERS[debugger_type].items():
            self._set_value(self.OPTIONS_ROOT + path, value)

        if debugfile:
            self._set_value(self.OPTIONS_ROOT + 'TargetCommonOption/OutputDirectory', os.path.dirname(debugfile) + '\\')
            self._set_value(self.OPTIONS_ROOT + 'TargetCommonOption/OutputName', os.path.basename(debugfile))

        self.save()
        return debug_mode





    def save(self):
        """Save changes"""
        self._prjxmltree.write(self.prjpath, xml_declaration=True, method='xml', encoding='UTF-8')







class Uvoptx(object):

    DEBUGGERS = {
        'cmsis-dap': 'BIN\\CMSIS_AGDI.dll',
        'j-link':'Segger\\JL2CM3.dll',
    }

    TEMPLATE = os.path.join(os.path.abspath(os.path.dirname(__file__)), \
        'templates/mdk.uvoptx')

    @classmethod
    def create_new_from_template(cls, uvoptx_path, target):
        tree = ET.parse(cls.TEMPLATE)
        tree.find('./Target/TargetName').text = target
        tree.write(uvoptx_path, xml_declaration=True, method='xml', encoding='UTF-8')


    def __init__(self, path):
        self.path = path
        self._xmltree = ET.parse(path)


    def set_debugger(self, target, debugger='cmsis-dap'):
        nodepath = "./Target[TargetName='{}']/TargetOption/DebugOpt/pMon".format(target)
        self._xmltree.find(nodepath).text = self.DEBUGGERS[debugger]



    def update_inifile(self, target):
        nodepath = "./Target[TargetName='{}']/TargetOption/DebugOpt/tIfile".format(target)
        root = os.path.dirname(self.path)
        return _update_inifile(self._xmltree, root, nodepath)


    def set_cmsis_serial_number(self, target, sn, action='program'):
        """Set CMSIS-DAPLINK serial number into .uvoptx.

        action: program/erase.
        """
        parent_path = "./Target[TargetName='{}']/TargetOption/TargetDriverDllRegistry".format(target)
        # get parent node
        parent_node = self._xmltree.find(parent_path)

        if parent_node is None:
            parent_node = ET.fromstring('<TargetDriverDllRegistry></TargetDriverDllRegistry>')
            self._xmltree.find("./Target[TargetName='{}']/TargetOption/".format(target)).append(parent_node)

        # flash_driver = flash_driver.replace('UL2CM3(', '').replace('.FLM))', '.FLM)')
        # get specfic node
        node = parent_node.find("./SetRegEntry[Key='CMSIS_AGDI']")
        if node is None:
            raise ValueError('Error: project debugger is not cmsis-dap!')
            # not exists, this will use default blocks
            # node = ET.fromstring(default_blocks)
            # parent_node.append(node)

        # update sn value
        driver = node.find('Name').text
        sn = sn[:32]
        snvalue = '-U{}'.format(sn)

        snp = re.compile(r'-U\w*')
        if snp.search(driver) is not None:
            driver = snp.sub(snvalue, driver)
        else:
            driver = snvalue + ' ' + driver # put the sn number at the beginning to avoid compatible issues


        # -FO1 means: erase flash
        # -FO15 means: program, verify, reset and run
        # if not do that the program will not run after flash download
        # -FO15 means: program, verify, reset and run
        # if not do that the program will not run after flash download
        # -F011 means: program, reset and run (without verify)
        # The Aruba Flash less requires this F011, and we will set F011 as default options since it's more stable
        if action == 'program':
            ac_value = ' -FO11 '
        elif action == 'erase':
            ac_value = ' -FO1 '
        flash_settings = re.compile(' -FO\d+ ')
        if flash_settings.search(driver) is not None:
            driver = flash_settings.sub(ac_value, driver)
        else:
            driver += ' -FO11 '
            logging.warning('flash setting not detected.')

        node.find('Name').text = driver
        logging.debug(node.find('Name').text)




    def save(self):
        self._xmltree.write(self.path, xml_declaration=True, method='xml', encoding='UTF-8')



def _update_inifile(tree, project_root, nodepath):
    # default_ini = os.path.join(os.path.abspath(os.path.dirname(__file__)), \
    #     'debugging.ini').replace('\\', '/')

    node = tree.find(nodepath)
    if node is None:
        logging.debug('Warning: The path "%s" is not exists!'%nodepath)
        return None

    # not conigured file, means it run in ram or sdram.
    if not node.text:
        return None
        #node.text = default_ini


    # configured but it maybe a relative path, further check
    elif not os.path.exists(node.text):
        inifile = os.path.join(project_root, node.text)
        if not os.path.exists(inifile):
            raise IOError('InitializationFile(%s) is not exists!'%inifile)

        with open(inifile, 'r') as file:
            content = file.read()

        # Append "EXIT" command to inifile
        if 'EXIT' not in content:
            with open(inifile, 'a+') as file:
                file.write('EXIT')

    logging.debug('InitializationFile: %s', node.text)
    return node.text
