import argparse
import os
import signal

import oyaml as yaml

import kamzik3
from kamzik3.snippets.snippetsWidgets import init_qt_app

# Parse arguments from commandline
parser = argparse.ArgumentParser()
parser.add_argument("--chdir", help="Path to active directory",
                    default="./")
parser.add_argument("--conf", help="Path to configuration file in yaml format",
                    default="./examples/conf_dummy_client.yml")
args = parser.parse_args()

# Set active directory
os.chdir(args.chdir)
# Create PyQT5 application
app = init_qt_app()

# Load configuration file
with open(args.conf, "r") as configFile:
    config = yaml.load(configFile, Loader=yaml.Loader)

# Start control loop for clients specified in configuration file
kamzik3.session.start_client_poller_loop()

signal.signal(signal.SIGINT, signal.SIG_DFL)
if "session_window" in config:
    config["session_window"].show()

# Start PyQT5 app loop
app.exec_()

# Close session
kamzik3.session.stop()
