from typing import List, IO, Optional, Type
from mitmproxy import io, http
from mitmproxy.exceptions import FlowReadException

from rikki.mitmproxy.plugin import ProxyDelegate
from rikki.mitmproxy.model import Request, Response
from rikki.mitmproxy.util import filter as filter_requests
from pathlib import Path


class DumpWriter:

    def __init__(self, path: str) -> None:
        self._path: Path = Path(path)

    def write_flows(self, flows: List[http.HTTPFlow]): assert False, f"{self} doesn't implement the method"

    def close(self): pass


class DumpReader:

    # noinspection PyTypeChecker
    def read_from(self, path: str) -> List[http.HTTPFlow]: assert False, f"{self} doesn't implement the method"


class MitmProxyDumpWriter(DumpWriter):

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.__file: IO[bytes] = open(str(self._path.absolute()), "wb")
        self.__writer = io.FlowWriter(self.__file)

    def write_flows(self, flows: List[http.HTTPFlow]):
        for flow in flows:
            self.__writer.add(flow)

    def close(self):
        self.__file.close()


class MitmProxyDumpReader(DumpReader):

    def read_from(self, path: str) -> List[http.HTTPFlow]:
        with open(path, "rb") as dump_file:
            flow_reader = io.FlowReader(dump_file)
            try:
                results: List[http.HTTPFlow] = []
                for flow in flow_reader.stream():
                    results.append(flow)
                return results
            except FlowReadException as e:
                assert False, f"File {path} corrupted"


class DumpWriterConfig:

    def __init__(
            self,
            path: str,
            dump_writer: Type[DumpWriter] = MitmProxyDumpWriter,
            request: Optional[Request] = None,
            response: Optional[Response] = None
    ) -> None:
        self.request: Optional[Request] = request
        self.response: Optional[Response] = response
        self.path: Optional[str] = path
        self.dump_writer: Type[DumpWriter] = dump_writer


class DumpWriterDelegate(ProxyDelegate):

    def __init__(self, config: DumpWriterConfig, recursive: bool = True) -> None:
        super().__init__(recursive=recursive)
        self.__config = config
        self.__flows: List[http.HTTPFlow] = []
        self.writer: DumpWriter = self.__config.dump_writer(path=self.__config.path)

    def request(self, flow: http.HTTPFlow):
        self.__flows.extend(
            filter_requests(
                flows=[flow],
                request=self.__config.request,
                response=self.__config.response
            )
        )

    def shutdown(self):
        self.writer.write_flows(self.__flows)
        self.writer.close()

    def clean_up(self):
        super().clean_up()
