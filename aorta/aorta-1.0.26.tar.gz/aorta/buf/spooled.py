import glob
import logging
import os
import tempfile

import proton

import aorta.lib.timezone
from .base import BaseBuffer
from ..const import ANNOTATE_NBF


class SpooledBuffer(BaseBuffer):
    """A :class:`BaseBuffer` implementation that relies on the local
    filesystem to ensure that messages are not lost.

    TODO: This is a very simple and naieve implementation. Optimizations
    regarding its disk-IO are necessary.

    TODO: The persisting/loading of messages in their various states
    should be abstracted to a proper object model.
    """
    SpoolNotAvailable = type('SpoolNotAvailable', (RuntimeError,), {})

    @property
    def queued(self):
        return len(self)

    @property
    def deliveries(self):
        return len(self._list_deliveries())

    @property
    def failed(self):
        return len(list(glob.glob(self.abspath('*/*.amqp'))))

    @staticmethod
    def verify_spool(spool):
        """Check if the spool is writable and raise an exception otherwise."""
        return os.path.exists(spool)\
            and os.access(spool, os.W_OK)\
            and os.access(spool, os.R_OK)

    def __init__(self, spool='/var/spool/aorta'):
        self._spool = os.path.abspath(spool)
        self.logger = logging.getLogger()
        self.logger.info("Persisting in-transit messages to %s", spool)

        # Ensure that the rejected and undeliverable folders
        # exist.
        os.makedirs(self._spool, exist_ok=True)
        os.makedirs(self.abspath('rejected'), exist_ok=True)
        os.makedirs(self.abspath('undeliverable'), exist_ok=True)
        os.makedirs(self.abspath('deliveries'), exist_ok=True)

    def inspect(self):
        """Verify that the buffer is operating normally or raise an exception
        otherwise.
        """
        if not self.verify_spool(self._spool):
            raise self.SpoolNotAvailable

    def abspath(self, *args):
        """Return the absolute path in the spool directory."""
        return os.path.join(self._spool, *args)

    def get(self, tag):
        """Return a :class:`proton.Message` instance by its
        delivery tag.
        """
        src = self.abspath('deliveries', '%s.dstate' % str(tag))
        if not os.path.exists(src):
            raise LookupError

        message = proton.Message()
        with open(src, 'rb') as f:
            message.decode(f.read())

        return message

    def enqueue(self, message, qat, nbf):
        """Queue a new message for transmission.

        Args:
            message (proton.Message): the message to enqueue.
            qat (datetime.datetime): the date and time at which
                the message was queued.
            nbf (datetime.datetime): the date and time before which
                the message may not be transmitted.

        Returns:
            None
        """
        self.persist(message, nbf=nbf)

    def pop(self):
        """Return the next :class:`proton.Message` instance
        that is queued for transmission. This may delete the
        message data from the persistent storage medium.
        """
        now = aorta.lib.timezone.now()
        message = None
        for filename in self._list_queued():
            with open(filename, 'rb') as f:
                message = proton.Message()
                message.decode(f.read())
                if message.annotations.get(ANNOTATE_NBF)\
                and message.annotations[ANNOTATE_NBF] > now:
                    message = None
                    continue

            os.unlink(filename)
            break
        assert message is None\
            or not message.annotations.get(ANNOTATE_NBF)\
            or message.annotations[ANNOTATE_NBF] <= now,\
            f'{message.annotations[ANNOTATE_NBF]} > {now}'
        return message

    def track(self, host, port, source, target, link, tag, message):
        """Track the delivery of `message` to the AMQP remote peer.

        Args:
            host (str): IP address of the AMQP peer.
            port (int): port at which the AMQP peer is listening.
            source (str): source name, if applicable.
            target (str): target name, if applicable.
            link (str): link identifier.
            tag (str): unique delivery tag.
            message (proton.Message): the AMQP message.

        Returns:
            None
        """
        dst = self.abspath('deliveries', '%s.tmp' % str(tag))
        with open(dst, 'wb') as f:
            f.write(message.encode())
            f.flush()
            os.fsync(f.fileno())

        os.rename(dst, dst.replace('.tmp','.dstate'))

    def on_accepted(self, delivery, message, disposition):
        """Invoked when the remote has indicated that it accepts the message.

        Args:
            delivery (proton.Delivery): describes the final state of the
                message transfer.
            message (proton.Message): the AMQP message.
            disposition (proton.Disposition): the message disposition
                describing the remote outcome

        Returns:
            None
        """
        filename = self.abspath('deliveries', '%s.dstate' % delivery.tag)
        os.unlink(filename)

    def error(self, tag, message, undeliverable=False):
        """Invoked when a message could not be delivered.

        Args:
            tag (str): identifies the delivery.
            message (proton.Message): the message that errored.
            undeliverable (bool): indicates if the message was
                undeliverable. If `undeliverable` is ``False``,
                the message was rejected by the remote, it this
                parameter is ``True``, it could not be delivered
                to the remote.

        Returns:
            None
        """
        self.persist(message, state='undeliverable' if undeliverable else 'rejected')

    def persist(self, message, state=None, nbf=0):
        now = aorta.lib.timezone.now()
        if state is not None:
            dst = self.abspath(state, f'{now}-{bytes.hex(message.id)}.tmp')
        else:
            dst = self.abspath(f'{now}-{bytes.hex(message.id)}.tmp')
        assert os.path.exists(os.path.dirname(dst)), dst
        if message.annotations is None:
            message.annotations = {}
        if nbf:
            message.annotations[ANNOTATE_NBF] = nbf
        with open(dst, 'wb') as f:
            f.write(message.encode())
            f.flush()
            os.fsync(f.fileno())

        os.rename(dst, dst.replace('.tmp','.amqp'))

    def _sort(self, path):
        dn, fn = os.path.split(path)
        return fn

    def _list_queued(self):
        files = list(glob.glob(os.path.join(self._spool, '*.amqp')))
        return sorted(files, key=self._sort)

    def _list_deliveries(self):
        files = glob.glob(os.path.join(self._spool, 'deliveries/*.dstate'))
        return list(files)

    def __len__(self):
        return len(self._list_queued())
