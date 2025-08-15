import math
import time
import random
import telebot
from telebot.types import InputMediaAnimation
from chat_context import ChatContext
from pathlib import Path


def register_gambling_slots_command(context: ChatContext):
    handler_command = "slots"
    handler_description = "депает в слотики"

    context.add_handler_help(handler_command, handler_description)

    symbols = ["⬛", "🍋", "🍒", "7️"]
    gifs = ["bar", "lemon", "berry", "7"]

    games_outcome = [
        {"symbols": [3, 3, 3], "coef": 20, "prob": 0.005},  # 7️⃣7️⃣7️⃣
        {"symbols": [2, 2, 2], "coef": 1.5, "prob": 0.05},  # 🍒🍒🍒
        {"symbols": [1, 1, 1], "coef": 2, "prob": 0.04},    # 🍋🍋🍋
        {"symbols": [0, 0, 0], "coef": 2.5, "prob": 0.03},  # ⬛️⬛️⬛️
        {"symbols": [0, 0, 1], "coef": 1.2, "prob": 0.05},
        {"symbols": [1, 1, 0], "coef": 1.3, "prob": 0.05},
        {"symbols": [2, 2, 3], "coef": 1.4, "prob": 0.03},
        {"symbols": None, "coef": 0, "prob": 0.725}
    ]

    result_gif_folder = Path("assets/")

    @context.bot.message_handler(commands=[handler_command])
    def slots(message: telebot.types.Message):
        context.any_message_handler(message)

        parts = message.text.split(" ")
        if len(parts) != 2 or not parts[1].isdigit() or int(parts[1]) <= 0:
            context.bot.reply_to(message, "Неправильный формат! /slots [ставка]")
            return

        bet = int(parts[1])
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_name = message.from_user.username

        context.database.take_money(user_id, chat_id, bet)

        spinning_gif_path = Path("assets/slot_spin_forever.gif")
        sent_msg = context.bot.send_animation(
            chat_id, open(spinning_gif_path, "rb"),
            caption=f"🎰 {user_name} Депнул {bet} сатоши 🎰\nКрутим..."
        )

        time.sleep(5)

        probs = [g["prob"] for g in games_outcome]
        chosen = random.choices(games_outcome, weights=probs, k=1)[0]
        chosen_symbols = chosen["symbols"]
        if chosen_symbols is None:
            chosen_symbols = random.sample(range(len(symbols)), 3)

        emoji_frame = [symbols[i] for i in chosen_symbols]
        result_str = f"[{emoji_frame[0]}][{emoji_frame[1]}][{emoji_frame[2]}]"

        gif_names = [gifs[i] for i in chosen_symbols]
        result_gif_name = f"{'_'.join(gif_names)}.gif"
        result_gif_path = result_gif_folder / result_gif_name

        with open(result_gif_path, "rb") as f:
            context.bot.edit_message_media(
                chat_id=chat_id,
                message_id=sent_msg.message_id,
                media=InputMediaAnimation(f, caption=f"🎰 {user_name} Депнул {bet} 🎰\n{result_str}")
            )

        if chosen["coef"] > 0:
            amount = math.ceil(bet * chosen["coef"])
            context.database.add_money(user_id, chat_id, amount)
            context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=sent_msg.message_id,
                caption=f"🎰 {user_name} Депнул {bet} 🎰\n{result_str} сатоши 🎰\nВыигрыш: {amount} сатоши"
            )
        else:
            context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=sent_msg.message_id,
                caption=f"🎰 {user_name} Депнул {bet} 🎰\n{result_str} сатоши 🎰\nПросрано {bet} сатоши"
            )
