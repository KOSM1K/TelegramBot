# import threading
import multiprocessing
import time

import traceback

import telebot
import random

import datetime

import json
from telebot.types import BotCommand

from hidden import token
from executor import executor

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


@bot.message_handler(commands=['exec'])
def bot_exec(message: telebot.types.Message):
    save_users(message)
    return_manager = multiprocessing.Manager()
    run_result = return_manager.list(["", return_manager.list()])

    code = None
    for i in message.entities:
        if i.type == 'pre' and i.language == 'python':
            code = message.text[i.offset: i.offset + i.length]
            break
    if code == None:
        bot.reply_to(message,
"Запущу твой код на языке python.\n\
Для отправки после комманды напиши Markdown с кодом и меткой языка python.\n\n \
```python\nprint('как-то вот так')```\n\n\
Все print будут заменены на сохранение строки в буффер вывода\n\n\
```\n(print(...) -> __bot_out_buff__.append(...))```\n\n\
Ввод пока невозможен, используй переменные",
        parse_mode="Markdown")
        return
    try:
        task_thread = multiprocessing.Process(target=executor, args=(code,run_result,))
        task_thread.start()
        task_thread.join(5)

        run_result[1] = list(map(str, run_result[1]))
        run_result[1] = '\n'.join(run_result[1])
        if task_thread.is_alive():
            task_thread.terminate()
            bot.reply_to(message,
                            f"Время исполнения истекло. Вот что успела вывести твоя программа:\n\n```out\n{run_result[1]}```",
                            parse_mode="Markdown")
            return
                
        if run_result[0] == "":
            bot.reply_to(message,
                         f"Исполнение программы завершилось успешно. Вот что успела вывести твоя программа:\n\n```out\n{run_result[1]}```",
                         parse_mode="Markdown")
        else:
            bot.reply_to(message,
                         f"Исполнение программы завершилось с ошибкой. Вот сообщение об ошибке:\n\n ```out\n{run_result[0]}``` \n\n Вот что успела вывести твоя программа:\n\n ```out\n{run_result[1]}```",
                         parse_mode="Markdown")
        return
    except Exception as e:
        bot.reply_to(message, f"Блять я маслину поймал:\n\n```{'\n'.join(list(map(str,list(traceback.extract_tb(e.__traceback__))))) + '\n' + '-|-'*10 + '\n' + str(e)}```", parse_mode="Markdown")

@bot.message_handler(commands=['get_member_list'])
def send_member_list(message: telebot.types.Message):
    save_users(message)
    chat_id = message.chat.id

    is_loud = "-loud" in message.text

    if chat_id in chat_members:
        str_of_users_with_indexes = ""
        index = 1
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


@bot.message_handler(commands=['uptime'])
def bot_uptime(message: telebot.types.Message):
    save_users(message)
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Я запущен уже {datetime.timedelta(seconds= time.time() - start_time)}")

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
            index = 1
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
        BotCommand("exec", "Run your python code!"),
        BotCommand("uptime", "For how long I have been standing?"),
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
        start_time = time.time()
        bot.infinity_polling()
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
