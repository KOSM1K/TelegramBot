import math
import time

import telebot
import random

from chat_context import ChatContext


def register_gambling_slots_command(context: ChatContext):
    handler_command = "slots"
    handler_description = "депает в слотики"

    context.add_handler_help(handler_command, handler_description)

    symbols = [
        "🍒",
        "🍋",
        "⭐",
        "🍉",
        "💎",
        "7️⃣"
    ]

    games_outcome = [
        {"symbols": [4, 4, 4], "coef": 10, "prob": 0.01},  # 💎💎💎
        {"symbols": [5, 5, 5], "coef": 20, "prob": 0.005},  # 7️⃣7️⃣7️⃣
        {"symbols": [0, 0, 0], "coef": 1.5, "prob": 0.05},  # 🍒🍒🍒
        {"symbols": [1, 1, 1], "coef": 2, "prob": 0.04},  # 🍋🍋🍋
        {"symbols": [2, 2, 2], "coef": 2.5, "prob": 0.03},  # 🍉🍉🍉
        {"symbols": [3, 3, 3], "coef": 3, "prob": 0.02},  # ⭐⭐⭐

        {"symbols": [0, 0, 1], "coef": 1.2, "prob": 0.05},
        {"symbols": [1, 1, 0], "coef": 1.3, "prob": 0.05},
        {"symbols": [2, 2, 3], "coef": 1.4, "prob": 0.03},

        {"symbols": None, "coef": 0, "prob": 0.725}
    ]

    @context.bot.message_handler(commands=[handler_command])
    def slots(message: telebot.types.Message):
        context.any_message_handler(message)

        arguments = message.text

        parts = arguments.split(" ")
        if len(parts) != 2:
            context.bot.reply_to(message, "Неправильный формат! /slots [ставка]")
            return

        part = parts[1]

        if (not part.isdigit()) or (int(part) <= 0):
            context.bot.reply_to(message, "Ставка это целое число > 0!")
            return

        bet = int(part)

        chat_id = message.chat.id
        user_id = message.from_user.id

        context.database.take_money(user_id, chat_id, bet)

        user_name = message.from_user.username

        sent = context.bot.reply_to(message, f"🎰 {user_name} Депнул {bet} 🎰\n[❓][❓][❓]")

        emojis = [s for s in symbols]

        last_frame = None
        for _ in range(3):
            frame = f"[{random.choice(emojis)}][{random.choice(emojis)}][{random.choice(emojis)}]"

            if last_frame != frame:
                context.bot.edit_message_text(
                    text=f"🎰 {user_name} Депнул {bet} 🎰\n{frame}",
                    chat_id=message.chat.id,
                    message_id=sent.message_id
                )
                last_frame = frame

            time.sleep(1)

        probs = [g["prob"] for g in games_outcome]
        chosen = random.choices(games_outcome, weights=probs, k=1)[0]

        chosen_symbols = chosen["symbols"]
        if chosen["symbols"] is None:
            chosen_symbols = random.sample(range(len(symbols)), 3)

        emoji_frame = [symbols[i] for i in chosen_symbols]

        result_str = f"[{emoji_frame[0]}][{emoji_frame[1]}][{emoji_frame[2]}]"

        if result_str != last_frame:
            context.bot.edit_message_text(
                text=f"🎰 {user_name} Депнул {bet} 🎰\n{result_str}",
                chat_id=message.chat.id,
                message_id=sent.message_id
            )

        time.sleep(1)

        if chosen["coef"] > 0:
            coef = chosen["coef"]
            amount = math.ceil(bet * coef)

            print("Win - Coef:", coef, "Amount:", amount)

            context.bot.edit_message_text(
                text=f"🎰 {user_name} Депнул {bet} 🎰\n{result_str}\n Выигрыш: {amount} сатоши",
                chat_id=message.chat.id,
                message_id=sent.message_id
            )

            context.database.add_money(user_id, chat_id, amount)
        else:
            context.bot.edit_message_text(
                text=f"🎰 {user_name} Депнул {bet} 🎰\n{result_str}\n Просрано {bet} сатоши",
                chat_id=message.chat.id,
                message_id=sent.message_id
            )
