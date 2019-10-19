import pickle
import pytest
import pandas as pd
from multiprocessing import Process
from time import sleep

from pipemaker.utils.dotdict import dotdict, autodict
from pipemaker.filesystem.filepath import Filepath
from pipemaker.queues.rabbitq import Rabbitq
from pipemaker.utils.defaultlog import log


def test_dotdict():
    """ test create, pickle, unpickle, get """
    dt = dotdict()
    dt.a = 123
    dt.b = "hello"

    # pickle and unpickle
    dt = pickle.loads(pickle.dumps(dt))

    # check resultsa
    assert isinstance(dt, dotdict)
    assert dt.a == 123
    assert dt.b == "hello"

def test_autodict():
    """ test create, pickle, unpickle, get """
    dt = autodict()
    dt.a = 123
    dt.b = "hello"
    dt.c.d = "goodbye"

    # pickle and unpickle
    dt = pickle.loads(pickle.dumps(dt))

    # check results
    assert isinstance(dt, autodict)
    assert dt.a == 123
    assert dt.b == "hello"
    assert dt.c.d == "goodbye"
    assert isinstance(dt.c, autodict)

@pytest.mark.parametrize("fs1", ["s3://registr1"])
@pytest.mark.parametrize("ext", [".pkl", ".xlsx"])
def test_filepath(fs1, ext, request):
    """ test exists, save, load, remove """

    # setup. done here rather than fixture to enable multiprocessing
    temp_fp = Filepath(f"{fs1}/temp/{request.function.__name__}")
    temp_fp.makedirs(recreate=True)

    # tests
    fp = Filepath(f"{temp_fp.url}/file1{ext}")
    assert fp.exists() == False
    value = pd.DataFrame([12])
    fp.save(value)
    assert fp.exists()
    loaded = fp.load()
    assert loaded.equals(value)
    fp.remove()
    assert fp.exists() == False

def stop_consuming(delay=2):
    log.info(f"stopping after {delay} seconds")
    sleep(delay)
    q = Rabbitq()
    q.delete()

def test_rabbitq(caplog):

    # reset queue
    q = Rabbitq()
    q.delete()

    # put messages on queue
    q = Rabbitq()
    q.put("hello")
    q.put("again")

    # list messages
    q = Rabbitq()
    assert q.list()==["hello", "again"]

    # listen for messages
    caplog.clear()
    p = Process(target=stop_consuming)
    p.start()
    q.listen()
    log.info(caplog.messages)
    expected = ["start listening", "hello", "again", "stop listening"]
    for message, expected in zip(caplog.messages, expected):
        assert message.startswith(expected)