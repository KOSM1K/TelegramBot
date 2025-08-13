import telebot

from chat_context import ChatContext


def register_gambling_balance_command(context: ChatContext):
    handler_command = "balance"
    handler_description = "выводит количество сатоши"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def balance(message: telebot.types.Message):
        context.any_message_handler(message)

        chat_id = message.chat.id
        user_id = message.from_user.id
        user_name = message.from_user.username

        money = context.database.get_money(user_id, chat_id)

        context.bot.reply_to(message, f"Баланс {user_name} - {money} сатоши")

