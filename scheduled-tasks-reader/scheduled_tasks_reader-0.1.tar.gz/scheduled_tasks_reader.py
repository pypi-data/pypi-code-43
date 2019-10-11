#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse
import xmltodict
import pandas as pd
import re


class CLIHandler:
    def __init__(self):
        self.columns = [
            "task_path",
            "task_name",
            "enabled",
            "hidden",
            "triggers",
            "exec_command",
            "exec_args",
            "schedule_time",
        ]
        self.default_values_sort_by = ["task_path", "task_name"]
        self.trigger_choices = [
            "EventTrigger",
            "TimeTrigger",
            "LogonTrigger",
            "BootTrigger",
            "CalendarTrigger",
            "SessionStateChangeTrigger",
            "RegistrationTrigger",
        ]
        self.output_format_choices = ["html", "json", "csv"]
        self.default_value_output_format = "html"
        parser = self.init_argparser()
        self.args = parser.parse_args()
        self.check_if_path_is_dir()
        self.parsed_scheduled_task_output = self.parse_scheduled_task_output()
        self.show_output()
        if self.args.output:
            self.store_output()

    def init_argparser(self):
        parser = argparse.ArgumentParser(
            prog="Scheduled Tasks Reader",
            description="Get Overview of Scheduled Tasks from the relevant registry files.",
        )
        parser.add_argument("dir_of_registry_files", help="Path to the directory containing the relevant registry files")

        parser.add_argument(
            "-o", "--output", help="Store output at specified location. It will overwrite existing files!"
        )
        parser.add_argument(
            "-of",
            "--output_format",
            choices=self.output_format_choices,
            metavar="",
            default=self.default_value_output_format,
            help=f"Define output format. Default value is: {self.default_value_output_format}.Allowed values are: {self.output_format_choices}",
        )
        parser.add_argument(
            "-n",
            "--task_names",
            nargs="+",
            help="Filter for array of one or more names of scheduled task (separated by space).",
        )
        parser.add_argument(
            "-p",
            "--task_paths",
            nargs="+",
            help="Filter for array of one or more paths of scheduled task (separated by space).",
        )
        parser.add_argument(
            "-s",
            "--sort_by",
            nargs="+",
            choices=self.columns,
            metavar="",
            default=self.default_values_sort_by,
            help=f"Sort by array of one or more attributes of scheduled task (separated by space). Default values are: {self.default_values_sort_by}.Allowed values are: {self.columns}",
        )
        parser.add_argument(
            "-t",
            "--task_triggers",
            nargs="+",
            choices=self.trigger_choices,
            metavar="",
            help=f"Filter for array of one or more trigger types of scheduled task (separated by space). Allowed values are: {self.trigger_choices}",
        )
        parser.add_argument("--table_terminal_output", action="store_true", help="Show the output as a table, needs a wide Terminal.")
        parser.add_argument("--only_hidden", action="store_true", help="Show only the hidden scheduled tasks")
        parser.add_argument(
            "--raw_data",
            action="store_true",
            help="Append the raw data from the scheduled tasks parsed from the xmls to the normal output.",
        )
        parser.add_argument("--version", action="version", version="%(prog)s 0.1")
        return parser

    def check_if_path_is_dir(self):
        if not os.path.isdir(self.args.dir_of_registry_files):
            raise ValueError(f"'{self.args.dir_of_registry_files}' is not a valid path of a directory")

    def parse_scheduled_task_output(self):
        schedule_task_parser = ScheduledTaskParser(self.args.dir_of_registry_files)

        data_frame = pd.DataFrame(schedule_task_parser.scheduled_tasks)
        data_frame = data_frame.sort_values(by=self.args.sort_by)
        data_frame = self.filter_data_frame(data_frame)
        return data_frame

    def filter_data_frame(self, data_frame):
        if self.args.only_hidden:
            data_frame = data_frame[data_frame.hidden == True]
        if self.args.task_paths:
            data_frame = data_frame[data_frame.task_path.isin(self.args.task_paths)]
        if self.args.task_names:
            data_frame = data_frame[data_frame.task_name.isin(self.args.task_names)]
        if self.args.task_triggers:
            data_frame = data_frame[
                data_frame.triggers.apply(
                    lambda triggers: any(trigger in self.args.task_triggers for trigger in triggers)
                )
            ]

        if self.args.raw_data:
            data_frame = data_frame.join(pd.io.json.json_normalize(data_frame["task_data"]))
            del data_frame["task_data"]
        else:
            data_frame = data_frame[self.columns]
        return data_frame

    def show_output(self):
        pd.set_option("display.max_columns", None)
        pd.set_option("display.expand_frame_repr", False)
        pd.set_option("max_colwidth", -1)
        pd.set_option("colheader_justify", "left")

        if self.args.table_terminal_output:
            print(self.parsed_scheduled_task_output.to_string(index=False))
        else:
            for task in self.parsed_scheduled_task_output.iterrows():
                print(task[1].to_string())
                print("===========================")

    def store_output(self):
        output_format = self.args.output_format
        with open(self.args.output, "w") as output_file:
            if output_format == "html":
                this_directory = os.path.abspath(os.path.dirname(__file__))
                html_template_path = os.path.join(this_directory, "html_template.html")
                with open(html_template_path, "r", encoding="UTF-8") as html_template:
                    html_template_content = html_template.read()
                html_content = html_template_content.format(
                    data=self.parsed_scheduled_task_output.to_html(table_id="dataframe", index=False)
                )
                output_file.write(html_content)
            elif output_format == "json":
                output_file.write(self.parsed_scheduled_task_output.to_json())
            elif output_format == "csv":
                output_file.write(self.parsed_scheduled_task_output.to_csv())


