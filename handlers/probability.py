import random

import telebot

from chat_context import ChatContext


def register_probability_command(context: ChatContext):
    handler_command = "prob"
    handler_description = "Выводит вероятность какого-то события"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def handler(message: telebot.types.Message):
        args = message.text.partition(' ')

        if len(args) != 3:
            context.bot.reply_to(message, "Ожидаемый формат: /prop <cобытие>")
            return

        event_name = args[2]

        if len(event_name) <= 1:
            context.bot.reply_to(message, "Ожидаемый формат: /prop <cобытие>")
            return

        probability = random.randint(0, 100)

        context.bot.reply_to(message, f"Вероятность \"{event_name}\" {probability}%")

