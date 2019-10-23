import json
import os


class Model(object):
    def __init__(self, config):
        self.config = config

    def train_and_eval_then_save(self, train_input_func, eval_input_func, config):
        # I am a dummy model, so I do nothing
        evaluate_result = {"acc": 0.9, "loss": 0.001}

        export_results = None

        self._dump_data(train_input_func, os.path.join(config["saved_model_dir"], "train_data.json"))
        self._dump_data(eval_input_func, os.path.join(config["saved_model_dir"], "test_data.json"))
        final_saved_model = config["saved_model_dir"]

        return evaluate_result, export_results, final_saved_model

    @staticmethod
    def _dump_data(input_func, output_file):
        data = list(input_func())
        with open(output_file, 'wt') as fd:
            json.dump(data, fd)
