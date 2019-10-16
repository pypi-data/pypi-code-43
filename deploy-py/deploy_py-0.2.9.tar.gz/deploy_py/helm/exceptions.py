class HelmUploadError(Exception):
    pass


class HelmRepoNotFoundError(Exception):
    def __init__(self, name, file, choices):
        self.message = f"helm with name '{name}' not found in '{file}; choices are: {', '.join(choices)}"
