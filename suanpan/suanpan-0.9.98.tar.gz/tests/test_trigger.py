import suanpan
from suanpan.app import app
from suanpan.app.arguments import Folder, String


@app.input(Folder(key="inputData1"))
@app.output(Folder(key="outputData1"))
@app.param(String(key="param1"))
def test1(context):
    args = context.args
    print(args.param1)
    return args.outputData1


@app.trigger(interval=1)
@app.trigger.output(Folder(key="outputData1"))
@app.trigger.param(String(key="param2"))
def test2(context):
    args = context.args
    print(args.param2)
    return args.outputData1


if __name__ == "__main__":
    suanpan.run(app)
