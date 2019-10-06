"""
name                Название пакета
version             Версия
description         Краткое описание
url                 URL-адрес сайта
license             Лицензия (требуется верная запись)
author              Имя автора
author_email        Почта автора
packages            Пакеты, которые нужно скопировать (без рекурсии, необходимо указывать вложенные)
install_requires    Зависимости пакета от других пакетов
scripts             Запускаемые из командной строки скрипты
py_modules          Модули, которые нужно скопировать
"""

from setuptools import setup

setup(
    name='lesson-utils',
    version='1.0.0',
    description='Collection of useful features for the course Python.',
    url='https://github.com/kyzima-spb/lesson-utils',
    license='Apache License 2.0',
    author='Kirill Vercetti',
    author_email='office@kyzima-spb.com',
    packages=['lesson_utils']
)
