from os import environ


class Environments:
    @classmethod
    def is_present(cls, env_name, return_value=False):
        values = None

        if hasattr(cls, env_name):
            to_check = getattr(cls, env_name)
            if isinstance(to_check, list):
                values = ((x, environ[x]) for x in to_check if x in environ)
            elif to_check in environ:
                values = environ[to_check]
            else:
                values = None
        elif env_name in environ:
            values = environ[env_name]
        else:
            values = None

        if return_value and not values:
            return None
        if return_value and isinstance(values, set):
            return values[0][-1]
        if return_value:
            return values
        if values:
            return True

        return False
