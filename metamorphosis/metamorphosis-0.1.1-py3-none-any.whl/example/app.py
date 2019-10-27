import logging

import graphene as g
import yaml

from flask import Flask, Response
from flask_graphql import GraphQLView

from metamorphosis import ServiceWebMutations, ServiceWebQuery
from .service import forms_service, FormsQuery


app = Flask(__name__)
app.secret_key = app.config['SECRET_KEY'] = 'foobar'
app.config['SVC_WEB_TOPIC'] = 'metamorphosis.services'

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('kafka').setLevel(logging.WARNING)

forms_service.init_app(app)

forms_service.logger.info("Forms Service initted. Adding mutations and queries")

@app.route('/consumer_config')
def consumer_config():
    return Response(yaml.dump(forms_service.default_consumer_config()), mimetype='text/yaml')


class FormServiceMutations(ServiceWebMutations, forms_service.Mutations):
    pass


class FormServiceQueries(ServiceWebQuery, FormsQuery):
    pass


schema = g.Schema(query=FormServiceQueries, mutation=FormServiceMutations)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))