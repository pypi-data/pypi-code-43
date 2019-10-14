"""
Sets Access-Control-Allow-Origin header to allow cross-origin resource sharing.

Usage:
    service = Service()
    service.add_filter(CORS(origin='*'))

    OR just

    service = Service()
    service.add_filter(CORS)

See:
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin
    https://auth0.com/blog/cors-tutorial-a-guide-to-cross-origin-resource-sharing/
"""
class CORS:
    def __init__(self, origin='*'):
        self.origin = origin

    def __call__(self, req, res, ctx, next):
        next(req, res, ctx)

        res.set_header('Access-Control-Allow-Origin', self.origin)