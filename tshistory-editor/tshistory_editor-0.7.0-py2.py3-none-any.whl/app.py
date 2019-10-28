from flask import Flask

from sqlalchemy import create_engine

from tshistory_editor.editor import editor


app = Flask('tseditor')


def kickoff(host, port, dburi):
    engine = create_engine(dburi)
    editor(app, engine)
    app.run(host=host, port=port, threaded=False)
