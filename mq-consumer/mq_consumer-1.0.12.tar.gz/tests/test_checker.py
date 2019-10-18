from mq_consumer.checkers import MQChecker
from mq_consumer.connectors import Connector

from tests.test_connection_params import connection_parameters


class TestChecker(MQChecker):
    def __init__(self):
        connector = Connector(
            connection_parameters,
            'exchange',
            'test',
        )
        super().__init__(connector)


def run():
    print(TestChecker().get_message_count())
    print(TestChecker().get_consumer_count())


if __name__ == '__main__':
    run()
