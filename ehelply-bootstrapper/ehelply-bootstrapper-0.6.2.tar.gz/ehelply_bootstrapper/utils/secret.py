class SecretManager:
    def __init__(self) -> None:
        self.secrets = []

    def add(self, secret: str):
        self.secrets.append(secret)

    def remove(self, secret: str):
        self.secrets.remove(secret)

    def exists(self, secret: str):
        return secret in self.secrets
