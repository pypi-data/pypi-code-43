import mock
import unittest

from dq import email


class TestEmail(unittest.TestCase):

    @mock.patch('emails.Message.send')
    def test_send_email(self, mock_send):
        resp = mock.MagicMock()
        resp.success = True
        mock_send.return_value = resp
        assert email.send_email(
            'unittest.to@danqing.io',
            'Unit test',
            'This is a test',
            'Danqing Liu',
            'unittest.from@danqing.io',
        )
        mock_send.assert_called_with(
            to='unittest.to@danqing.io',
            smtp={'user': 'danqing'},
        )

    @mock.patch('dq.email.error')
    @mock.patch('emails.Message.send')
    def test_send_email_error(self, mock_send, mock_error):
        resp_error = mock.MagicMock()
        resp_error.strerror = 'not found'
        resp = mock.MagicMock()
        resp.error = resp_error
        resp.success = False
        mock_send.return_value = resp
        assert not email.send_email(
            'unittest.to@danqing.io',
            'Unit test',
            'This is a test',
            'Danqing Liu',
            'unittest.from@danqing.io',
        )
        mock_send.assert_called_with(
            to='unittest.to@danqing.io',
            smtp={'user': 'danqing'},
        )
        mock_error.assert_called()
