import logging
import os

from polytropos.ontology.task import Task
import polytropos.actions

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
polytropos.actions.register_all()

data_dir: str = os.path.join("/dmz/github/analysis/polytropos/examples/s_7_csv/data")
conf_dir: str = os.path.join("/dmz/github/analysis/polytropos/examples/s_7_csv/conf")
task_dir: str = os.path.join(conf_dir, "tasks")
for file in os.scandir(task_dir):
    task_name: str = file.name[:-5]
    task = Task.build(conf_dir, data_dir, task_name)
    task.run()
