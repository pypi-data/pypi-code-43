from datetime import date

import janis_core as j
from janis_unix.tools.echo import Echo


class HelloWorkflow(j.Workflow):
    def constructor(self):
        self.input("inp", j.String(optional=True), default="Hello, world!")
        self.step("hello", Echo(inp=self.inp))
        self.output("out", source=self.hello)

    def id(self):
        return "hello"

    def friendly_name(self):
        return "Hello, World!"

    @staticmethod
    def tool_module():
        return "unix"

    def bind_metadata(self):

        self.metadata.version = "v1.0.0"
        self.metadata.contributors = ["Michael Franklin"]
        self.metadata.dateUpdated = date(2019, 8, 12)

        self.metadata.documentation = """\
This is the 'Hello, world' equivalent workflow that uses the Echo unix
tool to log "Hello, World!" to the console, and collects the result.

This is designed to be the first example that you can run with janis, ie:
    
``janis run hello``
"""


if __name__ == "__main__":
    print(HelloWorkflow().translate("cwl"))
