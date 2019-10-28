from abc import abstractmethod


class P4TargetDriver(object):

    def __init__(self):
        pass

    @abstractmethod
    def load_config(self):
        pass

    @abstractmethod
    def get_config(self):
        pass

    @abstractmethod
    def write_table_entry(self):
        pass

    @abstractmethod
    def delete_table_entry(self):
        pass

    @abstractmethod
    def read_table_entries(self):
        pass