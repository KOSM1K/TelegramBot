import telebot

from chat_context import ChatContext


def register_gambling_leaderboard_command(context: ChatContext):
    handler_command = "leaderboard"
    handler_description = "топ игроков"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def leaderboard(message: telebot.types.Message):
        context.any_message_handler(message)

        chat_id = message.chat.id
        chat_members = context.database.all_members_of_chat(chat_id)

        if len(chat_members) == 0:
            context.bot.reply_to(message, "Пока что никого не записал :(")
            return

        content = ""
        index = 1

        players = [
            {
                "member":  context.bot.get_chat_member(chat_id, cur_user_id),
                "money": context.database.get_money(cur_user_id, chat_id)
            }
            for cur_user_id in chat_members
        ]
        players_sorted = sorted(players, key=lambda p: p["money"], reverse=True)

        for player in players_sorted:
            target_username = player["member"].user.username

            content += "{:>8}".format(
                index) + f"    {target_username} - {player["money"]} сатоши\n"

            index += 1

        message = "Самые богатые участники:\n" + content

        context.bot.send_message(chat_id, message)
