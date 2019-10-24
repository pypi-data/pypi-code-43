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


@app.input(Int(key="inputData1"))
@app.input(Model(key="inputModel2", type=TestModel))
@app.output(Int(key="outputData1"))
@app.param(Int(key="param1"))
def test_predict(context):
    args = context.args
    return args.inputModel2.predict(args.inputData1)


@app.afterCall
def reload_model(context):
    args = context.args
    if app.isStream:
        args.inputModel2.reload(duration=args.param1)


if __name__ == "__main__":
    suanpan.run(app)
