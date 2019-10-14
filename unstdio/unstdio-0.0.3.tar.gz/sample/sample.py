from unstdio.unstdio import Unstdio
from unstdio.handlers import Out
from unstdio.formats import DictFormatter
import io

with Unstdio(stdout=Out(frmt=DictFormatter())) as unstdio:
    print("{Hello World!}")  # out to Unstdio instance
print(isinstance(unstdio.stdout, io.StringIO))
print(unstdio.stdout.getvalue())  # out to system stdout
