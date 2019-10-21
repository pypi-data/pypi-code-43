# unittest.py
#
# Copyright 2018 Eiichi Inohira
# This software may be modified and distributed under the terms
# of the MIT license
#
# for python 3

"""unittest
"""

import time
from multiprocessing import Process, Queue
import unittest
import http
import xmlrpc.client
import sysconfig

from . import RoIS_HRI, RoIS_Common
from . import Service_Application_IF, Service_Application_Base_example
from . import HRI_Engine_client, HRI_Engine_example
from . import Person_Detection_client, Person_Detection


class TestServericeApplicationIF(unittest.TestCase):
    """TestServericeApplicationIF
    """
    def setUp(self):
        # start the server process
        self.ps = Process(
            target=Service_Application_Base_example.example_sa, args=(8000,))
        self.ps.start()
        time.sleep(0.5)

    def test_IF(self):
        """ test_IF
        """

        q = Queue()
        # start the client process
        pc = Process(target=Service_Application_IF.example_sa_IF,
                     args=("http://127.0.0.1:8000/", q))
        pc.start()

        time.sleep(0.5)

        num_events = 0
        while not q.empty():
            msg = q.get()
            num_events += 1
            # print(msg.message)

        if pc.is_alive():
            pc.terminate()

        return self.assertEqual(num_events, 3)

    def tearDown(self):
        # terminate the server process
        if self.ps.is_alive():
            self.ps.terminate()
            while self.ps.is_alive():
                time.sleep(0.1)


class TestHRIEngineIF(unittest.TestCase):
    """TestHRIEngineIF
    """

    def setUp(self):
        # start the server process
        self.ps = Process(target=HRI_Engine_example.test_engine, args=(8001,))
        self.ps.start()
        time.sleep(0.1)

    def test_IF(self):
        """test_IF
        """

        with xmlrpc.client.ServerProxy("http://127.0.0.1:8001/") as proxy:
            a = HRI_Engine_client.SystemIF(proxy)
            b = HRI_Engine_client.CommandIF(proxy)

            try:
                res = [
                    a.connect(),
                    a.connect(),
                    b.bind(''),
                    a.disconnect(),
                    a.disconnect(),
                    b.bind('')]
                # print(res)
            except xmlrpc.client.ProtocolError as err:
                print(err)

        return self.assertEqual(res,
                                [
                                    RoIS_HRI.ReturnCode_t.OK,
                                    RoIS_HRI.ReturnCode_t.ERROR,
                                    RoIS_HRI.ReturnCode_t.OK,
                                    RoIS_HRI.ReturnCode_t.OK,
                                    RoIS_HRI.ReturnCode_t.ERROR,
                                    RoIS_HRI.ReturnCode_t.OK])

    def tearDown(self):
        # terminate the server process
        if self.ps.is_alive():
            self.ps.terminate()
            time.sleep(0.1)


class TestHRIEngineIF_integrated(unittest.TestCase):
    """TestHRIEngineIF_integrated
    """
    def setUp(self):
        # start the server process
        self.ps = Process(target=HRI_Engine_example.test_engine, args=(8002,))
        self.ps.start()
        time.sleep(0.1)

    def test_IF(self):
        """test_IF
        """

        try:
            a = HRI_Engine_client.IF("http://127.0.0.1:8002/")
            res = [
                a.connect(),
                a.connect(),
                a.get_profile(""),
                a.get_error_detail("0", ""),

                a.search(""),
                a.bind(""),
                a.bind_any(""),
                a.release(""),
                a.get_parameter(""),
                a.set_parameter("", ""),
                a.execute(""),
                a.get_command_result("", ""),

                a.query("", ""),

                a.subscribe("", ""),
                a.unsubscribe(""),
                a.get_event_detail("", ""),

                a.disconnect(),
                a.disconnect(),
                a.bind('')]
            # print(res)
        except xmlrpc.client.ProtocolError as err:
            print(err)

        return self.assertEqual(res,
                                [RoIS_HRI.ReturnCode_t.OK,
                                 RoIS_HRI.ReturnCode_t.ERROR,
                                 (RoIS_HRI.ReturnCode_t.OK, "Unsupported"),
                                 (RoIS_HRI.ReturnCode_t.OK, "None"),

                                 (RoIS_HRI.ReturnCode_t.OK, ["None"]),
                                 RoIS_HRI.ReturnCode_t.OK,
                                 (RoIS_HRI.ReturnCode_t.OK, ["None"]),
                                 RoIS_HRI.ReturnCode_t.OK,
                                 (RoIS_HRI.ReturnCode_t.OK, ["None"]),
                                 (RoIS_HRI.ReturnCode_t.OK, "0"),
                                 RoIS_HRI.ReturnCode_t.OK,
                                 (RoIS_HRI.ReturnCode_t.OK, ["None"]),

                                 (RoIS_HRI.ReturnCode_t.OK, ["None"]),

                                 (RoIS_HRI.ReturnCode_t.OK, "0"),
                                 RoIS_HRI.ReturnCode_t.OK,
                                 (RoIS_HRI.ReturnCode_t.OK, ["None"]),

                                 RoIS_HRI.ReturnCode_t.OK,
                                 RoIS_HRI.ReturnCode_t.ERROR,
                                 RoIS_HRI.ReturnCode_t.OK])

    def tearDown(self):
        # terminate the server process
        if self.ps.is_alive():
            self.ps.terminate()
            time.sleep(0.1)


class TestPD(unittest.TestCase):
    """TestPD
    """

    def setUp(self):
        # start the server process
        self.ps = Process(target=Person_Detection.example_pd, args=(8003,))
        self.ps.start()
        time.sleep(0.5)

    def test_IF(self):
        """test_IF
        """
        a = Person_Detection_client.Person_Detection_Client("http://127.0.0.1:8003/")
        try:
            res = [
                a.start(),
                a.stop(),
                a.suspend(),
                a.resume(),
                a.component_status(),
                len(a.events)]
        except xmlrpc.client.ProtocolError as err:
            print(err)

        a.__del__()

        return self.assertEqual(res,
                                [
                                    RoIS_HRI.ReturnCode_t.OK,
                                    RoIS_HRI.ReturnCode_t.OK,
                                    RoIS_HRI.ReturnCode_t.OK,
                                    RoIS_HRI.ReturnCode_t.OK,
                                    (RoIS_HRI.ReturnCode_t.OK, RoIS_Common.Component_Status.UNINITIALIZED),
                                    2])

    def tearDown(self):
        # terminate the server process
        if self.ps.is_alive():
            self.ps.terminate()
            time.sleep(0.1)


if __name__ == '__main__':
    print("python", sysconfig.get_python_version())
    print("platform:", sysconfig.get_platform())
    unittest.main()
