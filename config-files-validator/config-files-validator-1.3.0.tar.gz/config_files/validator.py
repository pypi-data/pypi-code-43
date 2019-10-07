import os

import json
import argparse
import yaml
import jinja2
import toml
from junit_xml import TestCase, TestSuite


class Result:
    def __init__(self, passed, path, msg=""):
        self.msg = msg
        self.test_case = TestCase(name=path)
        if not passed:
            assert msg
            self.test_case.add_failure_info(message=msg)

    def to_output(self):
        if self.test_case.is_failure():
            return f"{self.test_case.name} FAILED\n{self.test_case.failure_message}"
        return f"{self.test_case.name} PASSED"

    @property
    def passed(self):
        return not self.test_case.is_failure()


def xunit_report(results, file_type):
    test_cases = [result.test_case for result in results]
    test_suite = TestSuite(test_cases=test_cases, name=file_type)
    return TestSuite.to_xml_string(test_suites=[test_suite])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xunit", help="Generate xunit result file", action="store_true")
    parser.add_argument("--xunit-output-file", help="Xunit result file name", default="testreport.xml")
    parser.add_argument("files", nargs="+")
    return parser.parse_args()


def toml_validation_result(file):
    try:
        toml.load(file)
    except toml.TomlDecodeError as e:
        return Result(passed=False, path=file.name, msg=str(e))
    return Result(passed=True, path=file.name)


def yaml_validation_result(file):
    try:
        yaml.full_load(file)
    except yaml.YAMLError as e:
        return Result(passed=False, path=file.name, msg=str(e))
    return Result(passed=True, path=file.name)


def json_validation_result(file):
    try:
        json.load(file)
    except json.decoder.JSONDecodeError as e:
        return Result(passed=False, path=file.name, msg=str(e))
    return Result(passed=True, path=file.name)


def jinja2_validation_result(file):
    try:
        jinja2.Environment(autoescape=True).parse(file.read())
    except jinja2.exceptions.TemplateSyntaxError as e:
        return Result(passed=False, path=file.name, msg=str(e))
    return Result(passed=True, path=file.name)


def report_valid_files(file_type):
    failed = False
    args = parse_args()
    results = []
    for file_name in args.files:
        with open(file_name, "r") as config_file:
            if file_type == "yaml":
                result = yaml_validation_result(config_file)
            elif file_type == "json":
                result = json_validation_result(config_file)
            elif file_type == "jinja2":
                result = jinja2_validation_result(config_file)
            elif file_type == "toml":
                result = toml_validation_result(config_file)
            else:
                assert False
            if not result.passed:
                failed = True
            results.append(result)
        print(result.to_output())

        if args.xunit:
            xunit_folder = os.path.dirname(args.xunit_output_file)
            if xunit_folder:
                os.makedirs(xunit_folder, exist_ok=True)
            with open(args.xunit_output_file, "w") as xunit_file:
                xunit_file.write(xunit_report(results, file_type))

    if failed:
        exit(1)


def report_valid_json_files():
    report_valid_files("json")


def report_valid_yaml_files():
    report_valid_files("yaml")


def report_valid_jinja2_files():
    report_valid_files("jinja2")


def report_valid_toml_files():
    report_valid_files("toml")
