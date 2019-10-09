import functools
import re

try:
    import newrelic.agent as agent

    def set_transaction_name(func):
        @functools.wraps(func)
        def inner(request, resource_path):
            agent.set_transaction_name(
                get_transaction_name_path(resource_path),
                'Python/WebFramework/Controller'
            )
            return func(request, resource_path)
        return inner

except ImportError:
    def set_transaction_name(func):
        return func


def get_transaction_name_path(resource_path):
    """
    Takes a resource path and removes its last fragment if and only if that fragment is just digits
    e.g.
        'bars/foo' => 'bars/foo'
        'bars/bar/9' => 'bars/bar'
        'bars/19229' => 'bars'
        'bars/magic8ball' => 'bars/magic8ball'
    """
    path_fragments = resource_path.split('/')

    if re.match(r'^\d+$', path_fragments[-1]):
        return '/'.join(path_fragments[:-1])
    else:
        return resource_path
