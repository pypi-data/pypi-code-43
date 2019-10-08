import threading

from behave.__main__ import run_behave
from behave.configuration import Configuration
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.tools.main import run as run_mitmproxy, cmdline

from rikki.mitmproxy.plugin import ProxyPlugin


class RikkiConfiguration:

    def __init__(self) -> None:
        super().__init__()
        self.proxy_plugin = ProxyPlugin()


config = RikkiConfiguration()


class ExtendedDumpMaster(DumpMaster):

    def __init__(
            self,
            options: options.Options,
            with_termlog=False,
            with_dumper=True
    ) -> None:
        super().__init__(options, with_termlog, with_dumper)
        self.addons.add(*[config.proxy_plugin])
        options.flow_detail = 0
        config.proxy_plugin.proxy = self


class RikkiTestRunner:

    def __init__(self, plugin: ProxyPlugin = ProxyPlugin()) -> None:
        super().__init__()
        self.proxy_plugin = plugin

    def run(self, *args):
        config.proxy_plugin = self.proxy_plugin
        self._configure(args)

    def _configure(self, args):
        behave_thread = threading.Thread(target=self._start_behave, args=args)
        behave_thread.start()
        run_mitmproxy(ExtendedDumpMaster, cmdline.mitmdump, None, {})

    def _start_behave(self, args=None):
        configuration = Configuration(
            command_args=args,
            stdout_capture=False,
            stderr_capture=False,
            log_capture=False,
            junit=True
        )
        configuration.mitm_plugin = config.proxy_plugin
        configuration.proxy = config.proxy_plugin
        run_behave(configuration)
