import oyaml as yaml
from yaml import Loader

import kamzik3
from kamzik3.snippets.snippetsWidgets import init_qt_app

app = init_qt_app()

with open("conf_dummy_client.yml", "r") as configFile:
    config = yaml.load(configFile, Loader=Loader)

kamzik3.session.start_client_poller_loop()

w = config["session_window"]
w.show()
app.exec_()

kamzik3.session.stop()
