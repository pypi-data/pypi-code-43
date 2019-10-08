from hashlib import sha256

def hash_file(path:str)->str:
    """Return a deterministic hash for given file.
        path:str, path from where to load the file to hash.
    """
    h  = sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(path, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()