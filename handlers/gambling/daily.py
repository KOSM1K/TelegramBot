import random
from datetime import datetime, timedelta

import telebot

from chat_context import ChatContext


def register_gambling_daily_action(context: ChatContext):
    handler_command = "daily"
    handler_description = "выдает дейлики"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def daily(message: telebot.types.Message):
        MIN_DAILY_REWARD = 300
        MAX_DAILY_REWARD = 700

        chat_id = message.chat.id
        chat_members = context.database.all_members_of_chat(chat_id)

        if len(chat_members) == 0:
            context.bot.reply_to(message, "Пока что никого не записал :(")
            return

        last_daily = context.database.get_last_daily(chat_id)
        if last_daily is not None:
            last_call_dt = datetime.fromtimestamp(last_daily)
            elapsed = datetime.now() - last_call_dt

            if elapsed < timedelta(hours=24):
            # if elapsed < timedelta(seconds=24):
                context.bot.reply_to(message, f"Прошло лишь {elapsed} с прошлой выдачи")
                return

        context.database.update_daily(chat_id)

        for cur_user_id in chat_members:
            amount = random.randint(MIN_DAILY_REWARD, MAX_DAILY_REWARD)

            context.database.add_money(cur_user_id, chat_id, amount)

        context.bot.reply_to(message, "Дейлики выданы! Увидимся через 24 часа")

