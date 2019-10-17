from auger.api.mparts.deploy import ModelDeploy
from auger.api.mparts.predict import ModelPredict


class Model(object):
    """Auger Cloud Model(s) management."""

    def __init__(self, ctx, project):
        super(Model, self).__init__()
        self.project = project
        self.ctx = ctx

    def deploy(self, model_id, locally=False):
        ModelDeploy(self.ctx, self.project).execute(model_id, locally)

    def predict(self, filename, model_id, threshold=None, locally=False):
        ModelPredict(self.ctx).execute(filename, model_id, threshold, locally)
