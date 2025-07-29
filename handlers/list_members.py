import telebot
import random

from chat_context import ChatContext


def register_list_members_command(context: ChatContext):
    handler_command = "list_members"
    handler_description = "Выводит зарегестрированных участников чата"

    context.add_handler_help(handler_command, handler_description)

    def get_mentions(message: telebot.types.Message):
        return [elem for elem in message.entities if elem.type == "mention"]

    @context.bot.message_handler(commands=[handler_command])
    def bot_random(message: telebot.types.Message):
        context.any_message_handler(message)

        chat_id = message.chat.id
        is_loud = "-loud" in message.text

        chat_members = context.database.all_members_of_chat(chat_id)

        if len(chat_members) == 0:
            context.bot.reply_to(message, "Пока что никого не записал :(")
            return

        str_of_users_with_indexes = ""
        index = 1
        for cur_user_id in chat_members:
            target_username = context.bot.get_chat_member(chat_id, cur_user_id).user.username

            if is_loud:
                str_of_users_with_indexes += "{:>8}".format(
                    index) + f"    [{target_username}](tg://user?id={cur_user_id}) \n"
            else:
                str_of_users_with_indexes += "{:>8}".format(
                    index) + f"    {target_username} \n"
            index += 1

        message = "Вот список всех зарегестрированных участников:\n" + str_of_users_with_indexes

        if is_loud:
            context.bot.send_message(chat_id, message, parse_mode="Markdown")
        else:
            context. bot.send_message(chat_id, message)
