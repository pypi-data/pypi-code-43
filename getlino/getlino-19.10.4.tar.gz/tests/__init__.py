from getlino import SETUP_INFO

from atelier.test import TestCase


class PackagesTests(TestCase):
    def test_01(self):
        self.run_packages_test(SETUP_INFO['packages'])

    def test_developer_mode(self):
        self.run_subprocess(['sudo','getlino','-H env PATH=$PATH','configure','--batch' ,'--db-engine', 'postgresql' ,'--db-port' ,'5432'])
        self.run_subprocess(['sudo','getlino','-H env PATH=$PATH', 'startsite', '--batch', 'noi', 'mysite1', '--dev-repos', '"lino noi xl"'])
