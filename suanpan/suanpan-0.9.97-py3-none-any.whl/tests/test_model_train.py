import os

import suanpan
from suanpan.app import app
from suanpan.app.arguments import Int, Model
from suanpan.model import Model as BaseModel
from suanpan.utils import json


class TestModel(BaseModel):
    def load(self, path):
        self.model = json.load(os.path.join(path, "model.json"))

    def save(self, path):
        json.dump(self.model, os.path.join(path, "model.json"))

    def train(self, data):
        self.model = {"value": data}

    def predict(self, features):
        return self.model["value"]


@app.output(Model(key="outputModel1", type=TestModel))
@app.param(Int(key="param1"))
def test_train(context):
    args = context.args
    args.outputModel1.train(args.param1)
    return args.outputModel1


if __name__ == "__main__":
    suanpan.run(app)
