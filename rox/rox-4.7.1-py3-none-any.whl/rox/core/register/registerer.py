from rox.core.entities.variant import Variant


class Registerer:
    def __init__(self, flag_repository):
        self.flag_repository = flag_repository
        self.namespaces = set()

    def register_instance(self, container, ns):
        if ns is None:
            raise TypeError('A namespace cannot be null')

        if ns in self.namespaces:
            raise ValueError('A container with the given namespace (%s) has already been registered' % ns)

        self.namespaces.add(ns)

        for name, value in vars(container).items():
            if isinstance(value, Variant):
                self.flag_repository.add_flag(value, name if ns == '' else '%s.%s' % (ns, name))
