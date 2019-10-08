# -*- coding: utf-8 -*-
"""Модуль шифровальщиков."""

import subprocess
import logging


logger = logging.getLogger('msbackup')


class Gpg(object):
    """Шифровальщик посредством утилиты GnuPG."""

    def __init__(self, config, section='DEFAULT', **kwargs):
        """
        Конструктор.

        :param config: Конфигурация.
        :type config: :class:`ConfigParser.RawConfigParser`
        """
        self.cmd = kwargs.get('gpg_cmd') or config.get(
            section, 'GPG_COMMAND', fallback='/usr/bin/gpg')
        self.recipient = kwargs.get('gpg_recipient') or config.get(
            section, 'GPG_RECIPIENT', fallback=None)
        self.suffix = config.get(
            section, 'GPG_SUFFIX', fallback='.gpg')
        self.stderr = kwargs.get('err', subprocess.PIPE)

    def encrypt(self, in_stream, output):
        """
        Шифрование файла.

        :param source: Путь к шифруемому файлу.
        :type source: str
        :param output: Путь к зашифрованному файлу.
        :type output: str
        :param compress_level: Уровень сжатия зашифрованного файла.
        :type compress_level: int
        """
        params = [self.cmd, '--quiet', '--batch']
        params.append('--output')
        params.append(output)
        if self.recipient is not None:
            params.append('--recipient')
            params.append(self.recipient)
        else:
            params.append('--default-recipient-self')
        params.append('--encrypt')
        logger.debug('Run encrypt command: "%s".', ' '.join(params))
        subprocess.check_call(
            params,
            stdin=in_stream,
            stdout=subprocess.DEVNULL,
            stderr=self.stderr,
        )


# Encryptors map.
ENCRYPTORS = {
    'gpg': Gpg,  # Use gnupg encryptor.
}


def make_encryptor(name, *args, **kwargs):
    """
    Фабрика шифровальщика.

    :param name: Имя шифровальщика.
    :type name: str
    :param config: Конфигурация.
    :type config: :class:`ConfigParser.RawConfigParser`
    """
    if name is None:
        return None
    if name not in ENCRYPTORS:
        raise Exception('Unknown encryptor: {}'.format(name))
    return ENCRYPTORS[name](*args, **kwargs)
