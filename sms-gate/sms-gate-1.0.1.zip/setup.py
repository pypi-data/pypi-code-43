from distutils.core import setup
import smsgate

setup(
    name = 'sms-gate',
    version = smsgate.__version__,
    packages = ['smsgate'],
    url = 'https://gitlab.42dev.ru/pixel/sms-gate',
    author = 'pixel',
    author_email = 'piksel@mail.ru',
    maintainer = 'pixel',
    maintainer_email = 'piksel@mail.ru',
    license = 'Commercial',
    description = 'Класс для отправки SMS',
    download_url = 'https://gitlab.42dev.ru/pixel/sms-gate/-/archive/master/sms-gate-master.zip',
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    # package_data = {
    #     'smsgate': [
    #         '*.py',
    #     ],
    # },
    include_package_data = True,
    install_requires = [
        'requests==2.22.0',
    ],
)