class ScheduleTimeParser:
    def __init__(self, task_data, CalendarTrigger=True):

        self.attributes = {
            "schedule": None,
            "dayInterval": None,
            "daysOfWeek": None,
            "weeksInterval": None,
            "daysOfMonth": None,
            "months": None,
            "calenderTrigger": CalendarTrigger,
            "task_data": task_data,
            "executionLimit": None,
            "duration": None,
            "interval": None,
            "stopAtEnd": None,
        }

    def set_time_day(self, task_data):
        self.attributes["schedule"] = "ScheduleByDay"
        if "DaysInterval" in task_data:
            self.attributes["dayInterval"] = task_data["DaysInterval"]

    def set_time_week(self, task_data):
        self.attributes["schedule"] = "ScheduleByWeek"
        if "WeeksInterval" in task_data:
            self.attributes["weeksInterval"] = task_data["WeeksInterval"]
        if "DaysOfWeek" in task_data:
            self.attributes["daysOfWeek"] = list(task_data["DaysOfWeek"].keys())

    def set_time_month(self, task_data):
        self.attributes["schedule"] = "ScheduleByMonth"
        if "DaysOfMonth" in task_data:
            self.attributes["daysOfMonth"] = list(task_data["DaysOfMonth"].keys())
        if "Months" in task_data:
            self.attributes["months"] = list(task_data["Months"].keys())

    def select_set_time(self, schedule, task_data):
        if schedule == "ScheduleByDay":
            self.set_time_day(task_data)
        elif schedule == "ScheduleByWeek":
            self.set_time_week(task_data)
        elif schedule == "ScheduleByMonth":
            self.set_time_month(task_data)

    def set_trigger_time(self):
        if "ExecutionTimeLimit" in self.attributes["task_data"]:
            self.attributes["executionLimit"] = self.attributes["task_data"]["ExecutionTimeLimit"]
        if "Repetition" in self.attributes["task_data"]:
            if "Duration" in self.attributes["task_data"]["Repetition"]:
                self.attributes["duration"] = self.attributes["task_data"]["Repetition"]["duration"]
            if "Interval" in self.attributes["task_data"]["Repetition"]:
                self.attributes["interval"] = self.attributes["task_data"]["Repetition"]["Interval"]
            if "StopAtDurationEnd" in self.attributes["task_data"]["Repetition"]:
                self.attributes["stopAtEnd"] = self.attributes["task_data"]["Repetition"]["StopAtDurationEnd"]

    def get_schedule_time(self):
        if self.attributes["calenderTrigger"]:
            pattern = "(?P<schedule>ScheduleBy.*)"
            for tag in self.attributes["task_data"]:
                match = re.match(pattern, tag)
                if match:
                    schedule = match.group("schedule")
                    self.select_set_time(schedule, self.attributes["task_data"][schedule])
        elif not self.attributes["calenderTrigger"]:
            self.set_trigger_time()

    def return_information(self):
        self.get_schedule_time()
        res = {}
        self.attributes["calenderTrigger"] = None
        for attribute, value in self.attributes.items():
            if value and attribute != "task_data":
                res[attribute] = value
        return res


