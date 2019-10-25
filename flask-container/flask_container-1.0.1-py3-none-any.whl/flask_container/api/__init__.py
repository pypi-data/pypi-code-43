from flask import Blueprint
from flask_restful import Resource, Api, output_json

headers = {'Content-Type': 'application/json'}


bp = Blueprint('api',__name__, url_prefix='/api')
api = Api(bp, catch_all_404s=True)

class Sample(Resource):
    def get(self):
        response = {'data': 'hello from flask Container'}
        return output_json(response, 200, headers)

api.add_resource(Sample, '/sample')