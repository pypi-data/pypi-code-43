class PodNotFoundError(Exception):
    def __init__(self, selectors):
        self.message = f"no pods match given selectors: {selectors}"


class PortNotFoundError(Exception):
    def __init__(self, port_name, ports):
        self. message = f"no port found with name '{port_name}; available ports: {', '.join(p['name'] for p in ports)}"


class ContextNotFoundError(Exception):
    def __init__(self, context_name, file_name):
        self.message = f"context with name {context_name} not found in {file_name}"
