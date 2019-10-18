from masonite.provider import ServiceProvider

from .Javascript import Javascript


class JavascriptProvider(ServiceProvider):
    """Bind Javascript class into the Service Container."""

    wsgi = True

    def boot(self):
        pass

    def register(self):
        self.app.bind("Javascript", Javascript)

