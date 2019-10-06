from .redis_index_atom import RedisIndexAtom

def indexed(prop):
    return RedisIndexAtom(primary_atom=prop)
