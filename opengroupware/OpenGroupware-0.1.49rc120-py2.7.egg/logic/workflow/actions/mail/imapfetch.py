#
# Copyright (c) 2018
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
import zipfile
import imaplib
from email.Parser import Parser
from email.generator import Generator
from coils.foundation import BLOBManager
from .command import MailAction


class IMAPFetchMailAction(MailAction):
    __domain__ = "action"
    __operation__ = "imap-fetch-mail"
    __aliases__ = ['imapFetchMailAction', 'imapFetchMail', ]

    def __init__(self):
        MailAction.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/zip'

    def do_action(self):

        zfile = zipfile.ZipFile(
            self.wfile, 'a', compression=zipfile.ZIP_DEFLATED,
        )

        M = None
        if self._imap4_use_ssl:
            M = imaplib.IMAP4_SSL(self._imap_hostname)
            self.log_message(
                'Connected to IMAP host "{0}"'.format(self._imap_hostname, ),
                category='debug',
            )
        else:
            # connect to non SSL IMAP server
            pass  # TODO: implement

        M.login(self._imap_username, self._imap_password, )
        M.select(self._imap_mailbox)
        self.log_message(
            'Selected mailbox "{0}"'.format(self._imap_mailbox, ),
            category='debug',
        )
        typ, msg_ids = M.search(None, self._imap_search_string)

        self.gong()

        counter = 0
        message_index = dict()
        mailbox_ids = list()
        message_ids = msg_ids[0].split()

        self.log_message(
            'Search returned {0} messages'.format(len(message_ids), ),
            category='debug',
        )
        # Implement fetch limit
        if self._fetch_limit:
            self.log_message(
                'Truncating search results to {0} messages due to limit'
                .format(self._fetch_limit, ), category='debug',
            )
            message_ids = message_ids[:self._fetch_limit]

        for msg_id in message_ids:

            counter += 1
            if not (counter % 25):
                # gong every 25 messages - messages can be big
                self.gong()

            typ, data = M.fetch(msg_id, '(RFC822)')
            message = Parser().parsestr(data[0][1])
            message_id = message.get('message-id')
            mailbox_ids.append(msg_id)
            if message_id in message_index:
                self.log_message(
                    'Skipping duplicate Message-ID: "{0}"'.format(message_id),
                    category='debug',
                )
                continue
            # record the msg_id to support delete-after-fetch
            message_index[message_id] = msg_id

            sfile = BLOBManager.ScratchFile(require_named_file=True, )
            g = Generator(sfile, mangle_from_=False, maxheaderlen=255, )
            g.flatten(message)
            sfile.flush()
            sfile.seek(0)
            message = None
            zfile.write(sfile.name, arcname='{0}.mbox'.format(message_id, ))
            BLOBManager.Close(sfile)
            self.log_message(
                'Retrieved message "{0}"'.format(message_id, ),
                category='debug',
            )
        zfile.close()
        self.wfile.flush()
        self.log_message('ZIP document closed and flushed', category='debug', )
        self.log_message(
            'retrieved {0} messages from mailbox'.format(counter, ),
            category='debug',
        )

        message_ids = None
        self.gong()

        if self._do_post_delete:
            counter = 0
            for message_id, msg_id in message_index.items():

                counter += 1
                if not (counter % 150):
                    # gong every 150 messages
                    self.gong()

                M.store(msg_id, '+FLAGS', '\\Deleted', )
                self.log_message(
                    'Deleted message "{0}" ({1})'.format(message_id, msg_id, ),
                    category='debug',
                )
                if msg_id in mailbox_ids:
                    mailbox_ids.remove(msg_id)

            self.gong()

            if mailbox_ids:
                self.log_message(
                    '{0} messages remain in mailbox due to duplication'
                    .format(len(mailbox_ids), ),
                    category='info',
                )
                counter = 0
                for mailbox_id in mailbox_ids:

                    counter += 1
                    if not (counter % 150):
                        # gong every 150 messages
                        self.gong()

                    try:
                        M.store(mailbox_id, '+FLAGS', '\\Deleted', )
                    except Exception as exc:
                        self.log_message(
                            'storing flag on mailbox object {0} failed: {1}'
                            .format(mailbox_id, exc, ),
                            category='warn',
                        )
                self.log_message(
                    'Duplicated messages deleted', category='info',
                )
            self.log_message('Performing expunge', category='debug', )

            self.gong()

            M.expunge()

            self.gong()

        M.shutdown()
        self.log_message('IMAP connection closed', category='debug', )

    def parse_action_parameters(self):

        self._imap4_use_ssl = True if self.action_parameters.get(
            'useSSL', 'YES'
        ).upper() == 'YES' else False

        self._imap_hostname = self.process_label_substitutions(
            self.action_parameters.get(
                'imapHostName', '127.0.0.1'
            )
        )

        self._imap_username = self.process_label_substitutions(
            self.action_parameters.get(
                'imapUsername', 'fred123'
            )
        )

        self._imap_password = self.process_label_substitutions(
            self.action_parameters.get(
                'imapPassword', 'fred123'
            )
        )

        self._imap_mailbox = self.process_label_substitutions(
            self.action_parameters.get(
                'imapMailBox', 'INBOX',
            )
        )

        """  IMAP SEARCH CRITERIA
        allMsgs = "ALL"
        answered = "ANSWERED"
        onDate = "SENTON 05-Mar-2007"
        betweenDates = "SENTSINCE 01-Mar-2007 SENTBEFORE 05-Mar-2007"
        complexSearch1 = "UNANSWERED SENTSINCE 04-Mar-2007 Subject \"Problem\""
        bodySearch = "BODY \"problem solved\""
        orSearch = "OR SUBJECT Help SUBJECT Question"
        fromSearch = "FROM yahoo.com"
        johnSearch = "FROM John"
        recentSearch = "RECENT"
        notRecentSearch = "NOT RECENT"
        oldSearch = "OLD"
        markedForDeleteSearch = "DELETED"
        headerSearch = "HEADER DomainKey-Signature paypal.com"
        headerExistsSearch = "HEADER DomainKey-Signature \"\""
        newSearch = "NEW"
        sizeLargerSearch = "LARGER 500000"
        seenSearch = "SEEN"
        notSeenSearch = "NOT SEEN"
        toSearch = "TO support@chilkatsoft.com"
        toSearch2 = "HEADER TO support@chilkatsoft.com"
        smallerSearch = "SMALLER 30000"
        fullSubstringSearch = "TEXT \"Zip Component\""
        """
        self._imap_search_string = self.process_label_substitutions(
            self.action_parameters.get(
                'imapSearchCriteria', 'ALL',
            )
        )

        self._do_post_delete = True if self.action_parameters.get(
            'doPostFetchDelete', 'NO'
        ).upper() == 'YES' else False

        self._fetch_limit = int(self.action_parameters.get('fetchLimit', '0'))

    def do_epilogue(self):
        pass
