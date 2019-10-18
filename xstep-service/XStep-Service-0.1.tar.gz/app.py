"""
Start the x-step service API server with given port and interface.
"""

from flask import Flask
from flask_restplus import Resource, Api
import logging.config

# Initialize Flask framework
app = Flask(__name__)

# The main function for x-step service
if __name__ == '__main__':
    app.run(debug=True)
