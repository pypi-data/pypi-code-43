"""Implements an interface for backtesting."""
import datetime
import json
import os

import bson
from IPython.display import display, clear_output
from ipywidgets import FloatProgress
from pymongo import MongoClient

from ialib.data_ops import Data
from ialib.genie_metalanguage import CLEAR_ALL_MEMORY
from ialib.tests import classification, utility


class BackTest:
    """Provides an interface for backtesting."""
    def __init__(self, **kwargs):
        """
        Pass this a configuration dictionary as the argument such as:

        test_results_database = 'mongodb://mongo-kb:27017'

        test_config = {'name':'backtest-classification',
                        'test_type': 'classification', ## 'classification' or 'utility'
                        'utype': None, ## If 'test_type' = 'utility', then set to either 'polarity' or 'value'
                        'shuffle_data': True,
                        'fresh_start_memory': True, ## Clear all memory when starting and between runs
                        'mongo_location': test_results_database, ## location of mongo db where test results will be stored
                        'learning_strategy': 'continuous', # None, 'continuous' or 'on_error'
                        'bottle': bottle,
                        'data_source': dataset, ## or provide 'data_directories' as iterable of data.
                        'percent_reserved_for_training': 20,
                        'percent_of_dataset_chosen': 100,
                        'total_test_counts': 1 }

        test = BackTest(**test_config)

        mongo_location provides the location of a mongo database where the test results will be stored.

        Option of either data_source or data_directories can be provided:

            data_source provided is a sequence of sequences of GDF objects.
            data_directories provided should be a list of directories containing files of GDF as json dumps.

        """
        self.configuration = kwargs
        self.errors = []
        self.name = str(kwargs['name'])
        self.test_type = kwargs['test_type']
        self.utype = kwargs['utype']
        self.shuffle_data = kwargs['shuffle_data']
        self.learning_strategy = kwargs['learning_strategy']
        self.fresh_start_memory = kwargs['fresh_start_memory']
        self.mongo_location = kwargs['mongo_location']
        self.bottle = kwargs['bottle']
        if 'data_directories' in self.configuration:
            self.data_directories = kwargs['data_directories']
            self.data_source = None
        elif 'data_source' in self.configuration:
            self.data_source = kwargs['data_source']
            self.configuration['data_source'] = 'from-source'
            self.data_directories = None
        self.percent_reserved_for_training = int(kwargs['percent_reserved_for_training'])
        self.percent_of_dataset_chosen = int(kwargs['percent_of_dataset_chosen'])
        self.total_test_counts = int(kwargs['total_test_counts'])
        self.current_test_count = 0

        self.mongo_client = MongoClient(self.mongo_location)  # , document_class=OrderedDict)
        # Collection storing the backtesting results is the bottle's name.
        self.mongo_client.backtesting = self.mongo_client['{}-{}-{}'.format(
            self.name, self.bottle.genome.agent, self.bottle.name)]
        self.test_configuration = self.mongo_client.backtesting.test_configuration
        self.test_status = self.mongo_client.backtesting.test_status
        self.test_errors = self.mongo_client.backtesting.test_errors
        self.backtesting_log = self.mongo_client.backtesting.backtesting_log
        self.interrupt_status = self.mongo_client.backtesting.interrupt_status

        if self.test_type == "utility":
            self._tester = utility.Tester(**kwargs)
        elif self.test_type == 'classification':
            self._tester = classification.Tester(**kwargs)

        if self.data_directories:
            self.data = Data(data_directories=self.data_directories)
        elif self.data_source:
            self.data = Data(dataset=self.data_source)
        self.data.prep(self.percent_of_dataset_chosen, self.percent_reserved_for_training, shuffle=self.shuffle_data)
        sequence_count = len(self.data.train_sequences) + len(self.data.test_sequences)

        self.number_of_things_to_do = self.total_test_counts * sequence_count
        self.number_of_things_done = 0
        self.status = "not started"

        self.interrupt_status.replace_one({}, {'interrupt': False}, upsert=True)
        self.test_status.replace_one({}, {'status': 'not started',
                                          'number_of_things_to_do': self.total_test_counts * sequence_count,
                                          'number_of_things_done': 0,
                                          'current_test_count': self.current_test_count
                                          }, upsert=True)

        self.test_errors.drop()
        self.backtesting_log.drop()
        self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "test-started"})

        self.test_configuration.drop()
        self.test_configuration.insert_one({
            'name': self.name,
            'test_type': self.test_type,
            'utype': self.utype,
            'shuffle_data': self.shuffle_data,
            'learning_strategy': self.learning_strategy,
            'fresh_start_memory': self.fresh_start_memory,
            "bottle_name": self.bottle.name,
            "agent": self.bottle.genome.agent,
            "ingress_nodes": self.bottle.ingress_nodes,
            "query_nodes": self.bottle.query_nodes
        })

        headers = ["Test Run", "Trial", "Phase", "Filename", "Historical"] + [node["name"] for node in
                                                                              self.bottle.query_nodes] + ["hive"]
        self.backtesting_log.insert_one({"headers": headers})
        self.progress = FloatProgress(min=0, max=self.number_of_things_to_do, description="Starting...", bar_style="info")

        print("Recording results at '%s-%s-%s'" % (self.name, self.bottle.genome.agent, self.bottle.name))

    def _reset_test(self):
        """Reset the instance to the state it was in when created."""
        self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "resetTest"})
        if self.data_directories:
            self.data = Data(data_directories=self.data_directories)
        elif self.data_source:
            self.data = Data(dataset=self.data_source)
        self.data.prep(self.percent_of_dataset_chosen, self.percent_reserved_for_training, shuffle=self.shuffle_data)
        self._tester.next_test_prep()

    def _end_test(self):
        """Called when the test ends."""
        self.status = "finished"
        self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "test-ended"})
        nodes_status = self.bottle.query('showStatus')
        self.test_status.replace_one({}, {'status': 'finished',
                                          'nodes_status': nodes_status,
                                          'number_of_things_to_do': self.number_of_things_to_do,
                                          'number_of_things_done': self.number_of_things_to_do,
                                          'current_test_count': self.current_test_count}, upsert=True)

    def run(self):
        display(self.progress)
        self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "run"})
        while self.current_test_count < self.total_test_counts:
            self.current_test_count += 1
            self._setup_training()
            for sequence in self.data.train_sequences:
                self._train(sequence)
                self.number_of_things_done += 1
                self.progress.value = self.number_of_things_done
                self.progress.description = '%0.2f%%' % (100 * self.number_of_things_done / self.number_of_things_to_do)

            self._setup_testing()
            for sequence in self.data.test_sequences:
                self._tester(sequence)
                self.number_of_things_done += 1
                self.progress.value = self.number_of_things_done
                self.progress.description = '%0.2f%%' % (100 * self.number_of_things_done / self.number_of_things_to_do)

            if self.current_test_count < self.total_test_counts:
                self._reset_test()
            else:
                self._end_test()
                clear_output()

    def _setup_training(self):
        """Setup instance for training."""
        self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "setupTraining"})
        self.status = "training"
        self.test_status.replace_one({}, {'status': 'training',
                                          'number_of_things_to_do': self.number_of_things_to_do,
                                          'number_of_things_done': self.number_of_things_done,
                                          'current_test_count': self.current_test_count}, upsert=True)
        if self.fresh_start_memory:
            self.bottle.observe(CLEAR_ALL_MEMORY)
        return 'ready'

    def _train(self, sequence):
        """Train with the sequence in *sequence*."""
        # get a sequence either from a file, or directly as a list:
        if self.data_directories:
            self.backtesting_log.insert_one(
                {"timestamp_utc": datetime.datetime.utcnow(), "status": "training", "file": os.path.basename(sequence)})
            with open(sequence) as f:
                sequence = [json.loads(data.strip()) for data in f if data]
        elif self.data_source:
            sequence = sequence
            self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "training"})

        ## Train the sequence:
        result_log_record = self._tester.train(sequence)
        result_log_record['trial'] = self.number_of_things_done
        result_log_record['run'] = self.current_test_count
        self.backtesting_log.insert_one(result_log_record)
        return 'ready'

    def _setup_testing(self):
        """Set up the instance to begin backtesting."""
        self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "setupTesting"})
        self.status = "testing"
        self.test_status.replace_one({}, {'status': 'testing',
                                          'number_of_things_to_do': self.number_of_things_to_do,
                                          'number_of_things_done': self.number_of_things_done,
                                          'current_test_count': self.current_test_count}, upsert=True)
        return 'ready'

    def _test(self, sequence):
        """Run the backtest on *sequence*."""
        ## get a sequence either from a file, or directly as a list:
        if self.data_directories:
            self.backtesting_log.insert_one(
                {"timestamp_utc": datetime.datetime.utcnow(), "status": "testing", "file": os.path.basename(sequence)})
            with open(sequence) as f:
                sequence = [json.loads(data.strip()) for data in f if data]
        elif self.data_source:
            sequence = sequence
            self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "testing"})

        ## Test the sequence and record the results.
        result_log_record = self._tester.test(sequence)
        result_log_record['trial'] = self.number_of_things_done
        result_log_record['run'] = self.current_test_count
        self.backtesting_log.insert_one(bson.son.SON(result_log_record))
        return 'ready'
