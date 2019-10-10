import unittest

from zaach.oop import borg


class BorgTests(unittest.TestCase):

    def test_assimilation(self):
        drone = borg.Borg()
        drone.hello_world = "We are the Borg"

        locutus = borg.Borg()
        self.assertEqual(locutus.hello_world, "We are the Borg")


if __name__ == '__main__':
    unittest.main()
