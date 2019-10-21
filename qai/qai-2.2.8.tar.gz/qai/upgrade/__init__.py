import pprint
import os
import sys

from difflib import Differ
from typing import Tuple

from qai import __version__


pp = pprint.PrettyPrinter(indent=2)


def find_files(dir_abspath) -> Tuple[str, str, str]:
    # find application
    app = os.path.join(dir_abspath, "app.py")
    application = os.path.join(dir_abspath, "application.py")
    if not (os.path.exists(app) or os.path.exists(application)):
        raise FileNotFoundError(
            f"there is no app.py or application.py in the provided directory, {dir_abspath}"
        )
    app_path = app if os.path.exists(app) else application

    docker_path = os.path.join(dir_abspath, "Dockerfile")
    if not (os.path.exists(docker_path)):
        raise FileNotFoundError(
            f"there is no Dockerfile in the provided directory, {dir_abspath}"
        )

    requirements_path = os.path.join(dir_abspath, "requirements.txt")
    if not (os.path.exists(requirements_path)):
        with open(requirements_path, "w+") as f:
            f.write("")

    return app_path, docker_path, requirements_path


class DockerFile:
    new_base = "qsam/spacy_alpine:37"

    def __init__(self, fp):
        self.name = "Dockerfile"
        self.fp = fp
        with open(fp, "r") as f:
            self.lines = f.readlines()
        self.condition_modifier = [
            (
                lambda i, line: "FROM gcr.io/qordoba-devel/qai:" in line,
                self.from_replace,
            ),
            (lambda i, line: "WORKDIR /qai" in line, self.delete_line),
            (
                lambda i, line: "#" in line
                and "only" in line
                and "deps" in line
                and "qai" in line,
                self.delete_line,
            ),
            (lambda i, line: "pip install ." in line, self.delete_line),
        ]

    def from_replace(self, i, line):
        self.lines[i] = f"FROM {self.new_base}"

    def delete_line(self, i, line):
        self.lines[i] = ""

    def parse_lines(self):
        """
        This script will be run ~6 times.
        So better for the script to be slow, but writting it to be fast

        This method should be idempotent
        """
        for i, line in enumerate(self.lines):
            for condition, modifier in self.condition_modifier:
                if condition(i, line):
                    modifier(i, line)

    def dry_run(self):
        self.parse_lines()
        return "".join(self.lines)

    def update_DESTRUCTIVE(self):
        with open(self.fp, "w+") as f:
            f.write(self.dry_run())


class RequirementsTxt:
    def __init__(self, fp):
        self.name = "requirements.txt"
        self.fp = fp
        with open(self.fp, "r+") as f:
            self.req = f.read()
        self.qai = f"qai>={__version__}"

    def dry_run(self):
        return self.req.rstrip("\n") + f"\n{self.qai}\n"

    def update_DESTRUCTIVE(self):
        with open(self.fp, "w+") as f:
            f.write(self.dry_run())


class ApplicationDotPy:
    def __init__(self, fp):
        self.name = "application.py" if "application" in fp else "app.py"
        self.fp = fp
        with open(self.fp, "r") as f:
            self.lines = f.readlines()

    def add_connect_call_post_qconnect(self, i, line, start_pos=None, depth=0):
        if start_pos is None:
            depth = 1
            Qconnect = "QConnect("
            offset = len(Qconnect)
            start_pos = line.index(Qconnect) + offset
        for i_char, c_char in enumerate(line[start_pos:]):
            if c_char == "(":
                depth += 1
            elif c_char == ")":
                depth -= 1

            if depth == 0:
                print("found closing paren")
                newline = line[: i_char + offset + 1].rstrip() + ".connect()"
                self.lines[i] = newline

        if depth > 0:
            # QConnect(... must coninue on next line
            self.lines[i] = line.rstrip() + self.lines[i + 1].strip()
            del self.lines[i + 1]
            self.add_connect_call_post_qconnect(i, self.lines[i])

        if depth > 5:
            raise RecursionError(
                "Can't automatically replace QConnect with QRest, do it yourself"
            )

    def fix(self):
        for i, line in enumerate(self.lines):
            if "from qai" in line and "import QRest" in line:
                self.lines[i] = "from qai.qconnect.qrest import QRest"
            if "import QConnect" in line:
                self.lines[i] = "from qai.qconnect.qrest import QRest"
            if "QConnect(" in line:
                self.add_connect_call_post_qconnect(i, line)
                self.lines[i] = self.lines[i].replace("QConnect", "QRest")

    def dry_run(self):
        self.fix()
        return "".join(self.lines)

    def update_DESTRUCTIVE(self):
        with open(self.fp, "w") as f:
            f.write(self.dry_run())


def command_line():

    try:
        supplied_dir = sys.argv[1]
    except:
        supplied_dir = None

    if supplied_dir is None or not os.path.isdir(supplied_dir):
        raise ValueError(
            "Call this script with the path of the directory you want to fix"
            "e.g. `python -m qai.upgrade .` or `python -m qai.upgrade Users/sh/q/repos/service.formality`"
        )

    SERVICE_DIR = os.path.abspath(sys.argv[1])
    app_path, docker_path, requirements_path = find_files(SERVICE_DIR)

    with open(app_path, "r") as af, open(docker_path) as df, open(
        requirements_path
    ) as rf:
        old_files = [af.readlines(), df.readlines(), rf.readlines()]

    fixers = [
        ApplicationDotPy(app_path),
        DockerFile(docker_path),
        RequirementsTxt(requirements_path),
    ]

    outputs = [x.dry_run().splitlines(keepends=True) for x in fixers]

    print("The following changes would be applied:\n\n")

    d = Differ()
    for i in range(len(old_files)):
        print(f"{fixers[i].name}:\n")
        result = list(d.compare(old_files[i], outputs[i]))
        pp.pprint(result)
        print("\n")

    should_fix = input("Apply these changes? y or n")

    if should_fix != "y":
        print("no changes applied.")
        exit(0)

    for x in fixers:
        print(f"\nfixing {x.name}\n")
        x.update_DESTRUCTIVE()
    print("\n\ndone\n\n")

