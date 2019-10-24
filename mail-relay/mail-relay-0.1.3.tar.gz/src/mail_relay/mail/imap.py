import imaplib


class GetIMAPConnetion(object):
    def __init__(self, config):
        self.imap_config = config
        self.imap_conn = None

    def __enter__(self):
        self.imap_conn = imaplib.IMAP4(self.imap_config.host, self.imap_config.port)
        # do loging
        return self.imap_conn

    def __exit__(self, type_, value, traceback):
        self.imap_conn.close()
