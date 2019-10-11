from flask import Flask
from flask import session, request
from flask import render_template

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return "server_flask.index(): hi"  # render_template("index.html", message="hello, world")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files["file"]
        f.save("/tmp/workflow_1.yml")


@app.route("/download")
@app.route("/download/<string:workflow_id>")
def download(workflow_id=None):
    return "download %s" % workflow_id


@app.route("/list")
def list():
    return "list"


@app.route("/run")
def run():
    return "run"


@app.route("/logs")
def logs():
    return "logs"


@app.route("/delete")
def delete():
    return "delete"


@app.route("/ps")
def ps():
    return "ps"


@app.route("/history")
def history():
    return "history"


@app.route("/archive")
def archive():
    return "archive"


class WebServer:

    def quit(self):
        fns = sorted(dir(self.app))
        for f in fns:
            print(str(f))
        self.app.quit()

    def on_quit(self):
        print("WebServer.on_quit()")

    def __init__(self, server):
        self.server = server

    def execute(self):
        global app
        self.app = app
        app.debug = False
        app.host = "0.0.0.0"
        app.run()
