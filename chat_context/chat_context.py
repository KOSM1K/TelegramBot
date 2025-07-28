import telebot
from telebot.types import BotCommand

import time

from database.bot_db import BotDatabase


class ChatContext:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self.commands = []  # Contains list of helpers for commands
        self.start_time = None
        self.database = BotDatabase()

    def add_handler_help(self, name: str, description: str):
        self.commands.append(BotCommand(name, description))

    # Workaround for handling all commands
    # Note: this command will trigger database, so it can be slow
    # Probably, we should add /register command or manually add all members
    def any_message_handler(self, message: telebot.types.Message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        self.database.add_member(user_id, chat_id)

    def launch(self):
        try:
            self.bot.set_my_commands(self.commands)
        except Exception as e:
            print(f"failed to set commands annotation: \n\n {e}")

        try:
            print("Bot launched!")
            self.start_time = time.time()
            self.bot.infinity_polling()
        except KeyboardInterrupt:
            print("manually stopped")
            self.database.close()
            return
        except Exception as e:
            print(f"got unexpected error: \n\n {e} \n \n {str(e)}")
            self.database.close()
            return

        print("We are done!")
        self.database.close()
