from inspect import isclass, signature

from pyramid_services import Interface


class ServiceInjector:
    """
    Holds an interface and service name to be passed to `request.find_service`.
    """

    def __init__(self, iface=Interface, name=""):
        if isinstance(iface, str):
            iface = Interface
            name  = iface
        self.iface = iface
        self.name  = name


class ServiceViewMapper:
    """
    View mapper for use with pyramid_services.

    This uses the annotations on a given view to inject services. Services
    found by interface only can use the interface directly, for example:

        @view_config(route_name="home", renderer="json")
        def home(request, login_svc: ILoginService):
            token = login_svc.create_token_for_login(name)
            return {"access_token": token}

    Named services are injected using a ServiceInjector:

        @view_config(route_name="users", renderer="json")
        def users(request, db: ServiceInjector(name="db")):
            users = db.query(User)
            return {"users": users}

    The ServiceInjector class can be used as a shortcut for this:

        @view_config(route_name="users", renderer="json")
        def users(request, db: ServiceInjector):
            users = db.query(User)
            return {"users": users}
    """

    def __init__(self, **kw):
        pass

    def __call__(self, view):
        parameters = signature(view).parameters

        view_callable = view.__init__ if isclass(view) else view
        annotations = {
            name: eval(annotation, view_callable.__globals__)
            for (name, annotation)
            in view_callable.__annotations__.items()
        }

        services = []
        for parameter, annotation in annotations.items():
            if parameter in ("request", "context", "return"):
                continue
            if annotation == ServiceInjector:
                services.append((parameter, ServiceInjector(name=parameter)))
            elif isinstance(annotation, ServiceInjector):
                services.append((parameter, annotation))
            else:
                services.append((parameter, ServiceInjector(annotation)))

        def wrapped_view(context, request):
            kwargs = {
                name: request.find_service(iface=injector.iface, name=injector.name)
                for name, injector in services
            }
            if "context" in parameters:
                kwargs["context"] = context
            if "request" in parameters:
                kwargs["request"] = request
            if isclass(view):
                return view(**kwargs)()
            return view(**kwargs)

        return wrapped_view
