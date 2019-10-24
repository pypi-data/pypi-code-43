import logging

from polytropos.ontology.task import Task

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
conf_path = "/dmz/github/analysis/etl5"
data_path = "/tmp/debug"
task = "origin_to_logical_tr_only"
task = Task.build(conf_path, data_path, task)
task.run()