from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class Hash:
    def __init__(self, algo="sha512_224"):
        self.algo = algo.upper()

        if not hasattr(hashes, self.algo):
            raise ValueError(f"Unknown <algo> ({self.algo})")

    def file(self, file_path):
        digest = hashes.Hash(getattr(hashes, self.algo)(), backend=default_backend())

        with open(file_path, "rb") as file_stream:
            digest.update(file_stream.read())

        return digest.finalize().hex()

    def data(self, data):
        if not isinstance(data, bytes):
            raise ValueError(f"<data> must be {bytes}, {type(data)}, given.")

        digest = hashes.Hash(getattr(hashes, self.algo)(), backend=default_backend())
        digest.update(data)

        return digest.finalize().hex()
