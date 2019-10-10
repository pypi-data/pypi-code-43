class DeploymentFailedError(Exception):
    def __init__(self, message):
        self.message = f"deployment failed: {message}"
