from typing import Union

from telegram_bot_sdk.helper.util import check_locals
from telegram_bot_sdk.network import network
from telegram_bot_sdk.helper.config_manager import load_config
from telegram_bot_sdk.network.network import HttpVerbs
from telegram_bot_sdk.objects.telegram_objects.chat import Chat
from telegram_bot_sdk.objects.telegram_objects.chatMember import ChatMember
from telegram_bot_sdk.objects.telegram_objects.file import File
from telegram_bot_sdk.objects.telegram_objects.inlineQueryResult import InlineQueryResult
from telegram_bot_sdk.objects.telegram_objects.inlineQueryResultArticle import InlineQueryResultArticle
from telegram_bot_sdk.objects.telegram_objects.inputTextMessageContent import InputTextMessageContent
from telegram_bot_sdk.objects.telegram_objects.message import Message
from telegram_bot_sdk.objects.telegram_objects.poll import Poll
from telegram_bot_sdk.objects.telegram_objects.stickerSet import StickerSet
from telegram_bot_sdk.objects.telegram_objects.user import User
from telegram_bot_sdk.objects.telegram_objects.userProfilePhotos import UserProfilePhotos
from telegram_bot_sdk.objects.telegram_objects.update import Update
import asyncio


class TelegramBot:
    def __init__(self, bot_token):
        self.config = {"URL": "https://api.telegram.org/bot" + bot_token + "/"}
        self.my_network = network.NetworkInternalAsync(self.config)

    def get_updates(self, *, offset=None, limit=None, timeout=None, allowed_updates=None) -> list:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getUpdates", data=data_dict)
        return [Update(**x) for x in response]

    def get_me(self) -> User:
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getMe")
        return User(**response)

    def get_user_profile_photos(self, *, user_id, offset=None, limit=None) -> UserProfilePhotos:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.GET, call="getUserProfilePhotos", data=data_dict)
        return UserProfilePhotos(**response)

    def send_message(self, *, chat_id, text, parse_mode=None, disable_web_page_preview=None,
                     disable_notification=None, reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.GET, call="sendMessage", data=data_dict)
        return Message(**response)

    def send_location(self, *, chat_id, latitude, longitude, live_period=None, disable_notification=None,
                      reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="sendLocation", data=data_dict)
        return Message(**response)

    def send_venue(self, *, chat_id, latitude, longitude, title, address, foursquare_id=None,
                   foursquare_type=None, disable_notification=None, reply_to_message_id=None,
                   reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="sendVenue", data=data_dict)
        return Message(**response)

    def send_contact(self, *, chat_id, phone_number, first_name, last_name=None, vcard=None,
                     disable_notification=None, reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="sendContact", data=data_dict)
        return Message(**response)

    def send_poll(self, *, chat_id, question, options, disable_notification=None,
                  reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(call=HttpVerbs.POST, verb="sendPoll", data=data_dict)
        return Message(**response)

    def send_chat_action(self, *, chat_id, action) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="sendChatAction", data=data_dict)
        return response

    def get_file(self, file_id) -> File:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getFile", data=data_dict)
        return File(**response)

    def kick_chat_member(self, *, chat_id, user_id, until_date=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="kickChatMember", data=data_dict)
        return response

    def unban_chat_member(self, *, chat_id, user_id) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="unbanChatMember", data=data_dict)
        return response

    def restrict_chat_member(self, *, chat_id, user_id, permissions, until_date=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="restrictChatMember", data=data_dict)
        return response

    def promote_chat_member(self, *, chat_id, user_id, can_change_info=None, can_post_messages=None,
                            can_edit_messages=None, can_delete_messages=None, can_invite_users=None,
                            can_restrict_members=None, can_pin_messages=None, can_promote_members=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="promoteChatMember", data=data_dict)
        return response

    def set_chat_permissions(self, *, chat_id, permissions=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="setChatPermissions", data=data_dict)
        return response

    def export_chat_invite_link(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="exportChatInviteLink", data=data_dict)
        return response

    def set_chat_photo(self, *, chat_id, photo) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="setChatPhoto", data=data_dict)
        return response

    def delete_chat_photo(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="deleteChatPhoto", data=data_dict)
        return response

    def set_chat_title(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="setChatTitle", data=data_dict)
        return response

    def set_chat_description(self, *, chat_id, description=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="setChatDescription", data=data_dict)
        return response

    def pin_chat_message(self, *, chat_id, message_id, disable_notification=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="pinChatMessage", data=data_dict)
        return response

    def unpin_chat_message(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="unpinChatMessage", data=data_dict)
        return response

    def leave_chat(self, chat_id) -> Chat:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="leaveChat", data=data_dict)
        return Chat(**response)

    def get_chat(self, chat_id) -> Chat:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getChat", data=data_dict)
        return Chat(**response)

    def get_chat_administrators(self, chat_id) -> list:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getChatAdministrators", data=data_dict)
        return [ChatMember(**response)]

    def get_chat_members_counter(self, chat_id) -> int:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getChatMembersCount", data=data_dict)
        return response

    def get_chat_member(self, *, chat_id, user_id) -> ChatMember:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getChatMember", data=data_dict)
        return ChatMember(**response)

    def set_chat_sticker_set(self, *, chat_id, sticker_set_name) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="setChatStickerSet", data=data_dict)
        return response

    def delete_chat_sticker_set(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="deleteChatStickerSet", data=data_dict)
        return response

    def answer_callback_query(self, *, callback_query_id, text=None, show_alert=None, url=None,
                              cache_time=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="answerCallbackQuery", data=data_dict)
        return response

    def edit_message_text(self, *, text, chat_id=None, message_id=None, inline_message_id=None, parse_mode=None,
                          disable_web_page_preview=None, reply_markup=None) -> Union[bool, Message]:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="editMessageText", data=data_dict)
        if not isinstance(response, bool):
            return Message(**response)
        return response

    def edit_message_caption(self, *, chat_id=None, message_id=None, inline_message_id=None, caption=None,
                             parse_mode=None, reply_markup=None) -> Union[bool, Message]:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="editMessageCaption", data=data_dict)
        if not isinstance(response, bool):
            return Message(**response)
        return response

    def edit_message_media(self, *, media, chat_id=None, message_id=None, inline_message_id=None,
                           reply_markup=None) -> Union[bool, Message]:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="editMessageMedia", data=data_dict)
        if not isinstance(response, bool):
            return Message(**response)
        return response

    def edit_message_reply_markup(self, *, chat_id=None, message_id=None, inline_message_id=None,
                                  reply_markup=None) -> Union[bool, Message]:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="editMessageReplyMarkup", data=data_dict)
        if not isinstance(response, bool):
            return Message(**response)
        return response

    def stop_poll(self, *, chat_id, message_id, reply_markup=None) -> Poll:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="stopPoll", data=data_dict)
        return Poll(**response)

    def delete_message(self, *, chat_id, message_id) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="deleteMessage", data=data_dict)
        return response

    def get_sticker(self, *, chat_id, sticker, disable_notification=None, reply_to_message_id=None,
                    reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getSticker", data=data_dict)
        return Message(**response)

    def get_sticker_set(self, name) -> StickerSet:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="getStickerSet", data=data_dict)
        return StickerSet(**response)

    def upload_sticker_file(self, *, user_id, png_sticker) -> File:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="uploadStickerFile", data=data_dict)
        return File(**response)

    def create_new_sticker_set(self, *, user_id, name, title, png_sticker, emojis, contains_mask=None,
                               mask_position=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="createNewStickerSet", data=data_dict)
        return response

    def add_sticker_to_set(self, user_id, name, png_sticker, emojis, mask_position=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="addStickerToSet", data=data_dict)
        return response

    def set_sticker_position_in_set(self, *, sticker, position) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="setStickerPositionInSet", data=data_dict)
        return response

    def delete_sticker_from_set(self, sticker) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="deleteStickerFromSet", data=data_dict)
        return response

    def answer_inline_query(self, *, inline_query_id, results, cache_time=None, is_personal=None, next_offset=None,
                            switch_pm_text=None, switch_pm_parameter=None) -> bool:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="answerInlineQuery", data=data_dict)
        return response

    def send_invoice(self, *, chat_id, title, description, payload, provider_token, start_parameter, currency,
                     prices, provider_data=None, photo_url=None, photo_size=None, photo_width=None, photo_height=None,
                     need_name=None, need_phone_number=None, need_email=None, need_shipping_address=None,
                     send_phone_number_to_provider=None, send_email_to_provider=None, is_flexible=None,
                     disable_notification=None, reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = self.my_network.make_request(verb=HttpVerbs.POST, call="sendInvoice", data=data_dict)
        return Message(**response)


class TelegramBotAsync:
    def __init__(self, bot_token):
        self.config = {"URL": "https://api.telegram.org/bot" + bot_token + "/"}
        self.my_network = network.NetworkAsync(self.config)

    async def get_updates(self, *, offset=None, limit=None, timeout=None, allowed_updates=None) -> list:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getUpdates", data=data_dict)
        return [Update(**x) for x in response]

    async def get_me(self) -> User:
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getMe")
        return User(**response)

    async def get_user_profile_photos(self, *, user_id, offset=None, limit=None) -> UserProfilePhotos:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.GET, call="getUserProfilePhotos", data=data_dict)
        return UserProfilePhotos(**response)

    async def send_message(self, *, chat_id, text, parse_mode=None, disable_web_page_preview=None,
                           disable_notification=None, reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.GET, call="sendMessage", data=data_dict)
        return Message(**response)

    async def send_location(self, *, chat_id, latitude, longitude, live_period=None, disable_notification=None,
                            reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="sendLocation", data=data_dict)
        return Message(**response)

    async def send_venue(self, *, chat_id, latitude, longitude, title, address, foursquare_id=None,
                         foursquare_type=None, disable_notification=None, reply_to_message_id=None,
                         reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="sendVenue", data=data_dict)
        return Message(**response)

    async def send_contact(self, *, chat_id, phone_number, first_name, last_name=None, vcard=None,
                           disable_notification=None, reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="sendContact", data=data_dict)
        return Message(**response)

    async def send_poll(self, *, chat_id, question, options, disable_notification=None,
                        reply_to_message_id=None, reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(call=HttpVerbs.POST, verb="sendPoll", data=data_dict)
        return Message(**response)

    async def send_chat_action(self, *, chat_id, action) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="sendChatAction", data=data_dict)
        return response

    async def get_file(self, file_id) -> File:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getFile", data=data_dict)
        return File(**response)

    async def kick_chat_member(self, *, chat_id, user_id, until_date=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="kickChatMember", data=data_dict)
        return response

    async def unban_chat_member(self, *, chat_id, user_id) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="unbanChatMember", data=data_dict)
        return response

    async def restrict_chat_member(self, *, chat_id, user_id, permissions, until_date=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="restrictChatMember", data=data_dict)
        return response

    async def promote_chat_member(self, *, chat_id, user_id, can_change_info=None, can_post_messages=None,
                                  can_edit_messages=None, can_delete_messages=None, can_invite_users=None,
                                  can_restrict_members=None, can_pin_messages=None, can_promote_members=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="promoteChatMember", data=data_dict)
        return response

    async def set_chat_permissions(self, *, chat_id, permissions=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="setChatPermissions", data=data_dict)
        return response

    async def export_chat_invite_link(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="exportChatInviteLink", data=data_dict)
        return response

    async def set_chat_photo(self, *, chat_id, photo) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="setChatPhoto", data=data_dict)
        return response

    async def delete_chat_photo(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="deleteChatPhoto", data=data_dict)
        return response

    async def set_chat_title(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="setChatTitle", data=data_dict)
        return response

    async def set_chat_description(self, *, chat_id, description=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="setChatDescription", data=data_dict)
        return response

    async def pin_chat_message(self, *, chat_id, message_id, disable_notification=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="pinChatMessage", data=data_dict)
        return response

    async def unpin_chat_message(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="unpinChatMessage", data=data_dict)
        return response

    async def leave_chat(self, chat_id) -> Chat:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="leaveChat", data=data_dict)
        return Chat(**response)

    async def get_chat(self, chat_id) -> Chat:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getChat", data=data_dict)
        return Chat(**response)

    async def get_chat_administrators(self, chat_id) -> list:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getChatAdministrators", data=data_dict)
        return [ChatMember(**response)]

    async def get_chat_members_counter(self, chat_id) -> int:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getChatMembersCount", data=data_dict)
        return response

    async def get_chat_member(self, *, chat_id, user_id) -> ChatMember:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getChatMember", data=data_dict)
        return ChatMember(**response)

    async def set_chat_sticker_set(self, *, chat_id, sticker_set_name) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="setChatStickerSet", data=data_dict)
        return response

    async def delete_chat_sticker_set(self, chat_id) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="deleteChatStickerSet", data=data_dict)
        return response

    async def answer_callback_query(self, *, callback_query_id, text=None, show_alert=None, url=None,
                                    cache_time=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="answerCallbackQuery", data=data_dict)
        return response

    async def edit_message_text(self, *, text, chat_id=None, message_id=None, inline_message_id=None, parse_mode=None,
                                disable_web_page_preview=None, reply_markup=None) -> Union[bool, Message]:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="editMessageText", data=data_dict)
        if not isinstance(response, bool):
            return Message(**response)
        return response

    async def edit_message_caption(self, *, chat_id=None, message_id=None, inline_message_id=None, caption=None,
                                   parse_mode=None, reply_markup=None) -> Union[bool, Message]:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="editMessageCaption", data=data_dict)
        if not isinstance(response, bool):
            return Message(**response)
        return response

    async def edit_message_media(self, *, media, chat_id=None, message_id=None, inline_message_id=None,
                                 reply_markup=None) -> Union[bool, Message]:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="editMessageMedia", data=data_dict)
        if not isinstance(response, bool):
            return Message(**response)
        return response

    async def edit_message_reply_markup(self, *, chat_id=None, message_id=None, inline_message_id=None,
                                        reply_markup=None) -> Union[bool, Message]:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="editMessageReplyMarkup", data=data_dict)
        if not isinstance(response, bool):
            return Message(**response)
        return response

    async def stop_poll(self, *, chat_id, message_id, reply_markup=None) -> Poll:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="stopPoll", data=data_dict)
        return Poll(**response)

    async def delete_message(self, *, chat_id, message_id) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="deleteMessage", data=data_dict)
        return response

    async def get_sticker(self, *, chat_id, sticker, disable_notification=None, reply_to_message_id=None,
                          reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getSticker", data=data_dict)
        return Message(**response)

    async def get_sticker_set(self, name) -> StickerSet:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="getStickerSet", data=data_dict)
        return StickerSet(**response)

    async def upload_sticker_file(self, *, user_id, png_sticker) -> File:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="uploadStickerFile", data=data_dict)
        return File(**response)

    async def create_new_sticker_set(self, *, user_id, name, title, png_sticker, emojis, contains_mask=None,
                                     mask_position=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="createNewStickerSet", data=data_dict)
        return response

    async def add_sticker_to_set(self, user_id, name, png_sticker, emojis, mask_position=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="addStickerToSet", data=data_dict)
        return response

    async def set_sticker_position_in_set(self, *, sticker, position) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="setStickerPositionInSet", data=data_dict)
        return response

    async def delete_sticker_from_set(self, sticker) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="deleteStickerFromSet", data=data_dict)
        return response

    async def answer_inline_query(self, *, inline_query_id, results, cache_time=None, is_personal=None, next_offset=None,
                                  switch_pm_text=None, switch_pm_parameter=None) -> bool:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="answerInlineQuery", data=data_dict)
        return response

    async def send_invoice(self, *, chat_id, title, description, payload, provider_token, start_parameter, currency,
                           prices, provider_data=None, photo_url=None, photo_size=None, photo_width=None,
                           photo_height=None, need_name=None, need_phone_number=None, need_email=None,
                           need_shipping_address=None, send_phone_number_to_provider=None, send_email_to_provider=None,
                           is_flexible=None, disable_notification=None, reply_to_message_id=None,
                           reply_markup=None) -> Message:
        data_dict = check_locals(**locals())
        response = await self.my_network.make_request(verb=HttpVerbs.POST, call="sendInvoice", data=data_dict)
        return Message(**response)


async def worker():
    t = TelegramBotAsync()
    await asyncio.create_task(fetch_messages(t))


async def do_things(telebot, update):
    if update.inline_query.query:
        text = "Habe das empfangen: " + update.inline_query.query
        await telebot.send_message(chat_id=update.message.chat.id_unique, text=text)
        await telebot.answer_inline_query(inline_query_id=update.inline_query.id_unique, results=[])
    await asyncio.sleep(0.1)


async def fetch_messages(telebot):
    offset = None
    while True:
        update = await telebot.get_updates()
        for item in update:
            print(item.__dict__)
            if item.inline_query:
                await do_things(telebot, item)


def main():
    asyncio.run(worker())


if __name__ == '__main__':
    main()
