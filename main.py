import threading
import time

import telebot
import random

import multiprocessing

from telebot.types import BotCommand

from hidden import token
import json

TOKEN = token
bot = telebot.TeleBot(TOKEN)


def AddUser(chat_id, user_id):
    if chat_id not in chat_members:
        chat_members[chat_id] = list()
    if user_id not in chat_members[chat_id]:
        chat_members[chat_id].append(user_id)
        chat_members[chat_id].sort(key=lambda x: bot.get_chat_member(chat_id, x).user.username)
        print(
            f"Added user {user_id} {bot.get_chat_member(chat_id, user_id).user.username} at chat {chat_id}")


def RemoveUser(chat_id, user_id):
    if chat_id not in chat_members:
        return
    if user_id not in chat_members[chat_id]:
        return
    chat_members[chat_id].remove(user_id)
    print(
        f"Removed user {user_id} {bot.get_chat_member(chat_id, user_id).user.username} at chat {chat_id}")


@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message: telebot.types.Message):
    for new_member in message.new_chat_members:
        # if not message.from_user.is_bot:
        AddUser(message.chat.id, new_member.id)


# Обработчик для удаления участников
@bot.message_handler(content_types=['left_chat_member'])
def handle_left_member(message: telebot.types.Message):
    # if not message.from_user.is_bot:
    RemoveUser(message.chat.id, message.from_user.id)


@bot.message_handler(commands=['eval'])
def bot_eval(message: telebot.types.Message):
    run_result = []
    def evaluator(code: str):
        nonlocal run_result
        __bot_out_buff__ = []
        banned_samples = {
            "import",
            "open",
            "exec",
            "eval",
            "bultins",
            "os",
            "sys",
            "getattr",
            "system",
            "globals"
        }

        refined_code = code.replace("print", "__bot_out_buff__.append")
        # refined_code = code
        print(refined_code)
        if any(i in refined_code for i in banned_samples):
            run_result = ["бан тебе нахуй педрила, нельзя такой код писать", __bot_out_buff__]
            return
        try:
            exec(refined_code)
            run_result = ["", __bot_out_buff__]
        except Exception as e:
            run_result = [str(e), __bot_out_buff__]

    chat_id = message.chat.id
    my_message = bot.reply_to(message,
                              "Все print будут заменены на сохранение строки в буффер вывода. Ввод пока невозможен, используй переменные")

    code = None
    for i in message.entities:
        if i.type == 'pre' and i.language == 'python':
            code = message.text[i.offset: i.offset + i.length]
            break
    try:
        task_thread = threading.Thread(target=evaluator, args=(code,))
        task_thread.start()
        task_thread.join(5)

        run_result[1] = list(map(str, run_result[1]))
        run_result[1] = '\n'.join(run_result[1])
        if task_thread.is_alive():
            bot.reply_to(message,
                         f"Время исполнения истекло. Вот что успела вывести твоя программа:\n\n```out\n{run_result[1]}```",
                         parse_mode="Markdown")
        elif run_result[0] == "":
            bot.reply_to(message,
                         f"Исполнение программы завершилось успешно. Вот что успела вывести твоя программа:\n\n```out\n{run_result[1]}```",
                         parse_mode="Markdown")
        else:
            bot.reply_to(message,
                         f"Исполнение программы завершилось с ошибкой. Вот сообщение об ошибке:\n\n ```out\n{run_result[0]}``` \n\n Вот что успела вывести твоя программа:\n\n {run_result[1]}",
                         parse_mode="Markdown")
        return
    except Exception as e:
        bot.reply_to(message, f"Блять я маслину поймал:\n\n{e}")

@bot.message_handler(commands=['get_member_list'])
def send_member_list(message: telebot.types.Message):
    save_users(message)
    chat_id = message.chat.id

    is_loud = "-loud" in message.text

    if chat_id in chat_members:
        str_of_users_with_indexes = ""
        index = 0
        for cur_user_id in chat_members[chat_id]:
            if is_loud:
                str_of_users_with_indexes += "{:>8}".format(
                    index) + f"    [{bot.get_chat_member(chat_id, cur_user_id).user.username}](tg://user?id={cur_user_id}) \n"
            else:
                str_of_users_with_indexes += "{:>8}".format(
                    index) + f"    {bot.get_chat_member(chat_id, cur_user_id).user.username} \n"
            index += 1
        if is_loud:
            bot.send_message(chat_id, "Вот список всех зарегестрированных участников:\n" + str_of_users_with_indexes,
                             parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "Вот список всех зарегестрированных участников:\n" + str_of_users_with_indexes)
    else:
        bot.send_message(chat_id, "Пока что никого не записал :(")


