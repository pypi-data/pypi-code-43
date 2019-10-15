import os
import sys
import importlib.util
from flask import Flask, request
import click

@click.command()
@click.option('--module', '-m', 'module_path' , required=True, help='path to the module containing the function')
@click.option('--function', '-f', required=True, help='name of the function as you wrote in the code')
@click.option('--endpoint', '-e', help='name of the endpoint to use if differente from the function name')
@click.option('--port', '-p', default=5000, help='port number to use in the server')
@click.option('--http-methods', '-h', 'http_methods', type=click.Choice(['GET', 'POST']), multiple=True, default=['GET','POST'], help='http methods that server will be answering')
def main(module_path, function, endpoint, port, http_methods):
    """ Serve functions using Flask """
    # if no endpoint was provided, we use the function name instead
    if endpoint is None:
        endpoint = function
    # dinamically import the module and the function to run
    spec = importlib.util.spec_from_file_location('cloud_function', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, function)
    # serve the code in the specified route
    print(' * Serving ' + function + '@' + module_path + ' in http://localhost:'+ str(port) + '/' + endpoint)
    app = Flask('gcpfemu')
    @app.route('/' + endpoint, methods=list(http_methods))
    def index():
        return fn(request)
    app.run(port=port, debug=True)

if __name__ == '__main__':
    main()
