def resolvers():
    """Return all supported resolvers, ordered by precedence"""
    from . import gradle, cbng_web
    return [cbng_web.CbngWebResolver, gradle.GradleResolver]
