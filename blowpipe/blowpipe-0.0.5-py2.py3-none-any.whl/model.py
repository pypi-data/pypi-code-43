"""
the blowpipe.model package represents all the in-memory data structures we required
they can be persisted using the blowpipe.model_db package
"""
import json
import yaml as yaml_lib
from blowpipe import constants
from urllib.request import urlopen
from blowpipe import logger


class Workflow:
    """
    A Workflow contains the steps and describes the order of operations,
    conditions under which it runs
    """

    def __init__(self, yaml=None):
        if yaml is not None:
            self.load_raw(yaml)

    def get(self, key, default_value=None):
        self._data.get(key) or default_value

    def load_file(self, filename):
        self.filename = filename
        if filename.lower().startswith("http"):
            contents = urlopen(filename).read()
            self.load_raw(contents)
        else:
            with open(filename, "r") as f:
                file_data = f.read()
                self.load_raw(file_data)

    def load_raw(self, yaml):
        self._yaml = yaml
        self._data = yaml_lib.safe_load(yaml)
        self._steps = []
        for step_data in self._data.get("steps"):
            step = Step(step_data, self)
            self._steps.append(step)

    def to_yaml(self):
        return yaml_lib.dump(self._data)

    def get_name(self):
        return self._data.get("name")

    def get_description(self):
        return self._data.get("description") or None

    def set_name(self, name):
        self._data["name"] = name

    def set_description(self, name):
        self._data["description"] = name

    def get_state(self):
        return self._data.get("state") or constants.STATE_UNKNOWN

    def set_state(self, state):
        self._data["state"] = state

    def get_variables(self):
        return self._data.get("variables") or {}

    def get_all_steps(self):
        return self._steps

    def get_step(self, step_name):
        for s in self.get_all_steps():
            if s.get_name() == step_name:
                return s
        return None

    def get_running_steps(self):
        results = []
        for s in self.get_all_steps():
            if s.is_running():
                results.append(s)
        return results

    def get_ready_to_run_steps(self):
        results = []
        for s in self.get_all_steps():
            if not s.is_running() and not s.is_complete():
                # then it might be ready to run if all dependencies have been met
                dependencies = s.get_dependencies()
                is_ready_to_run = True
                for step in dependencies:
                    if not step.is_complete():
                        is_ready_to_run = False
                        break
                if is_ready_to_run:
                    results.append(s)
        return results

    def get_root_steps(self):
        """
        returns the entrypoint step(s) in the workflow
        """
        roots = []
        for step in self.get_all_steps():
            if step.is_root():
                roots.append(step)
        if len(roots) == 0:
            roots.append(self.get_all_steps()[0])
        return roots

    def validate(self):
        """
        inspects self to understand if the Step definition is valid
        returns Tuple (bool, reasons[])
        """
        return True, []

    def __eq__(self, other):
        if other is None:
            return False
        return self.get("id") == other.get("id")


class Step:
    """
    A Step is unit of work within the Workflow
    It does not have a DB entry as it is in the yaml/graph; the object model is built
    whenever we effectively deserialise the workflow from the db
    """

    def __init__(self, data, workflow):
        self._data = data
        self._workflow = workflow
        self.logger = logger.Logger("Step: " + self.get_name())

    def validate(self):
        """
        inspects self to understand if the Step definition is valid
        returns Tuple (bool, reasons[])
        """
        return True, []

    def get_children(self):
        """
        returns any children to be executed after this concludes
        :return:
        """
        all_steps = self._workflow.get_all_steps()
        children = []
        for step in all_steps:
            if self in step.get_dependencies():
                children.append(step)
        return children

    def get_dependencies(self):
        """
        returns all Steps that this Step depends on having previously completed
        before it can run
        :return:
        """
        dependencies = []
        names = self._data.get("depends_on") or []
        for name in names:
            step = self._workflow.get_step(name)
            dependencies.append(step)
        return dependencies

    def environment(self):
        return self._data.get("environment") or {}

    def is_enabled(self):
        return self._data.get("is_enabled") or True

    def is_root(self):
        return self._data.get("is_entrypoint") or False

    def get_image_name(self):
        return self._data.get("image")

    def set_container_name(self, container_name):
        self._data["container_name"] = container_name

    def get_container_name(self):
        return self._data.get("container_name") or None

    def set_started(self, started):
        self._data["container_started"] = started

    def get_started(self):
        return self._data.get("container_started") or None

    def set_completed(self, completed):
        self._data["container_completed"] = completed

    def get_completed(self):
        return self._data.get("container_completed") or None

    def get_name(self):
        return self._data.get("name")

    def get_command(self):
        return self._data.get("command")

    def is_running(self):
        state = self.get_state()
        return state == constants.STATE_IN_PROGRESS

    def is_complete(self):
        state = self.get_state()
        return state == constants.STATE_COMPLETE

    def get_state(self):
        return self._data.get("state") or constants.STATE_IDLE

    def set_state(self, state):
        self.logger.debug(">>>>>>>>> .set_state('" + self.get_state() + "' => '" + state + "')")
        self._data["state"] = state

    def environment(self):
        return self._data.get("environment")

    def set_container_info(self, container_info):
        """
        unpacks the passed ContainerInfo and stores the raw data
        :return:
        """
        self._data["container_info"] = container_info.data

    def get_container_info(self):
        """
        returns a ContainerInfo wrapper, or None
        :return:
        """
        info = self._data.get("container_info") or None
        if info is not None:
            return ContainerInfo(info)
        else:
            return None

    def get_container_exit_code(self):
        return self.get_container_info().get_container_exit_code()
        # self._data.get("container_exit_code")

    def __repr__(self):
        return json.dumps(self._data, indent=4)


class ContainerInfo:
    """
    wrapper class for the response from a docker api call
    useful when querying the json returned
    """

    def __init__(self, data):
        self.data = data

    def is_container_complete(self):
        return self.get_container_status() == "exited"

    def is_container_running(self):
        return self.data.get("State").get("Running")

    def is_container_paused(self):
        return self.data.get("State").get("Paused")

    def is_container_restarting(self):
        return self.data.get("State").get("Restarting")

    def is_container_oom_killed(self):
        return self.data.get("State").get("OOMKilled")

    def is_container_dead(self):
        return self.data.get("State").get("Dead")

    def get_container_name(self):
        return self.data.get("Name")

    def get_container_image(self):
        return self.data.get("Image")

    def get_container_exit_code(self):
        return self.data.get("State").get("ExitCode")

    def get_container_error(self):
        return self.data.get("State").get("Error")

    def get_container_started_at(self):
        return self.data.get("State").get("StartedAt")

    def get_container_finished_at(self):
        return self.data.get("State").get("FinishedAt")

    def get_container_status(self):
        return self.data.get("State").get("Status")

    def get_container_env(self):
        return self.data.get("Config").get("Env")
