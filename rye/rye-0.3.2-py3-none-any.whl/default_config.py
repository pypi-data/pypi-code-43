import sys

default = {
    "task_class": "rye.task:Task",
    "env_class": "rye.environment:Env",
    "default_tasks": [],
    "base_location": ".rye",
    "task": {"isolate": False, "target_environments": [], "commands": []},
    "environment": {
        "location": ["{{ base_location }}", "{{ ('_', name, id) | join }}"],
        "clean_existing": True,
        "depends_files": [],
        "setup_commands": [["pip", "install", "-r", "requirements.txt"]],
        "create_command": [
            sys.executable,
            "-m",
            "virtualenv",
            "{{ location | list_to_path }}",
        ],
        "install_command": [],
    },
    "environment.python37": {"python": "python3.7"},
    "environment.py37": {"python": "python3.7"},
    "environment.python36": {"python": "python3.6"},
    "environment.py36": {"python": "python3.6"},
    "environment.python38": {"python": "python3.8"},
    "environment.py38": {"python": "python3.8"},
    "environment.python27": {"python": "python2.7"},
    "environment.py27": {"python": "python2.7"},
    "environment.poetry": {
        "install_command": ["poetry", "install"],
        "depends_files": ["poetry.lock"],
        "setup_commands": [["poetry", "install", "--no-root"]],
    },
    "environment.pip": {
        "install_command": ["pip", "install", "-e", "."],
        "depends_files": ["requirements.txt"],
        "setup_commands": [["pip", "install", "-r", "requirements.txt"]],
    },
    "environment#local": {
        "location": ["{{ '' | current_venv }}"],
        "clean_existing": False,
        "python": "python",
    },
    "task.pytest": {"commands": [["pytest", "tests"]]},
    "task.setup-local-poetry": {
        "commands": [["echo", "SETUP COMPLETE"]],
        "target_environments": ["environment.poetry#local"],
    },
    "task.setup-local-pip": {
        "commands": [["echo", "SETUP COMPLETE"]],
        "target_environments": ["environment.pip#local"],
    },
}
