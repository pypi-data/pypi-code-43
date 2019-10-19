from pathlib import Path
import os
import json
import collections
import shutil
import stream
import tempfile
import shutil
from .utils import dict_merge, update_json_file, read_json_file, make_tarfile
from .proto import minetorch_pb2


class Experiment():

    def __init__(self, identity):
        self.identity = identity
        self.experiment_dir = self._prepare_directories()

    def _prepare_directories(self):
        featurize_dir = Path() / '.featurize_experiments'
        if not os.path.isdir(featurize_dir):
            os.mkdir(featurize_dir)
        experiment_dir = featurize_dir / self.identity
        if not os.path.isdir(experiment_dir):
            os.mkdir(experiment_dir)
        return experiment_dir

    def update_config(self, config):
        config_file_path = self.config_file('draft')
        if os.path.isfile(config_file_path):
            with open(config_file_path, 'r') as f:
                original_config = json.load(f)
            dict_merge(original_config, config)
        else:
            original_config = config
        with open(config_file_path, 'w') as f:
            json.dump(original_config, f)

    def config_file(self, version):
        return self.experiment_dir / f'config.{str(version)}.json'

    def metadata_file(self):
        return self.experiment_dir / 'metadata.json'

    def runtime_config_file(self):
        return self.experiment_dir / 'runtime.config.json'

    def generate_runtime_config(self):
        """use metadata and current.config.json to generate a runtime.config.json
        file, which can be feed to featurize-runtime agent directly
        """
        runtime_config = self.get_metadata()
        config = self.get_config('current')
        dict_merge(runtime_config, config)
        update_json_file(self.runtime_config_file(), runtime_config)

    def commit_config(self):
        """Archived current version, publish draft version and create new draft
        version. Commit will also generate runtime config file
        """
        draft = self.config_file('draft')
        current = self.config_file('current')
        metadata = self.get_metadata()

        draft_config = self.get_config('draft')

        if os.path.isfile(current):
            # if has current, archived it
            current_config = self.get_config('current')
            shutil.move(current, self.config_file(current_config['version']))

        # make the draft version as the current
        shutil.copy(draft, current)

        # create a new draft version similar to the current,
        # except the version number should plus onek
        draft_config['version'] += 1
        self.update_config(draft_config)

        # update metadata
        metadata['total_versions'] += 1
        self.update_metadata(metadata)

    def graph_file(self, file_name):
        return self.experiment_dir / file_name

    def create_graph(self, graph_name):
        graphs = set(self.get_metadata().get('graphs', []))
        graphs.add(graph_name)
        graphs = list(graphs)
        self.update_metadata({
            'graphs': graphs
        })
        self.graph_file(graph_name).touch()

    def get_graphs(self):
        return self.get_metadata().get('graphs', [])

    def add_point(self, graph_name, point):
        graph_file = self.graph_file(graph_name)
        raw_point = minetorch_pb2.RawPoint()
        raw_point.x = point['x']
        raw_point.y = point['y']
        with open(graph_file, 'ab') as f:
            stream.dump(f, raw_point, gzip=False)

    def update_metadata(self, metadata):
        update_json_file(self.metadata_file(), metadata)

    def get_metadata(self):
        return read_json_file(self.metadata_file())

    def get_config(self, version):
        return read_json_file(self.config_file(version))

    def log_file(self):
        return self.experiment_dir / 'log.txt'

    def delete(self):
        shutil.rmtree(self.experiment_dir)

    def add_remark(self, remark):
        metadata = self.get_metadata()
        if 'remarks' not in metadata:
            metadata['remarks'] = []
        metadata['remarks'].insert(0, remark)
        self.update_metadata(metadata)

    def docker_file(self):
        return self.experiment_dir / 'docker.tar.gz'

    def create_docker_zip_file(self):
        dirpath = Path(tempfile.mkdtemp())
        requirements_file = dirpath / 'requirements.txt'
        runtime_file = dirpath / 'runtime.config.json'
        docker_file = dirpath / 'Dockerfile'

        with open(requirements_file, 'w') as f:
            content = "\n".join([
                'featurize-jupyterlab',
                'featurize-runtime',
                'featurize-package'
            ])
            f.write(content)

        with open(docker_file, 'w') as f:
            content = "\n".join([
                'FROM python:3',
                'WORKDIR /runtime',
                'COPY requirements.txt /runtime',
                'RUN pip3 install -r requirements.txt',
                'COPY . /runtime',
                'RUN featurize_server package:add ftpkg.demo',
                'CMD featurize run --config runtime.config.json',
            ])
            f.write(content)
        shutil.copy(self.runtime_config_file(), runtime_file)
        make_tarfile(self.docker_file(), dirpath)
        return dirpath
