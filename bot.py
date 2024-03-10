import telebot
import logging as log
from config import bot_token
from gpt import get_resp, levels
from telebot.types import ReplyKeyboardMarkup
from db import create_db, insert_data, update_data, update_answer, select_data, delete_user_data, pr_db
# from db import delete_data
bot = telebot.TeleBot(bot_token)  # Введите свой токен в config.py
continue_array = ["continue", "contunie", "con", "cont", "продолжить", "продолжит"]

# log конфиг
log.basicConfig(
    level=log.INFO,
    filemode="w",
    filename="logbook.txt",
    format='%(asctime)s - %(levelname)s - %(message)s')

create_db()  # создание базы данных

# сбор стандартной клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard.add("/solve_task_math", "/solve_task_physics", "/continue", "/help")

# сбор клавиатуры для continue
cont_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cont_keyboard.add("/solve_task_math", "/solve_task_physics", "/continue", "/help", "/response")

# сбор клавиатуры старта
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
start_keyboard.add("/help")


# сбор клавиатуры выбора уровня
level_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
level_keyboard.add("Новичок", "Продвинутый")


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    reg(message)
    bot.send_message(message.chat.id, f"Привет, {select_data('name', user_id)}! Я GPT бот-помощник, "
                                      f"имитирующий учителя математики/физики!\n"
                                      "Я могу помочь вам с уравнением или объяснить физические процессы.\n"
                                      "Введите /help, чтобы получить список моих команд.\n",
                     reply_markup=start_keyboard)
    return


# Прием и обработка промтов

@bot.message_handler(commands=['solve_task_math', 'solve_task_physics'])  # команда для ввода вопроса
def solve_task_message(message):
    user_id = message.from_user.id
    delete_user_data(user_id)
    reg(message)
    if message.text == 'solve_task_math':
        subj = 'math'
    else:
        subj = 'physics'
    update_data('subject', subj, user_id)
    bot.send_message(message.chat.id, "Выберите ваш уровень.", reply_markup=level_keyboard)
    bot.register_next_step_handler(message, get_level)
    return


def get_level(message):
    user_id = message.from_user.id
    level = message.text.lower()
    if level in levels:
        update_data('level', levels[level], user_id)
        bot.send_message(message.chat.id, "Введите ваш вопрос.")
        bot.register_next_step_handler(message, get_promt)
    else:
        bot.send_message(message.chat.id, "Выберите один из предложенных уровней.", reply_markup=level_keyboard)
        bot.register_next_step_handler(message, get_level)
    return


def get_promt(message):  # получение промта и его проверка
    user_id = message.from_user.id
    if message.content_type == 'text':
        if message.text[0] != '/':
            promt = message.text
            log.info("promt received")
            update_data('task', promt, user_id)
            answer_to_promt(promt, message.chat.id, user_id, keyboard)
        else:
            bot.send_message(message.chat.id, "В данный момент команды недоступны.\n"
                                              "Введите вопрос.")
            bot.register_next_step_handler(message, get_promt)
    else:
        bot.send_message(message.chat.id, "Отправьте вопрос текстом.")
        bot.register_next_step_handler(message, get_promt)
    return


def answer_to_promt(promt, chat_id, user_id, answer_keyboard):  # ответ на промт
    prev_answ = select_data('answer', user_id)
    subj = select_data('subject', user_id)
    level = select_data('level', user_id)
    answer = get_resp(promt, prev_answ, subj, level)
    if answer != "ERROR":
        if answer != "":
            update_answer(answer, user_id)
            bot.send_message(chat_id, answer)
            bot.send_message(chat_id, "Чтобы продолжить ответ, напиши /continue", reply_markup=answer_keyboard)
        else:
            bot.send_message(chat_id, "Мне больше нечего добавить.\n"
                                      "Введите /response, чтобы увидеть полный ответ.", reply_markup=cont_keyboard)
        log.info("response received")
    else:
        bot.send_message(chat_id, "При генерации ответа на промт произошла ошибка. Попробуйте ещё раз.",
                         reply_markup=keyboard)
        log.error("No response received")
    return

####################


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "Введите /solve_task_math, чтобы задать вопрос по математике.\n"
                                      "Введите /solve_task_physics, чтобы задать вопрос по физике.\n"
                                      "Введите /continue, чтобы бот продолжил свой ответ.\n"
                                      "Введите /response, чтобы просуммировать ответ бота на заданный вопрос "
                                      "(совмещает все ответы бота в один после команды continue).",
                     reply_markup=keyboard)
    return


@bot.message_handler(commands=continue_array)  # продолжить ответ
def continue_message(message):
    user_id = message.from_user.id
    if select_data('task', user_id) != '':
        bot.send_message(message.chat.id, "Продолжаю...")
        promt = select_data('task', user_id)
        answer_to_promt(promt, message.chat.id, user_id, cont_keyboard)
    else:
        bot.send_message(message.chat.id, "Сначала вам нужно задать вопрос.")
    return


@bot.message_handler(commands=['debug'])  # Дебаг
def debug_message(message):
    bot.send_message(message.chat.id, "Отправляю логбук:")
    with open("logbook.txt", "rb") as f:
        bot.send_document(message.chat.id, f)
    return


# @bot.message_handler(commands=['del'])  # удаление базы данных
# def delete(message):
#     delete_data()
#     return


@bot.message_handler(commands=['pr'])  # вывод базы данных
def pr(message):
    pr_db()
    return


@bot.message_handler(commands=['response'])  # Показывает полный ответ
def show_complete_response(message):
    user_id = message.from_user.id
    if select_data('answer', user_id) != "":
        bot.send_message(message.chat.id, f"Суммирую ответ:\n"
                                          f"{select_data('answer', user_id)}")
    else:
        bot.send_message(message.chat.id, "Ответ пуст. Попробуйте задать вопрос.")
    return


@bot.message_handler(content_types=['text'])  # Обработка текста
def answer_to_text(message):
    bot.send_message(message.chat.id, "Выберите одну из предложенных команд", reply_markup=keyboard)
    return


def reg(message):  # Регистрация
    user_id = message.from_user.id
    if select_data('user_id', user_id) == "not found":
        insert_data(user_id)
        update_data('name', message.from_user.first_name, user_id)
        log.info(f"Запись о пользователе с id {user_id} добавлена")
    else:
        log.info("Запись уже существует")
    return


log.info("Бот запущен")
bot.polling(non_stop=True)
