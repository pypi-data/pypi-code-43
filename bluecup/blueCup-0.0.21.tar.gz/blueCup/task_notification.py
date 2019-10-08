from collections import namedtuple
from typing import Any, Dict

from nezha.aliyun.robot import Robot
from nezha.aliyun.uemail import Email

from .celery import app
from .task_base import check_schema

emailAbout = namedtuple('emailAbout',
                        ['mail_user', 'mail_pass', 'title', 'content', 'filename', 'receivers', 'specified_receivers']
                        )

dingUrl = namedtuple('dingUrl', ['ding_msg', 'ding_exception'])


def check_args(*args: Dict) -> None:
    if len(*args) > 1:
        raise NotImplementedError(f'args {args} is not support now')


@app.task(name='send_email', bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_email(self: Any, mail_user: str,
               mail_pass: str,
               title: str,
               content: str,
               receivers: str,
               content_is_file: bool = False) -> None:
    Email(mail_user, mail_pass).send_email(title, content, receivers, content_is_file=content_is_file)


@app.task(name='send_email_attach', bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_email_attach(self: Any, mail_user: str,
                      mail_pass: str,
                      title: str,
                      content: str,
                      filename: str,
                      receivers: str, *args: Dict) -> None:
    """
    :param self:
    :param mail_user:
    :param mail_pass:
    :param title:
    :param content:
    :param filename: file can get from filename or args.
    :param receivers:
    :param args: It is adapted to celery task flow. the json schema should be TaskBase.schema_response
    :return:
    """
    print('send_email_attach', locals())
    if not filename:
        print('filename may be passed by args, args is', args)
        check_args(*args)
        last_task_result, = args
        check_schema(last_task_result)
        is_succeed = last_task_result.get('is_succeed')
        if not is_succeed:
            raise ValueError(f'last_task_result {last_task_result} is failed')
    Email(mail_user, mail_pass).send_email_attach(title, content, filename, receivers)


@app.task(name='send_dingding_text', bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_dingding_text(self: Any, url: str, msg: str) -> None:
    Robot(url).send_text(msg)


@app.task(name='send_dingding_markdown', bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_dingding_markdown(self: Any, url: str, title: str, msg: str) -> None:
    print('send_dingding_markdown', locals())
    Robot(url).send_markdown(title, msg)
