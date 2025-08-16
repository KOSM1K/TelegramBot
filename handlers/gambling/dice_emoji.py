import math
import time
import telebot
from chat_context import ChatContext


def dice_emoji(context: ChatContext, message: telebot.types.Message, emoji: str, name: str, score_handler):
    context.any_message_handler(message)

    parts = message.text.split(" ")
    if len(parts) != 2 or not parts[1].isdigit() or int(parts[1]) <= 0:
        context.bot.reply_to(message, f"Неправильный формат! /{name} [ставка]")
        return

    bet = int(parts[1])
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.username

    if not context.database.take_money(user_id, chat_id, bet):
        context.bot.reply_to(message, "У тебя нет столько денег!")
        return

    sent_msg = context.bot.send_dice(
        chat_id=message.chat.id,
        emoji=emoji,
        reply_to_message_id=message.message_id
    )

    context.bot.reply_to(message, f"{user_name} депнул {bet} сатоши")

    time.sleep(1.5)

    coef, is_win = score_handler(sent_msg.dice)

    if is_win:
        amount = math.ceil(bet * coef)
        context.database.add_money(user_id, chat_id, amount)
        context.bot.reply_to(
            message,
            f"🎰 {user_name} выиграл {amount} сатоши"
        )
    else:
        context.bot.reply_to(
            message,
            f"🎰 {user_name} просрал {bet} сатоши"
        )
