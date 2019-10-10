from .router import Router

def create_app(box_class, router):
    from .application import Application

    class MyApp(Application):
        pass

    MyApp.box_class = box_class
    MyApp.router = router

    return MyApp