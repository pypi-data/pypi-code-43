import suanpan
from suanpan.app import app
from suanpan.app.arguments import String


@app.output(String(key="outputData1"))
def hello_world(_):
    for i in range(10):
        app.send(str(i))


if __name__ == "__main__":
    suanpan.run(app)
