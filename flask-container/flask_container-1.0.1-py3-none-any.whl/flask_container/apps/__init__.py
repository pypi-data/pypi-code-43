from flask import Blueprint
from flask_restful import Resource, Api, output_json

headers = {'Content-Type': 'application/json'}


bp = Blueprint('apps',__name__, url_prefix='/apps')
api = Api(bp, catch_all_404s=True)

def app_loader():
    # TODO: load apps
    pass