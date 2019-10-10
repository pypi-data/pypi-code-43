#!/usr/bin/env python
from techela.app import app
import threading
import webbrowser

port = 5543
url = f"http://127.0.0.1:{port}"


def open_course():
    try:
        wb = webbrowser.get('chrome')
        wb.open(url)
    except:
        webbrowser.open(url)


threading.Timer(1.25, open_course).start()
app.run(port=port, debug=True, use_reloader=False)
