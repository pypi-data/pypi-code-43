import os
from pathlib import Path
from rikki.template.environment import environment_template
from rikki.template.feature import feature_template
from rikki.template.run_file import run_file_template
from rikki.template.behave_ini_file import behave_ini_file_templete


def behave_init():
    features_folder_name = "features"
    resource_folder_name = "res"

    if not os.path.exists(Path(features_folder_name)):
        os.makedirs(Path(features_folder_name))

    if not os.path.exists(Path(resource_folder_name)):
        os.makedirs(Path(resource_folder_name))

    steps_folder_path = Path("{0}/steps".format(features_folder_name))

    if not os.path.exists(steps_folder_path):
        os.makedirs(steps_folder_path)

    with open(Path("features/environment.py"), "w") as environment:
        environment.write(environment_template)

    with open(Path("features/example.feature"), "w") as example_feature:
        example_feature.write(feature_template)

    with open(Path("run.py"), "w") as run_file:
        run_file.write(run_file_template)

    with open(Path("behave.ini"), "w") as behave_ini_file:
        behave_ini_file.write(behave_ini_file_templete)