class ScheduledTaskParser:
    def __init__(self, dir_path):
        self.scheduled_task_reader = ScheduledTaskReader(dir_path)
        self.scheduled_tasks = self.scheduled_task_reader.scheduled_tasks
        self.add_additional_information()

    def add_additional_information(self):
        for index, schedule_task in enumerate(self.scheduled_tasks):
            schedule_task_data = schedule_task["task_data"]
            enabled = self.get_enabled(schedule_task_data)
            self.scheduled_tasks[index]["enabled"] = enabled
            self.scheduled_tasks[index]["schedule_time"] = self.get_schedule_time(schedule_task_data)
            self.scheduled_tasks[index]["hidden"] = self.get_hidden_flag(schedule_task_data)
            self.scheduled_tasks[index]["triggers"] = self.get_triggers(schedule_task_data)
            self.scheduled_tasks[index]["exec_command"] = self.get_exec_command(schedule_task_data)
            self.scheduled_tasks[index]["exec_args"] = self.get_exec_args(schedule_task_data)

    def get_enabled(self, task_data):
        return "Enabled" in task_data["Settings"] and task_data["Settings"]["Enabled"] == "true"

    def get_schedule_time(self, task_data):
        if "Triggers" in task_data and task_data["Triggers"]:
            if "CalendarTrigger" in task_data["Triggers"]:
                if (
                    "Enabled" in task_data["Triggers"]["CalendarTrigger"]
                    and task_data["Triggers"]["CalendarTrigger"]["Enabled"] == "true"
                ) or "Enabled" not in task_data["Triggers"]["CalendarTrigger"]:
                    schedule_time = ScheduleTimeParser(task_data["Triggers"]["CalendarTrigger"], True)
                    return schedule_time.return_information()

            if "TimeTrigger" in task_data["Triggers"]:
                if (
                    "Enabled" in task_data["Triggers"]["TimeTrigger"]
                    and task_data["Triggers"]["TimeTrigger"]["Enabled"] == "true"
                ) or "Enabled" not in task_data["Triggers"]["TimeTrigger"]:
                    schedule_time = ScheduleTimeParser(task_data["Triggers"]["TimeTrigger"], False)
                    return schedule_time.return_information()
        return "N/A"

    def get_hidden_flag(self, task_data):
        if "Hidden" in task_data["Settings"]:
            return task_data["Settings"]["Hidden"] == "true"
        return False

    def get_triggers(self, task_data):
        triggers = []
        if "Triggers" in task_data and task_data["Triggers"]:
            for trigger, data in task_data["Triggers"].items():
                if data and "Enabled" in data and data["Enabled"] == "true":
                    triggers.append(trigger)
                elif data and "Enabled" not in data:
                    triggers.append(trigger)
                elif not data:
                    triggers.append(trigger)
        return triggers

    def get_exec_command(self, task_data):
        if "Actions" in task_data and "Exec" in task_data["Actions"] and "Command" in task_data["Actions"]["Exec"]:
            return task_data["Actions"]["Exec"]["Command"]
        return ""

    def get_exec_args(self, task_data):
        if "Actions" in task_data and "Exec" in task_data["Actions"] and "Arguments" in task_data["Actions"]["Exec"]:
            return task_data["Actions"]["Exec"]["Arguments"]
        return ""


class ScheduledTaskReader:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.scheduled_tasks = self.get_scheduled_tasks()

    def get_scheduled_tasks(self):
        """iterate through every file in the directory and call get_scheduled_task_information"""
        scheduled_tasks = []
        for path, subdirs, files in os.walk(self.dir_path):
            for task_name in files:
                scheduled_tasks.append(self.get_scheduled_task_information(path, task_name))
        return scheduled_tasks

    def get_scheduled_task_information(self, path, task_name):
        full_path = os.path.join(path, task_name)

        with open(full_path, "r", encoding="utf-16") as file:
            task_data = xmltodict.parse(file.read())["Task"]
        task_path = os.path.relpath(path, self.dir_path)

        return {"task_path": task_path, "task_name": task_name, "task_data": task_data}


def main():
    CLIHandler()


if __name__ == "__main__":
    main()
