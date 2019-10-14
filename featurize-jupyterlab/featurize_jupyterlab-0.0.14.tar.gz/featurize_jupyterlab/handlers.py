import json
import os
from pathlib import Path
import shutil
from datetime import datetime
from .package_manager import PackageManager
from .proto import minetorch_pb2
import stream

from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import APIHandler, web
from . import core
import hashlib
import collections
from .experiment import Experiment
from .utils import featurize_dir


class FeaturizeHandler(APIHandler):

    def finish(self, data = {}):
        wrapped_data = {
            'status': 'success',
            'data': data,
        }
        return super().finish(json.dumps(wrapped_data))

    def prepare(self):
        self.experiment = None
        self.post_data = None

        if self.request.method == 'POST':
            self.post_data = json.loads(self.request.body)
            identity = self.post_data.get('identity', None)
        else:
            identity = self.get_argument('identity', None)

        if identity is not None:
            self.experiment = Experiment(identity)


class CommitmentHandler(FeaturizeHandler):

    def post(self):
        self.experiment.commit_config()
        self.experiment.generate_runtime_config()
        self.experiment.create_docker_zip_file()
        self.finish()


class DockerfileHandler(web.RequestHandler):

    def get(self):
        identity = self.get_argument('identity', None)
        if identity is None:
            self.set_status(400)
            self.finish()
            return
        experiment = Experiment(identity)

        self.set_header("Content-Disposition", "attachment; filename=docker.tar.gz")
        with open(experiment.docker_file(), 'rb') as f:
            while 1:
                data = f.read(16384) # or some other nice-sized chunk
                if not data: break
                self.write(data)
        self.finish()

class ExperimentHandler(FeaturizeHandler):

    def post(self):
        sha1 = hashlib.sha1()
        data = json.loads(self.request.body)
        sha1.update(data['name'].encode('utf-8'))
        identity = sha1.hexdigest()
        experiment = Experiment(identity)
        package = PackageManager()

        config = {
            'version': 1,
            'server_addr': f'{self.request.host.split(":")[0]}:6725',
            'name': data['name'],
            'enabled_package': ','.join(package.packages),
            'identity': identity,
            'created_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'components': {}
        }
        experiment.update_config(config)
        experiment.update_metadata({
            'version': 'draft',
            'identity': identity,
            'created_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'status': 'not_running',
            'total_versions': 0,
            'name': data['name']
        })
        self.finish(config)

    def get(self):
        if self.experiment is None:
            # TODO: load all experiments is expensive, should add cache
            metadatas = []
            for identity in os.listdir(featurize_dir):
                metadatas.append(Experiment(identity).get_metadata())
            self.finish(metadatas)
        else:
            self.finish(self.experiment.get_metadata())

    def delete(self):
        self.experiment.delete()
        self.finish()


class ComponentsHandler(FeaturizeHandler):

    def get(self):
        component_type = self.get_argument("type", None)
        if component_type is not None:
            component = getattr(core, component_type)
        else:
            component = core.ComponentDecorator
        data = list(map(lambda m: m.to_json_serializable(), component.registed_components))
        self.finish(data)


class ConfigHandler(FeaturizeHandler):

    def get(self):
        config = self.experiment.get_config('draft')
        self.finish(config)

    def post(self):
        data = json.loads(self.request.body)
        self.experiment.update_config(data['config'])
        self.finish(self.experiment.get_config('draft'))


class ExperimentStatusHandler(FeaturizeHandler):
    def post(self):
        self.experiment.update_metadata({
            'status': self.post_data['status']
        })


class ExperimentGraphHandler(FeaturizeHandler):
    def get(self):
        graph_name = self.get_argument('graph_name', None)
        start_at = int(self.get_argument('start_at', 0))

        with open(self.experiment.graph_file(graph_name), 'rb') as f:
            f.seek(start_at)
            points = [a for a in stream.parse(f, minetorch_pb2.Point)]
            points = list(map(lambda p: {'x': p.x, 'y': p.y}, points))
            self.finish({
                'position': f.tell(),
                'points': points,
            })


class LogHandler(FeaturizeHandler):
    def get(self):
        offset = int(self.get_argument('offset', 0))
        limit = int(self.get_argument('limit', 1000))

        with open(self.experiment.log_file(), 'r') as f:
            f.seek(offset)
            content = f.read(limit)
            while True:
                char = f.read(1)
                if char and char != "\n":
                    content += char
                else:
                    break
            self.finish({
                'read_up_to': f.tell(),
                'logs': content,
            })


class RemarkHandler(FeaturizeHandler):
    def post(self):
        self.experiment.add_remark(self.post_data['remark'])
        self.finish()


def setup_handlers(npapp):
    featurize_handlers = [
        ("/featurize/components", ComponentsHandler),
        ("/featurize/config", ConfigHandler),
        ("/featurize/experiments", ExperimentHandler),
        ("/featurize/experiments/status", ExperimentStatusHandler),
        ("/featurize/commitment", CommitmentHandler),
        ("/featurize/experiments/graphs", ExperimentGraphHandler),
        ("/featurize/experiments/log", LogHandler),
        ("/featurize/experiments/remark", RemarkHandler),
        ("/featurize/experiments/dockerfile", DockerfileHandler)
    ]

    # add the baseurl to our paths
    base_url = npapp.web_app.settings["base_url"]
    featurize_handlers = [(ujoin(base_url, x[0]), x[1]) for x in featurize_handlers]
    npapp.web_app.add_handlers(".*", featurize_handlers)
