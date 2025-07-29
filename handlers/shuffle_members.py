import telebot

import random

from chat_context import ChatContext


def register_shuffle_members_command(context: ChatContext):
    handler_command = "shuffle"
    handler_description = "Случайным образом распределяет учатников чата"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def bot_shuffle(message: telebot.types.Message):
        context.any_message_handler(message)

        chat_id = message.chat.id

        is_loud = "-loud" in message.text

        mentions = [elem for elem in message.entities if elem.type == "mention"]

        if len(mentions) > 0:
            chosen_mention = random.choice(mentions)
            response_msg = message.text[chosen_mention.offset:chosen_mention.offset + chosen_mention.length]

            context.bot.send_message(chat_id, f"Случайный порядок: {response_msg}")
            return

        chosen_order = context.database.all_members_of_chat(chat_id)

        if len(chosen_order) == 0:
            context.bot.reply_to(message, "Не могу выбрать никого, недостаточно данных 🫤")
            return

        for i in range(int(len(chosen_order) ** 0.5 + 1)):
            random.shuffle(chosen_order)

        message = "Случайный порядок:\n"
        index = 1
        for tg_id in chosen_order:
            target_username = context.bot.get_chat_member(chat_id, tg_id).user.username
            if is_loud:
                message += "{:>8}".format(
                    index) + f"    [{target_username}](tg://user?id={tg_id}) \n"
            else:
                message += "{:>8}".format(
                    index) + f"    {target_username} \n"

            index += 1

        if is_loud:
            context.bot.send_message(chat_id,
                                     message,
                                     parse_mode="Markdown")
        else:
            context.bot.send_message(chat_id, message)
