import os


class UtilsTest:

    @staticmethod
    def get_file_running_app(self):
        file_running_app = os.path.join(os.path.dirname(__file__),"test","res","running_app.json")
        return file_running_app

    @staticmethod
    def get_file_empty_cluster(self):
        file_empty_cluster = os.path.join(os.path.dirname(__file__), "test","res", "empty_cluster.json")
        return file_empty_cluster
