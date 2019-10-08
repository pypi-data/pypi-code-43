import json
import logging
import os

import boto3
from colorlog import ColoredFormatter, StreamHandler

import news2play.common.config as config
from news2play.common import file_meta_data, file_log, folder_data_ymd
from news2play.common.cursor_utils import Spinner
from news2play.common.utils import Program, logged
from news2play.tts import PollyTextToSpeech
from news2play.web_downloader import fid_spider

logger = logging.getLogger(__name__)

init_stage = False


@logged(level=logging.INFO, message='text to speech...')
def text2speech(tts):
    with open(file_meta_data) as f:
        meta_data_list = json.loads(f.read())

    # for debug mode, only test first three news
    if Program.debugging():
        meta_data_list = meta_data_list[:3]

    for i, meta_data in enumerate(meta_data_list):
        title = meta_data['title']
        content = meta_data['news']
        author = meta_data['author']
        timestamp = meta_data['timestamp']
        filename = meta_data['filename']

        logger.info(f"top news: {i + 1}")
        logger.info(f"title: {title}")
        logger.info(f"author: {author}")
        logger.info(f"timestamp: {timestamp}")

        f_name = os.path.join(folder_data_ymd, filename)

        news_contents = list(map(str.strip, content.split('-', 1)))

        logger.debug(f'''title:\n{title}''')

        if len(news_contents) > 1:
            text = f'''{title}. from {news_contents[0]}. {news_contents[1]}'''
            logger.debug(f'''news content0:\n{news_contents[0]}''')
            logger.debug(f'''news content1:\n{news_contents[1]}''')
        else:
            text = f'''{title}. from {author}. {news_contents}'''
            logger.debug(f'''text:\n{text}''')

        tts.save_audio(f_name, text, config.audio_type)


@logged(level=logging.INFO, message='download news...')
def download_news():
    news_json = fid_spider.load_news(config.storage_data)

    f_name = os.path.join(file_meta_data)
    with open(f_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(news_json, indent=4))


def upload_files_to_s3(path):
    session = boto3.Session()

    s3 = session.resource("s3")
    bucket = s3.Bucket(config.s3_bucket)

    for subdir, dirs, files in os.walk(path):
        for file in files:
            if not file.startswith('.'):
                full_path = os.path.join(subdir, file)
                with open(full_path, 'rb') as data:
                    bucket.put_object(Key=full_path[len(path) + 1:], Body=data)


# below log will not run as the logger is not init
@logged(level=logging.INFO, message='storage init...')
def storage_init():
    for item in [config.storage_conf, config.storage_data, config.storage_log]:
        if not os.path.exists(item):
            os.makedirs(item)


# below log will not run as the logger is not init
@logged(level=logging.INFO, message='logging init...')
def logging_init():
    file_handler = logging.FileHandler(file_log, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    file_handler.setFormatter(file_formatter)

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)
    # console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # console_handler.setFormatter(console_formatter)

    console_handler = StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_color_formatter = ColoredFormatter(
        "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s %(message_log_color)s%(message)s",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={
            'message': {
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        },
        style='%'
    )
    console_handler.setFormatter(console_color_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    disable_loggers = ['urllib3', 'pydub']
    for item in disable_loggers:
        logging.getLogger(item).setLevel(logging.WARNING)


@logged(level=logging.INFO, message='module init...')
def module_init():
    import nltk
    nltk.download('punkt')


def init():
    storage_init()
    logging_init()
    module_init()


def main():
    # todo: for debug, in current thread
    if Program.debugging():
        download_news()
        text2speech(PollyTextToSpeech())
        # text2speech(AzureTextToSpeech())
    else:
        with Spinner():
            download_news()
            text2speech(PollyTextToSpeech())
            # text2speech(AzureTextToSpeech())


def run():
    global init_stage
    if init_stage is False:
        init()
        init_stage = True

    logger.info('︿(￣︶￣)︿ news to audios start...')
    main()
    logger.info('ヾ(￣▽￣)Bye~Bye~ news to audios finished.')
    upload_files_to_s3(config.storage_data)
    logger.info('upload to s3.')
