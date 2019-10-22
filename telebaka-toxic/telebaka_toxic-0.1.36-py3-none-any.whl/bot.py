import re
from django.db import models
from django.utils.timezone import now, localtime
from functools import partial

from telegram import Bot, Update, User
from telegram.ext import MessageHandler, Filters, CommandHandler, BaseFilter, RegexHandler
from telegram.utils.helpers import mention_html

from bots.models import TelegramBot
from telebaka_toxic.models import ToxicityRating, String


TOXIC_PHRASES = [
    r'наху[йя]',
    r'[оа]?ху[йёиел]',
    r'пизд',
    r'(за|вы)?[её]б',
    r'токс',
    r'залуп',
    r'дерьм',
    r'мраз[ьио]',
    r'светов',
    r'бур[яа]ков',
    r'(вы)?бл[яэ][дт]',
    r'(обо|на)?сс[аы]',
    r'(обо|на)?ср[аи]',
    r'пер[джн]',
    r'пук',
    r'мусор',
    r'чь?мо',
    r'ло[хш]',
    r'пид[оа]р',
    r'говн',
    r'муд[аи]',
    r'сос[иау]',
    r'[вш]инд',
    r'подави',
    r'мамк?',
    r'долбо',
    r'олен',
    r'натурал',
    r'транспортн',
    r'тн',
    r'веган',
    r'лоно',
    r'параш',
    r'прохоров',
    r'фк[^\w]',
    r'нин',
    r'неонил',
    r'осенин',
    r'самодуров',
    r'бойк',
    r'оч[^\w]',
    r'цего',
    r'люстраци',
    r'полл?юци',
    r'м[ао]рлен',
    r'фл[еэ]ш',
    r'трап',
    r'бод',
    r'фаш',
    r'нац',
    r'либер',
    r'ари[йе]'
    r'джава',
    r'пхп',
    r'php',
    r'java',
    r'спасиб',
    r'лину[пкс]',
    r'г[ие]нз',
    r'гош',
    r'гирш',
    r'кря',
    r'кобзон',
    r'кобзон',
    r'кобзон',
    r'овчаров',
    r'овчаров',
    r'овчаров',
]


def send_stats(bot: Bot, chat_id, date, bot_instance):
    ratings = ToxicityRating.objects\
                  .filter(chat_id=chat_id, date=date, rating__gt=0, bot=bot_instance)\
                  .order_by('-rating')
    result = []
    for r in ratings:
        result.append(f' · {r.name}: {r.rating}')
    result = '\n'.join(result)
    bot.send_message(chat_id, f'Список токсичных существ на сегодня ({date}):\n\n{result}', parse_mode='html')


def get_string(rating):
    min_rating = String.objects.filter(min_rating__lte=rating).aggregate(mmr=models.Max('min_rating'))['mmr']
    result = String.objects.filter(min_rating=min_rating).order_by('?').first()
    if result:
        return result.text
    else:
        if rating == -1:
            return 'Кто токсичный? Ну вот кто?'
        else:
            return 'Бип-буп. Осторожно, {warned_link} токсичен. Уровень токсичности: {warned_rating}.'


def get_rating(chat_id, user, bot_instance):
    rating, created = ToxicityRating.objects.update_or_create(
        user_id=user.id, chat_id=chat_id, date=localtime().date(), bot=bot_instance,
        defaults={
            'username': user.username,
            'name': user.full_name
        }
    )
    return rating


def add_toxicity(value, chat_id, user: User, bot_instance):
    rating = get_rating(chat_id, user, bot_instance)
    rating.rating += value
    rating.save()
    return rating


def stats(bot: Bot, update: Update, bot_instance: TelegramBot):
    send_stats(bot, update.effective_message.chat_id, localtime().date(), bot_instance)


def toxic(bot: Bot, update: Update, bot_instance: TelegramBot):
    if update.effective_message.reply_to_message:
        r = update.effective_message.reply_to_message
        if update.effective_user.id == r.from_user.id:
            return
        warned_rating = add_toxicity(3, update.effective_message.chat_id, r.from_user,
                                     bot_instance)
        warner_rating = add_toxicity(5, update.effective_message.chat_id, update.effective_message.from_user,
                                     bot_instance)
        update.effective_message.reply_text(get_string(warned_rating.rating).format(warned_link=warned_rating.link,
                                                                                    warned_rating=warned_rating.rating,
                                                                                    warner_link=warner_rating.link,
                                                                                    warner_rating=warner_rating.rating),
                                            parse_mode='html', quote=True)
    else:
        update.effective_message.reply_text(get_string(-1), parse_mode='html', quote=True)


def regex(bot: Bot, update: Update, bot_instance: TelegramBot):
    m = update.effective_message
    rating = get_rating(m.chat_id, m.from_user, bot_instance)
    for phrase in TOXIC_PHRASES:
        if re.search(r'^(.*[^\w])?' + phrase, update.effective_message.text, re.IGNORECASE):
            rating.rating += 1
    if m.reply_to_message and m.reply_to_message.from_user.id == bot.id:
        rating.rating += 1
    # if 'кобзон' in update.effective_message.text.lower():
    #     update.message.reply_text('Он умер')
    rating.save()


def sticker(bot: Bot, update: Update, bot_instance: TelegramBot):
    add_toxicity(1, update.effective_message.chat_id, update.effective_message.from_user, bot_instance)


def ger_callback(bot: Bot, update: Update):
    update.effective_message.reply_text('{} has gorren'.format(mention_html(update.effective_user.id,
                                                                            update.effective_user.full_name)),
                                        parse_mode='html')


def setup(dispatcher):
    stats_callback = partial(stats, bot_instance=dispatcher.bot_instance)
    toxic_callback = partial(toxic, bot_instance=dispatcher.bot_instance)
    regex_callback = partial(regex, bot_instance=dispatcher.bot_instance)
    sticker_callback = partial(sticker, bot_instance=dispatcher.bot_instance)
    dispatcher.add_handler(CommandHandler('stats', stats_callback))
    dispatcher.add_handler(CommandHandler('toxic', toxic_callback))
    dispatcher.add_handler(CommandHandler('warn', toxic_callback))
    dispatcher.add_handler(CommandHandler('ger', ger_callback))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, regex_callback))
    dispatcher.add_handler(MessageHandler(Filters.sticker, sticker_callback))
    return dispatcher
