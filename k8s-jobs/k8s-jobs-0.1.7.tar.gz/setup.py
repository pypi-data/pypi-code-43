# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['k8s_jobs']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses>=0.6.0,<0.7.0', 'jinja2>=2.10,<3.0', 'kubernetes>=10.0,<11.0']

setup_kwargs = {
    'name': 'k8s-jobs',
    'version': '0.1.7',
    'description': 'Async Job Manager + AWS Batch Replacement for K8s',
    'long_description': 'K8s Jobs\n=========\n\n.. image:: https://badge.fury.io/py/k8s-jobs.svg\n    :target: https://badge.fury.io/py/k8s-jobs\n.. image:: https://travis-ci.com/danieltahara/k8s-jobs.svg?token=cZTmQ2jMoLFe6Ve33X6M&branch=master\n\nK8s Jobs is a library for implementing an asynchronous job server on Kubernetes. It is\nintended to provide a simple framework for executing single-shot asynchronous jobs or\ncommands (unlike something like Celery that can have arbitrary fanout and nesting), as\nwell as a server implementation that can stand in as a replacement for AWS Batch and\ntrigger jobs on-command.\n\nKubernetes Job Management\n-------------------------\n\nThis project provides an abstraction around kubernetes APIs to allow you to dynamically\nspawn (templated) jobs and clean up after them when they have run.\n\nThe two abstractions of interest are the ``JobManager`` and ``JobManagerFactory``. The\nlatter provides a factory for the former and helps convert (kubernetes) configuration\ninto a working application.\n\nThe ``JobManager`` is responsible for creating (templated) jobs given a job definition\nname and template arguments. It is recommended that the jobs target a dedicated node\ninstance group so as not to contend with live application resources. It is further\nrecommended that you configure the `Cluster Autoscaler\n<https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler>`_ on this\ninstance group to ensure you do not run out of capacity (even better would be something\nlike the `Escalator <https://github.com/atlassian/escalator>`_, a batch job-oriented\nautoscaler). This will most closely mirror the behavior of a service like AWS Batch,\nwhich automatically adjusts the number of nodes based on workload.\n\nThe ``JobManager`` is also responsible for cleaning up terminated (completed or failed)\njobs after some retention period. This is provided for version compatibility across K8s,\nand to avoid using a feature that is still in Alpha. For more details, see the `TTL\nController\n<https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/>`_.\n\nLabeling and Annotations\n++++++++++++++++++++++++\n\nThe ``JobManager`` (and associated objects) makes use of `labels and annotations\n<https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/>`_ in\norder to properly identify and manage jobs. Of note are the following:\n\nLabels:\n\n* ``app.kubernetes.io/managed-by``: A recommended kubernetes label, populated with the\n  value of the ``JobSigner`` signature. This is used to logically identify jobs created\n  by the ``JobManager`` of interest, rather than by third party applications or users.\n* ``job_definition_name``: Identifies the job definition on which the job was based\n  (maps to a name in the manager config).\n\nAnnotations:\n\n* ``job_deletion_time_unix_sec``: If present, the earliest time at which the job can be\n  deleted. It is only set after the job has reached a terminal state. This is meant to\n  help implement baseline retention for resource management purposes, as well as to\n  provide an avenue for users to mark and prevent the deletion of a job so that it can\n  be inspected for debugging.\n\nExamples\n--------\n\nFlask Server\n++++++++++++\n\nThe server is a proof-of-concept implementation intended as a replacement for and\nextension to AWS Batch. It is a flask application housed completely under\n``examples/flask``. You do not need to use the server in order to take advantage of the\nprimitives on which it relies.\n\nThe server listens on a route for job creation requests, much in the same way AWS batch\nmight be implemented under the hood.\n\nKubernetes Resources\n++++++++++++++++++++\n\nThe Kubernetes resources under ``examples/k8s/`` provide the configuration needed for\ndeploying a server to Kubernetes. Specifically, it demonstrates how to configure jobs to\nbe run by the manager.  It relies on ConfigMap volume mounts in order to load the\ntemplates into a consistent location. See the ``JobManagerFactory`` for the specific\nrequired structure.\n\nThere is a corresponding dockerfile at ``examples/Dockerfile`` that can be used with the\ntemplates. You can build it as follows:\n\n.. code::\n\n   docker build -t flask-app -f examples/Dockerfile .\n\nQuickStart\n----------\n\nTo install dependencies:\n\n.. code:: bash\n\n  poetry install\n\nTo run the sample server locally (make sure you have ``~/.kube/config`` configured):\n\n.. code:: bash\n\n  JOB_SIGNATURE=foo JOB_NAMESPACE=default JOB_DEFINITIONS_CONFIG_PATH=path/to/conf python examples/flask/app.py\n',
    'author': 'Daniel Tahara',
    'author_email': 'dktahara@gmail.com',
    'url': 'https://github.com/danieltahara/k8s-jobs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.8',
}


setup(**setup_kwargs)
