import pkg_resources

from .agent import Agent, AgentError

version = pkg_resources.require("scopeagent")[0].version

name = "scopeagent"
global_agent = None
