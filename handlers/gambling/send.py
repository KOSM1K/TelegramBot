import telebot

from chat_context import ChatContext


def register_gambling_send_command(context: ChatContext):
    handler_command = "send"
    handler_description = "пересылает сатоши в ответ на сообщение"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def send(message: telebot.types.Message):
        context.any_message_handler(message)

        chat_id = message.chat.id
        user_id = message.from_user.id
        user_name = message.from_user.username

        if not message.reply_to_message:
            context.bot.reply_to(message, "Отправь в ответ на сообщение человека, которому хочешь отправить")
            return

        parts = message.text.split(" ")
        if len(parts) != 2:
            context.bot.reply_to(message, "Неверный формат команды! /send [сколько]")
            return

        mention = message.reply_to_message.from_user

        if (not (parts[1].isdigit() or (parts[1][:-1].isdigit() and parts[1][-1] == "%"))) or (mention is None):
            context.bot.reply_to(message, "Неверный формат команды! /send [сколько]")
            return

        amount = 0
        if parts[1][-1] != '%':
            amount = int(parts[1])
        else:
            amount = int((int(parts[1][:-1]) / 100) * context.database.get_money(user_id, chat_id))

        if amount <= 0:
            context.bot.reply_to(message, "Отправить можно только > 0 сатоши")
            return

        result = context.database.take_money(user_id, chat_id, amount)

        if result:
            context.database.add_money(mention.id, chat_id, amount)
            context.bot.reply_to(message, f"{user_name} перевел {amount} {mention.username}")
        else:
            context.bot.reply_to(message, f"Недостаточно денег!")
