#!/usr/bin/env python3
from time import sleep
import shlex
import configparser
from subprocess import Popen, PIPE
from dogtail.rawinput import typeText, pressKey, keyCombo
from dogtail.tree import root
from qecore import run, QE_LOGGER
from qecore.time_limit import Timeout


class Application:
    def __init__(self, component, a11yAppName=None, desktopFileExists=True,
                 desktopFileName=None, appProcessName=None, shell=None,
                 session_type=None, session_desktop=None, logging=False):
        """
        Initiate Application instance.

        @param component : str
            Application name.
        @param a11yAppName : str
            Name of application as it appears in accessibility tree.
        @param desktopFileExists : bool
            States that desktop file of given application exists or not.
        @param desktopFileName : str
            Name of desktop file if the name is different from application name.
        @param appProcessName : str
            Name process of application if the name of is different from application name.
        @param logging : bool
            Turn on logging of this submodule. Passed from sandbox.
        """

        self.logging = logging

        if self.logging:
            QE_LOGGER.info(" ".join((
                f"__init__(self, component={component}, a11yAppName={a11yAppName}",
                f"desktopFileExists={desktopFileExists}, desktopFileName={desktopFileName}",
                f"appProcessName={appProcessName}, shell='expecting_passed_shell'",
                f"session_type={session_type}, session_desktop={session_desktop}",
                f"logging={str(logging)}"
            )))

        self.shell = shell
        self.session_type = session_type
        self.session_desktop = session_desktop
        self.pid = None
        self.instance = None
        self.component = component
        self.a11y_app_name = a11yAppName if a11yAppName else component
        self.desktop_file_exists = desktopFileExists
        self.exit_shortcut = "<Control_L><Q>"
        self.kill = True
        self.kill_command = None
        self.desktop_file_name = desktopFileName if desktopFileName else ""
        self.app_process_name = appProcessName if appProcessName else component
        self.get_desktop_file_data()


    def get_desktop_file_data(self):
        """
        Parse desktop file.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} get_desktop_file_data(self)")

        if self.desktop_file_exists: # zenity/gnome-shell do not have desktop file
            desktop_run = run(" ".join((
                f"rpm -qlf $(which {self.component}) |",
                f"grep /usr/share/applications/ |",
                f"grep .desktop |",
                f"grep '{self.desktop_file_name}'"
            )), verbose=True)


            if desktop_run[1] != 0:
                raise Exception(f"Desktop file of application '{self.component}' was not found.")

            desktop_file = desktop_run[0].strip("\n")
            desktop_file_config = configparser.RawConfigParser()
            desktop_file_config.read(desktop_file)

            self.name = desktop_file_config.get("Desktop Entry", "name")
            self.exec = desktop_file_config.get("Desktop Entry", "exec").split(" ")[0]


    def start_via_command(self, command=None, in_session=False, kill=True):
        """
        Start application via command.

        @param command : str
            Complete command that is to be used to start application.
        @param in_session : bool
            Start application via command in session. TODO.
        @param kill : bool
            If application is running while command is run. Application will be killed.
        """

        if self.logging:
            QE_LOGGER.info("".join((
                f"{self.component} ",
                f"start_via_command(self, command={command}, in_session={in_session}, kill={kill})"
            )))

        if self.is_running() and kill:
            self.kill_application()

        if in_session:
            pressKey("Esc")
            keyCombo("<Alt><F2>")
            sleep(0.5)
            keyCombo("<Alt><F2>")
            sleep(0.5)
            enter_a_command = self.shell.findChild(lambda x: "activate" in x.actions and x.showing)
            enter_a_command.text = command if command else self.exec
            sleep(0.5)
            pressKey("Enter")
        else:
            self.process = Popen(shlex.split(command if command else self.exec),\
                 stdout=PIPE, stderr=PIPE)

        self.wait_before_app_starts(30)
        self.instance = self.get_root()


    def start_via_menu(self, kill=True):
        """
        Start application via command.

        @param kill : bool
            If application is running while start_via_menu is called. Application will be killed.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} start_via_menu(self, kill={kill})")

        gnome_version_present = run("rpm -q gnome-shell").strip("\n")
        if ("classic" in self.session_desktop) and ("3.32" in gnome_version_present):
            assert False, f"Application cannot be started via menu in {gnome_version_present}."

        if not self.desktop_file_exists:
            raise Exception("".join((
                f"Testing target '{self.a11y_app_name}' does not have desktop file. ",
                f"Indication of user failure!"
            )))

        if self.is_running() and kill:
            self.kill_application()

        run(" ".join((
            "dbus-send",
            "--session",
            "--type=method_call",
            "--dest=org.gnome.Shell",
            "/org/gnome/Shell",
            "org.gnome.Shell.FocusSearch"
        )))

        sleep(1)
        typeText(self.name)
        pressKey("Enter")

        self.wait_before_app_starts(30)
        self.instance = self.get_root()


    def close_via_shortcut(self):
        """
        Start application via shortcut.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} close_via_shortcut(self)")

        if not self.is_running():
            raise Exception("".join((
                f"Application '{self.a11y_app_name}' is no longer running. ",
                f"Indication of test failure!"
            )))

        keyCombo(self.exit_shortcut)

        self.wait_before_app_closes(30)
        self.instance = None


    def already_running(self):
        """
        If application is started by other means other than this submodule,
        this will initiate data that are necessary.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} already_running(self)")

        self.wait_before_app_starts(15)
        self.instance = self.get_root()


    def get_root(self):
        """
        Get accessibility root of appllication.

        @return : <accessibility_object>
            Return root object of application.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} get_root(self) search by '{self.a11y_app_name}'")

        return root.application(self.a11y_app_name)


    def is_running(self):
        """
        Get accessibility root of appllication.

        @return : bool
            Return state of application. Running or not.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} is_running(self)")
        try:
            for _ in range(3):
                is_running = self.a11y_app_name in [x.name for x in root.applications()]
                if is_running:
                    break
            return is_running
        except Exception:
            return False


    def get_pid_list(self):
        """
        Get list of processes of running application.

        @return : str
            Return all running processes of application, seperated by new line character,
            not converting to list. Return nothing if application is not running.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} get_pid_list(self)")

        if self.is_running():
            return run(f"pgrep -fla {self.app_process_name}").strip("\n")

        return None


    def get_all_kill_candidates(self):
        """
        Take result of get_pid_list and return only processes of application.
        If kill candidate happens to have ['runtest', 'behave', 'dogtail', '/usr/bin/gnome-shell']
        in its process name. Process will not be killed.
        This prevents testname colliding with found process so we will not kill the test itself.

        @return : list
            Return all processed id of applications.
            Return empty list if no satisfactory process was found.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} get_all_kill_candidates(self)")

        application_pid_string = self.get_pid_list()
        if application_pid_string:
            application_pid_list = application_pid_string.split("\n")
        else:
            return []

        final_pid_list = []
        for process in application_pid_list:
            if not (("runtest" in process) or \
                    ("behave" in process) or \
                    ("dogtail" in process) or \
                    (process == "/usr/bin/gnome-shell")):
                extracted_pid = process.split(" ", 1)[0]
                try:
                    final_pid_list.append(int(extracted_pid))
                except ValueError:
                    pass # skip non-digits
        return final_pid_list


    def kill_application(self):
        """
        Kill application.
        """

        if self.logging:
            QE_LOGGER.info(f"{self.component} kill(self)")

        if self.is_running() and self.kill:
            if not self.kill_command:
                for pid in self.get_all_kill_candidates():
                    run(f"sudo kill -9 {pid} > /dev/null")
            else:
                run(self.kill_command)


    # Following two could be merged, I could not think of a nice way of doing it though.
    def wait_before_app_starts(self, time_limit):
        """
        Wait before application starts.

        @param time_limit : int
            Number which signifies time before the run is stopped.
        """

        if self.logging:
            QE_LOGGER.info("".join((
                f"{self.component} ",
                f"wait_before_app_starts(self, time_limit={time_limit})"
            )))

        with Timeout(time_limit):
            try:
                while not self.is_running():
                    sleep(0.1)
            except Exception:
                assert False, "".join((
                    f"Application '{self.a11y_app_name}' is not running. ",
                    f"Indication of test failure!"
                ))

    def wait_before_app_closes(self, time_limit):
        """
        Wait before application stops.

        @param time_limit : int
            Number which signifies time before the run is stopped.
        """

        if self.logging:
            QE_LOGGER.info("".join((
                f"{self.component} ",
                f"wait_before_app_closes(self, time_limit={time_limit}"
            )))

        with Timeout(time_limit):
            try:
                while self.is_running():
                    sleep(0.1)
            except Exception:
                assert False, "".join((
                    f"Application '{self.a11y_app_name}' is running. ",
                    f"Indication of test failure!"
                ))