# Команда /rand выбирает случайного участника
@bot.message_handler(commands=['random'])
def bot_random(message: telebot.types.Message):
    save_users(message)
    chat_id = message.chat.id

    is_loud = "-loud" in message.text

    mentions = [elem for elem in message.entities if elem.type == "mention"]

    if len(mentions) == 0:
        if chat_id in chat_members and chat_members[chat_id]:
            chosen_one = random.choice(list(chat_members[chat_id]))
            if is_loud:
                bot.send_message(chat_id,
                                 f"🎲 Случайный выбор: [{bot.get_chat_member(chat_id, chosen_one).user.username}](tg://user?id={chosen_one})",
                                 parse_mode="Markdown")
            else:
                bot.send_message(chat_id,
                                 f"🎲 Случайный выбор: {bot.get_chat_member(chat_id, chosen_one).user.username}")
        else:
            bot.send_message(chat_id, "Не могу выбрать никого, недостаточно данных 🫤")
    else:
        chosen_mention = random.choice(mentions)
        # chosen_mention = telebot.types.MessageEntity()
        response_msg = message.text[chosen_mention.offset:chosen_mention.offset + chosen_mention.length]

        bot.send_message(chat_id, f"Случайный выбор: {response_msg}")


@bot.message_handler(commands=['shuffle'])
def bot_shuffle(message: telebot.types.Message):
    save_users(message)
    chat_id = message.chat.id

    is_loud = "-loud" in message.text

    mentions = [elem for elem in message.entities if elem.type == "mention"]

    if len(mentions) == 0:
        if chat_id in chat_members and chat_members[chat_id]:
            chosen_order = chat_members[chat_id]
            for i in range(int(len(chosen_order) ** 0.5 + 1)):
                random.shuffle(chosen_order)
            message = "Случайный порядок:\n"
            index = 0
            for i in chosen_order:
                if is_loud:
                    message += "{:>8}".format(
                        index) + f"    [{bot.get_chat_member(chat_id, i).user.username}](tg://user?id={i}) \n"
                else:
                    message += "{:>8}".format(
                        index) + f"    {bot.get_chat_member(chat_id, i).user.username} \n"
                index += 1
            if is_loud:
                bot.send_message(chat_id,
                                 message,
                                 parse_mode="Markdown")
            else:
                bot.send_message(chat_id,
                                 message)
        else:
            bot.send_message(chat_id, "Не могу выбрать никого, недостаточно данных 🫤")
    else:
        chosen_mention = random.choice(mentions)
        # chosen_mention = telebot.types.MessageEntity()
        response_msg = message.text[chosen_mention.offset:chosen_mention.offset + chosen_mention.length]

        bot.send_message(chat_id, f"Случайный порядок: {response_msg}")


# Запоминаем участников, когда они что-то пишут
@bot.message_handler()
def save_users(message: telebot.types.Message):
    print(message)
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not message.from_user.is_bot:
        AddUser(chat_id, user_id)


if __name__ == "__main__":
    commands = [
        BotCommand("random", "Get random member from all registered, or choose one from mentioned after command"),
        BotCommand("shuffle",
                   "Get random order from all registered members, or random order of mentioned after command"),
        BotCommand("get_member_list", "Get list of all registered members"),
    ]
    try:
        bot.set_my_commands(commands)
    except Exception as e:
        print(f"failed to set commands annotation: \n\n {e}")
    try:
        chat_members_df = open("chat_members.json", mode='r')
        chat_members = json.load(chat_members_df)
        chat_members_df.close()

        # chat_members = dict()
        for key in list(chat_members.keys()):
            chat_members[int(key)] = sorted(chat_members[key], key=lambda x: bot.get_chat_member(key, x).user.username)
            chat_members.pop(key)

        print("data loaded successfully")
    except Exception as e:
        chat_members = dict()
        print(f"failed to read data: \n\n {e}")

    # bot.infinity_polling()
    try:
        bot.polling()
    except KeyboardInterrupt:
        print("manually stopped")
    except Exception as e:
        print(f"got unexpected error: \n\n {e} \n \n {str(e)}")

    try:
        chat_members_df = open("chat_members.json", mode='w')
        chat_members_df.truncate()
        json.dump(chat_members, chat_members_df, indent=4)
        chat_members_df.close()
        print("successfully dumped data")
    except Exception as e:
        print(f"data dump failed: \n\n {e}")
