"""
An example file showing how to start the webgeodyn server
"""
import os.path
import webgeodyn.server
import webgeodyn.models


def run():
    """
    Runs the webgeodyn example
    """
    # Initialise the list of the models
    models = webgeodyn.models.Models()

    # Load a model into the list of models (several can be loaded at once)
    # Syntax: models.loadModel('/path/to/the/model/directory', "Name of the model", "Format of the model")
    # Example for CHAOS:
    models.loadModel(os.path.join(os.path.dirname(__file__), 'example_data', './CHAOS-6-x4'), 'CHAOS-6-x4 model', 'CHAOS')
    # Example for current pygeodyn computation:
    home_dir = os.path.expanduser('~')
    pygeodyn_dir = os.path.join(home_dir, 'pygeodyn_results', 'Current_computation')
    if(os.path.isfile(os.path.join(pygeodyn_dir, 'Current_computation.hdf5'))):
        models.loadModel(os.path.join(home_dir, 'pygeodyn_results', 'Current_computation'), 'Current pygeodyn computation', 'pygeodyn_hdf5')

    # Start the server with the loaded models
    webgeodyn.server.startServer(models)


if __name__ == "__main__":
    run()
