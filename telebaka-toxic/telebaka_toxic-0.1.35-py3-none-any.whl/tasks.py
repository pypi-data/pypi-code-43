import logging
from celery import shared_task
from django.utils.timezone import localtime
from telegram import Bot, TelegramError

from bots.models import TelegramBot
from telebaka_toxic.bot import send_stats
from telebaka_toxic.models import ToxicityRating


@shared_task
def stats():
    date = localtime().date()
    for bot_instance in TelegramBot.objects.filter(plugin_name='telebaka_toxic'):
        bot = Bot(bot_instance.token)
        chats_ids = set(ToxicityRating.objects.filter(date=date, bot=bot_instance).values_list('chat_id', flat=True))
        for chat_id in chats_ids:
            try:
                send_stats(bot, chat_id, date, bot_instance)
            except TelegramError:
                logging.warning(f'Error while sending stats to chat {chat_id}')
