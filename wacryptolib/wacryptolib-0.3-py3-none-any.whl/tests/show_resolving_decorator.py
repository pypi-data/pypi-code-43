
import wrapt

@wrapt.decorator
def inject_session(wrapped, instance, args, kwargs):
    def resolver(session, **kwargs):
        all_kwargs = dict(session=session, **kwargs)
        if not all_kwargs["session"]:
            all_kwargs["session"] = "<SESSION>"
        return all_kwargs
    return wrapped(**resolver(*args, **kwargs))

@inject_session
def myfunc(session):
    return session

@inject_session
def myfunc2(a, b, session):
    return session

@inject_session
def myfunc3(a, b, session=None):
    return session

@inject_session
def myfunc4(a, b, *session):
    return session

@inject_session
def myfunc5(a, b, *args, session=None, **kwargs):
    return session

@inject_session
def myfunc6(a, b, *args, **session):
    return session


if __name__ == "__main__":

    assert myfunc(None) == myfunc(session=None) == "<SESSION>"
    assert myfunc("<stuff>") == myfunc(session="<stuff>") == "<stuff>"

    assert myfunc2(1, 2) == "<SESSION>"  # TypeError: resolver() takes 1 positional argument but 2 were given

    assert myfunc3(1, 2, session="<stuff>") == "<stuff>"  # TypeError: resolver() takes 1 positional argument but 2 were given
