#!python
import flask
import multiprocess as mp
import pandas as pd
import requests
from time import sleep
from IPython.core.display import HTML

from ..db import get_db
from ...filesystem.filepath import Filepath
from ...queues.logq import Logq
from ...queues.eventq import Eventq
from ...queues.taskq import Taskq

import logging
log = logging.getLogger()

app = flask.Flask(__name__)

# web pages #####################################################################

@app.route('/shutdown')
def shutdown():
    """ shutdown flask from inside a request """
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Server shutting down"

@app.route("/")
def status():
    """ render html page with tables showing task summary, task list, queues """
    db = get_db()
    tables = []
    titles = []

    # task summary
    status = ["pending", "waiting", "ready",
              "loading", "running", "saving", "completed",
              "failed", "failed_missing", "failed_upstream", "total"]
    task = db.taskview()
    summary = db.taskview().groupby("status")[["url"]].count().T
    summary.columns.name = None
    for s in status:
        if s not in summary.columns:
            summary[s] = 0
    summary["total"] = summary.sum(axis=1)
    tables.append(summary[status].to_html(index=False, table_id="summary"))
    titles.append("task count by status")

    # task list
    waits = db((db.task.status == "waiting")).select(db.waiting.ALL)
    if len(waits)>0:
        waits = pd.DataFrame.from_dict(waits.as_dict(), orient="index")
        waits = waits.drop(["id"], axis=1)
        # abbreviate to name
        waits = waits.groupby("task").apply(lambda x: ", ".join([Filepath(f).name for f in x.awaiting]))
        task["awaiting"] = waits
    else:
        task["awaiting"] = ""
    task = task.reset_index().fillna("")
    # view path as shorter and excludes username/password
    task.url = task.url.apply(lambda x: Filepath(x).path)
    task = task.rename(columns=dict(url="path"))
    tables.append(task.to_html(index=False, table_id="task"))
    titles.append("task list")

    # queues
    tables.append(queues())
    titles.append("queues")

    db.close()
    return flask.render_template('view.html',tables=tables, titles=titles)

# control functions  #########################################################################

def restart():
    """ stop and start flask """
    stop_flask()
    start_flask()

def start_flask():
    """ start flask in background process """
    log.info("starting flask")
    p = mp.Process(target=start_flask_process)
    p.start()

def start_flask_process():
    """ process target for start_flask"""
    log.info(f"starting flask pid={mp.current_process().pid}")
    app.run(debug=False)

def stop_flask():
    """ request and wait for shutdown """
    log.info("shutting down flask")

    # request
    try:
        r = requests.get("http://localhost:5000/shutdown")
        if r.status_code != 200:
            log.warning(f"flask shutdown failed with status_code={r.status_code}")
            return
    except requests.exceptions.ConnectionError:
        # flask not running
        return

   # wait
    while True:
        try:
            r = requests.get("http://localhost:5000")
        except:
            break
        log.info("waiting for flask to shutdown")
        sleep(1)

def queues():
    """ display queues in notebook """
    taskq = Taskq()
    eventq = Eventq()
    logq = Logq()
    queues = [taskq, eventq, logq]
    listeners = " ".join([f"{t.name}={t.queue.method.consumer_count}" for t in queues])
    messages = " ".join([f"{t.name}={t.queue.method.message_count}" for t in queues])
    logs = "<br>".join(logq.list())

    return HTML(f"listeners: {listeners}<br>messages: {messages}<br><h2>logs</h2>{logs}")

if __name__ == "__main__":
    """ for testing. normally run in background process """
    app.run(debug=True)
