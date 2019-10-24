import suanpan
from suanpan.app import app
from suanpan.app.arguments import String


@app.output(String(key="outputData1"))
def hello_world(_):
    return "Hello World!"


if __name__ == "__main__":
    suanpan.run(app)
