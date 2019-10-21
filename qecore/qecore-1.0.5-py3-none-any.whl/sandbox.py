#!/usr/bin/env python3
import os
import re
import base64
from time import strftime, sleep, localtime
from subprocess import Popen
from dogtail.tree import root
from dogtail.utils import config
from dogtail.rawinput import keyCombo
from qecore import run, QE_LOGGER
from qecore.application import Application
from qecore.time_limit import Timeout, QETimeoutError


class TestSandbox:
    def __init__(self, component, logging=False):
        """
        Initiate TestSandbox instance.

        @param component : str
            Testing component name.
        @param logging : bool
            Turn on or off logging of this submodule.
            Default option is False.
            Mostly used if submodule encounters a corner case that was not caught in implementation.
        """

        self.logging = logging

        if self.logging:
            QE_LOGGER.info(f"__init__(self, component={component}, logging={str(self.logging)})")

        self.component = component
        self.current_scenario = None
        self.background_color = None

        self.logging_start = None
        self.screenshot_run_result = None

        self.record_video = True
        self.record_video_pid = None

        self.attach_video = True
        self.attach_video_on_pass = False

        self.attach_journal = True
        self.attach_journal_on_pass = False

        self.attach_screenshot = True
        self.failed_test = False

        self.attach_faf = True
        self.attach_faf_on_pass = False

        self.workspace_return = False

        self.set_keyring = True

        self.wait_for_stable_video = True

        self.production = True

        self.applications = []
        self.default_application = None
        self.retrieve_session_data()
        self.wait_until_shell_becomes_responsive()

        self.shell = root.application("gnome-shell")


    def before_scenario(self, context, scenario):
        """
        Actions that are to be executed before every scenario.

        @param context : <context_object>
            Pass this object from environment file.
        @param scenario : <behave_object>
            Pass this object from environment file.
        """

        if self.logging:
            QE_LOGGER.info(f"before_scenario(self, context, scenario) test: {scenario.tags[-1]}")

        self.failed_test = False

        self.current_scenario = scenario.tags[0]
        self.set_log_start_time()
        self.overview_action("hide")
        self.set_typing_delay(0.2)
        self.set_debug_to_stdout_as(False)
        self.close_yelp()
        self.close_initial_setup()
        self.copy_data_folder()
        self.set_blank_screen_to_never()

        self.set_up_embedding(context)

        if self.record_video and self.production:
            self.start_recording()

        self.detect_keyring()
        self.return_to_home_workspace()


    def after_scenario(self, context, scenario):
        """
        Actions that are to be executed after every scenario.

        @param context : <context_object>
            Pass this object from environment file.
        @param scenario : <behave_object>
            Pass this object from environment file.
        """

        if self.logging:
            QE_LOGGER.info(f"after_scenario(self, context, scenario) test: {scenario.tags[0]}")

        if scenario.status == "failed":
            self.failed_test = True

        if self.attach_screenshot and self.failed_test:
            self.capture_image()

        if self.record_video:
            self.stop_recording()

        self.overview_action("hide")

        for application in self.applications:
            application.kill_application()

        if self.attach_screenshot and self.failed_test:
            self.attach_screenshot_to_report(context)

        if self.attach_journal and (self.failed_test or self.attach_journal_on_pass):
            self.attach_journal_to_report(context)

        if self.attach_video and (self.failed_test or self.attach_video_on_pass):
            self.attach_video_to_report(context)

        if self.attach_faf and (self.failed_test or self.attach_faf_on_pass):
            self.attach_abrt_link_to_report(context)


    def start_recording(self):
        """
        Start recording video.
        """

        if self.logging:
            QE_LOGGER.info("start_recording(self)")

        self.display_clock_seconds()
        self.set_max_video_length_to(600)

        record_video_process = Popen("qecore_start_recording", shell=True)
        self.record_video_pid = record_video_process.pid


    def stop_recording(self):
        """
        Stop recording video.
        """

        if self.logging:
            QE_LOGGER.info("stop_recording(self)")

        if self.record_video_pid is not None:
            run(f"sudo kill -9 {self.record_video_pid} > /dev/null")

        self.record_video_pid = None


    def get_app(self, name, a11yAppName=None, desktopFileExists=True,
                desktopFileName=None, appProcessName=None):
        """
        Return application to be used in test.

        @param name : str
            Name of application.
        @param a11yAppName : str
            Name of application in a11y tree.
        @param desktopFileExists : bool
            Does desktop file of application exist.
        @param desktopFileName : str
            Name of desktop file of application.
        @param appProcessName : str
            Name of process after application starts.
        """

        if self.logging:
            QE_LOGGER.info("".join((
                f"get_app(self, name={name}, a11yAppName={a11yAppName}, ",
                f"desktopFileExists={desktopFileExists}, desktopFileName={desktopFileName})"
            )))

        new_application = Application(name, a11yAppName, desktopFileExists,
                                      desktopFileName, appProcessName,
                                      self.shell, self.session_type,
                                      self.session_desktop, self.logging)

        self.applications.append(new_application)
        self.default_application = new_application \
            if self.default_application is None else self.default_application

        return new_application


    def wait_until_shell_becomes_responsive(self):
        """
        Give some time if shell is not yet loaded fully.
        """

        if self.logging:
            QE_LOGGER.info("wait_until_shell_becomes_responsive(self)")

        if self.session_type == "x11":
            with Timeout(30):
                while not "gnome-shell" in [x.name for x in root.applications()]:
                    sleep(0.5)
        else:
            sleep(1) # in wayland there is no way to make sure the session is loaded, so just sleep


    def retrieve_session_data(self):
        """
        Get session type/desktop data.
        """

        if self.logging:
            QE_LOGGER.info("retrieve_session_data(self)")

        self.architecture = run("uname -m").strip("\n")

        # Distributions expected for now: self.distribution = ["Red Hat Enterprise Linux", "Fedora"]
        self.distribution = run("cat /etc/os-release | grep ^NAME=")
        self.distribution = self.distribution.split("=")[-1].strip("\n").strip("\"")

        try:
            self.resolution = [int(x) for x in \
                re.findall(r"\d+x\d+", run("xrandr | grep '*'"))[0].split("x")]
        except Exception as error:
            self.resolution = f"The resolution retrieval failed for: {error}"

        self.session_desktop = run("echo $XDG_SESSION_DESKTOP").strip('\n')
        self.session_type = "x11"
        if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
            self.session_type = "wayland"


    def set_up_embedding(self, context):
        def embed_data(mime_type, data, caption):
            for formatter in context._runner.formatters:
                if "html" in formatter.name:
                    self._embed_to = formatter

            if hasattr(self, "_embed_to"):
                self._embed_to.embedding(mime_type=mime_type, data=data, caption=caption)
            else:
                return None

        context.embed = embed_data


    def set_log_start_time(self):
        """
        Save time. Will be used to retrieve logs from journal.
        """

        if self.logging:
            QE_LOGGER.info("set_log_start_time(self)")

        self.logging_start = strftime("%Y-%m-%d %H:%M:%S", localtime())


    def close_yelp(self):
        """
        Close yelp application that is opened after fresh installation.
        """

        if self.logging:
            QE_LOGGER.info("close_yelp(self)")

        help_process_id = run("pgrep yelp").strip("\n")
        if help_process_id.isdigit():
            run(f"kill -9 {help_process_id}")


    def close_initial_setup(self):
        """
        Close initial setup window that is opened after first login.
        """

        if self.logging:
            QE_LOGGER.info("close_initial_setup(self)")

        run("echo yes > ~/.config/gnome-initial-setup-done")


    def set_blank_screen_to_never(self):
        """
        Set blank screen to never. For longer tests it is undesirable for screen to lock.
        """

        if self.logging:
            QE_LOGGER.info("set_blank_screen_to_never(self)")

        run("gsettings set org.gnome.desktop.session idle-delay 0")


    def set_max_video_length_to(self, number=600):
        """
        Set maximum allowed video lenght.

        @param number : int
            Maximum video lenght.
        """

        if self.logging:
            QE_LOGGER.info(f"set_max_video_length_to(self, number={number})")

        run(" ".join((
            f"gsettings set",
            f"org.gnome.settings-daemon.plugins.media-keys",
            f"max-screencast-length {number}"
        )))


    def display_clock_seconds(self):
        """
        Display clock seconds for better tracking test in video.
        """

        if self.logging:
            QE_LOGGER.info("display_clock_seconds(self)")

        run("gsettings set org.gnome.desktop.interface clock-show-seconds true")


    def return_to_home_workspace(self):
        """
        Return to home workspace.
        """

        if self.logging:
            QE_LOGGER.info("return_to_home_workspace(self)")

        if not self.workspace_return:
            return

        keyCombo("<Super><Home>")


    def set_typing_delay(self, number):
        """
        Set typing delay so slower machines will not lose characters on type.

        @param number : int
            Time in between accepted key strokes.
        """

        if self.logging:
            QE_LOGGER.info(f"set_typing_delay(self, number={number})")

        config.typingDelay = number


    def set_debug_to_stdout_as(self, true_or_false=False):
        """
        Set debugging to stdout.

        @param true_or_false : bool
            Decision if debug to stdout or not.
        """

        if self.logging:
            QE_LOGGER.info(f"set_debug_to_stdout_as(self, true_or_false={true_or_false})")

        config.logDebugToStdOut = true_or_false


    def copy_data_folder(self):
        """
        Copy /data folder to /tmp/.
        """

        if self.logging:
            QE_LOGGER.info("copy_data_folder(self)")

        if os.path.isdir("data/"):
            for single_file in os.listdir("data/"):
                run(f"cp data/{single_file} /tmp/{single_file}")


    def detect_keyring(self):
        """
        Detect if keyring was setup. If not, setup the keyring with empty password.

        @param context : <context_object>
            Passed object.
        """

        if self.logging:
            QE_LOGGER.info("detect_keyring(self)")

        if not self.set_keyring:
            return

        current_user = os.path.expanduser("~")
        is_keyring_set = os.path.isfile("/tmp/keyring_set")
        is_keyring_in_place = os.path.isfile(f"{current_user}/.local/share/keyrings/default")

        if not is_keyring_set or not is_keyring_in_place:
            run(f"sudo rm -rf {current_user}/.local/share/keyrings/*")

            create_keyring_process = Popen("qecore_start_keyring", shell=True)
            self.keyring_process_pid = create_keyring_process.pid

            self.shell.child("Continue").click()
            self.shell.child("Continue").click()

            run(f"touch /tmp/keyring_set")

        run("killall qecore_start_keying")


    def capture_image(self):
        """
        Capture screenshot after failed step.
        """

        if self.logging:
            QE_LOGGER.info("capture_image(self)")

        if not self.production:
            return

        self.screenshot_run_result = run("gnome-screenshot -f /tmp/screenshot.png", verbose=True)


    def attach_screenshot_to_report(self, context):
        """
        Attach screenshot to report upon failed test.

        @param context : <context_object>
            Passed object.
        """

        if self.logging:
            QE_LOGGER.info("attach_screenshot_to_report(self, context)")

        if not self.production:
            return

        if self.screenshot_run_result[1] != 0:
            context.embed(mime_type="text/plain",
                          data=f"Screenshot capture failed: \n{self.screenshot_run_result}\n",
                          caption="Screenshot")
        else:
            data_base64 = base64.b64encode(open("/tmp/screenshot.png", "rb").read())
            data_encoded = data_base64.decode("utf-8").replace("\n", "")
            context.embed(mime_type="image/png",
                          data=data_encoded,
                          caption="Screenshot")


    def attach_image_to_report(self, context, image=None, caption="DefaultCaption"):
        """
        Attach image to report upon user request.

        @param context : <context_object>
            Passed object.
        @param image : str
            Location of image/png file.
        @param caption : str
            Caption that is to be displayed in test report.
        """

        if self.logging:
            QE_LOGGER.info("attach_image_to_report(self, context)")

        if not self.production:
            return

        if os.path.isfile(image):
            data_base64 = base64.b64encode(open(image, "rb").read())
            data_encoded = data_base64.decode("utf-8").replace("\n", "")
            context.embed(mime_type="image/png",
                          data=data_encoded,
                          caption=caption)


    def attach_video_to_report(self, context):
        """
        Attach video to report upon failed test.

        @param context : <context_object>
            Passed object.
        """

        if self.logging:
            QE_LOGGER.info("attach_video_to_report(self, context)")

        if not (self.production and self.record_video):
            return

        absolute_path_to_video = os.path.expanduser("~/Videos")
        screencast_list = [f"{absolute_path_to_video}/{file_name}" for file_name in \
            os.listdir(absolute_path_to_video) if "Screencast" in file_name]

        video_name = f"{self.component}_{self.current_scenario}"
        absolute_path_to_new_video = f"{absolute_path_to_video}/{video_name}.webm"

        if screencast_list == []:
            context.embed(mime_type="text/plain",
                          data="No video file found.",
                          caption="Video")
        else:
            if self.wait_for_stable_video:
                self.wait_for_video_encoding(screencast_list[0])

            data_base64 = base64.b64encode(open(screencast_list[0], "rb").read())
            data_encoded = data_base64.decode("utf-8").replace("\n", "")
            context.embed(mime_type="video/webm",
                          data=data_encoded,
                          caption="Video")
            run(f"mv {screencast_list[0]} {absolute_path_to_new_video}")
            run(f"sudo rm -rf {absolute_path_to_video}/Screencast*")


    def attach_journal_to_report(self, context):
        """
        Attach journal to report upon failed test.

        @param context : <context_object>
            Passed object.
        """

        if self.logging:
            QE_LOGGER.info("attach_journal_to_report(self, context)")

        if not self.production:
            return

        journal_run = run(" ".join((
            f"sudo journalctl",
            f"--all",
            f"--output=short-precise",
            f"--since='{self.logging_start}'"
            f"> /tmp/journalctl_short.log"
        )), verbose=True)

        if journal_run[1] != 0:
            context.embed(mime_type="text/plain",
                          data=f"Creation of journalctl file failed: \n{journal_run}\n",
                          caption="journalctl")
        else:
            context.embed(mime_type="text/plain",
                          data=open("/tmp/journalctl_short.log", "r").read(),
                          caption="journalctl")
            
        run("rm /tmp/journalctl_short.log")


    def attach_abrt_link_to_report(self, context):
        """
        Attach abrt link to report upon detected abrt FAF report.

        @param context : <context_object>
            Passed object.
        """

        if self.logging:
            QE_LOGGER.info("attach_abrt_link_to_report(self, context)")

        if not self.production:
            return

        faf_reports = set()
        abrt_directories = run("sudo ls /var/spool/abrt/ | grep ccpp-").strip("\n").split("\n")

        for abrt_directory in abrt_directories:
            try:
                reason_file = f"/var/spool/abrt/{abrt_directory}/reason"
                reported_to_file = f"/var/spool/abrt/{abrt_directory}/reported_to"

                abrt_faf_reason_run = run(f"sudo cat '{reason_file}'", verbose=True)
                abrt_faf_hyperlink_run = run(f"sudo cat '{reported_to_file}'", verbose=True)

                if abrt_faf_reason_run[1] == 0 and abrt_faf_hyperlink_run[1] == 0:
                    abrt_faf_reason = abrt_faf_reason_run[0].strip("\n")
                    abrt_faf_hyperlink = abrt_faf_hyperlink_run[0].split("ABRT Server: URL=")[-1].split("\n")[0]

                    faf_reports.add((abrt_faf_hyperlink, f"Reason: {abrt_faf_reason}"))

            except Exception as error:
                print(f"Exception caught: {error}")
                continue

        if faf_reports:
            context.embed("link", faf_reports, caption="FAF reports")


    def wait_for_video_encoding(self, file_name):
        """
        Wait until the video is fully encoded.
        This is verified by videos changing size.
        Once the file is encoded the size will not change anymore.

        @param file_name : str
            Video location for size verification.
        """

        if self.logging:
            QE_LOGGER.info(f"wait_for_video_encoding(self, file_name={file_name})")

        current_size = 0
        current_stability = 0

        try:
            with Timeout(15):
                while current_stability < 50:
                    new_size = os.path.getsize(file_name)
                    if current_size == new_size:
                        current_stability += 1
                    else:
                        current_stability = 0
                    current_size = new_size
                    sleep(0.1)

        except QETimeoutError:
            QE_LOGGER.info("Timeout reached while waiting for video encoding. Resuming embedding.")


    def set_background(self, color=None, background_image=None):
        """
        Change background to single color. Currently support for white/black/image.

        @param color : str
            String black/white to set as background color.
        @param background_image : str
            Image location to be set as background.
        """

        if self.logging:
            QE_LOGGER.info("".join((
                f"set_background(self, color={color}, ",
                f"background_image={background_image})."
            )))

        if background_image:
            run(f"gsettings set org.gnome.desktop.background picture-uri file://{background_image}")
        elif color == "white":
            run("gsettings set org.gnome.desktop.background picture-uri file://")
            run("gsettings set org.gnome.desktop.background primary-color \"#FFFFFF\"")
            run("gsettings set org.gnome.desktop.background secondary-color \"#FFFFFF\"")
            run("gsettings set org.gnome.desktop.background color-shading-type \"solid\"")
        elif color == "black":
            run("gsettings set org.gnome.desktop.background picture-uri file://")
            run("gsettings set org.gnome.desktop.background primary-color \"#000000\"")
            run("gsettings set org.gnome.desktop.background secondary-color \"#000000\"")
            run("gsettings set org.gnome.desktop.background color-shading-type \"solid\"")
        else:
            QE_LOGGER.info(" ".join((
                f"Color '{color}' is not defined.",
                f"You can define one yourself and submit merge request or"
                f"email modehnal@redhat.com for support."
            )))


    def overview_action(self, action="hide"):
        """
        Hide or show application overview.

        @param action : str
            Hide or show application overview.
        """

        if self.logging:
            QE_LOGGER.info(f"overview_action(self, action={action})")

        if action == "hide":
            run(" ".join((
                "dbus-send",
                "--session",
                "--type=method_call",
                "--dest=org.gnome.Shell",
                "/org/gnome/Shell",
                "org.gnome.Shell.Eval",
                "string:'Main.overview.hide();'"
            )))
        elif action == "show":
            run(" ".join((
                "dbus-send",
                "--session",
                "--type=method_call",
                "--dest=org.gnome.Shell",
                "/org/gnome/Shell",
                "org.gnome.Shell.FocusSearch"
            )))
        else:
            assert False, "Unknown option"
