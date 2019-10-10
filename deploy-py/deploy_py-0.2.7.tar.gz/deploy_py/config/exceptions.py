class DeploymentNotFoundError(Exception):
    def __init__(self, name):
        self.message = f"no deployment config found for: {name}"
