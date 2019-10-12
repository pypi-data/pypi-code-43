import firebase_admin
from firebase_admin import db
import platform
from datetime import datetime
import os


class ghsTools():

    def update_pulse(self, consecutive_number_of_runs, service_name):
        """Updates the pulse for this application
        Arguments:
            consecutive_number_of_runs {int} -- how many times the application has ran in a row
            service_name {str} -- name of the service
        Returns:
            dict -- what the pulse was set as in the database
        """
        current_time = str(datetime.now())
        ref = db.reference("db-info/pulses/" + service_name)
        if "linux" in str(platform.platform()).lower():
            ip_command = str(os.popen("hostname -I").read())
            ip = ip_command.split(" ")[0]
        else:
            ip = ""
        ref_set = {
            "Pulse-Time": current_time,
            "Pulse-Amount-(Consecutive)": consecutive_number_of_runs,
            "Pulse-Node": str(platform.uname().node),
            "Pulse-OS": str(platform.platform()),
            "Pulse-Python-Version": str(platform.python_version()),
            "Pulse-IP": ip
        }
        ref.set(ref_set)
        return ref_set

    def set_monitoring_info(self, email_notifications, pulse_time_diff_secs, service_name):
        """Updates the monitoring section for this micro service
        Arguments:
            email_notifications {bool} -- if the user should get email notifications
            pulse_time_diff_secs {int} -- amount of seconds between each pulse (exact)
            service_name {str} -- name of the service
        """
        ref = db.reference("db-info/monitoring/" + service_name)
        ref_set = {
            "email-notification": email_notifications,
            "pulse-time-diffs-(secs)": pulse_time_diff_secs + 300,
            "pulse-time-diffs-exact-(secs)": pulse_time_diff_secs
        }
        ref.set(ref_set)
        return ref_set
