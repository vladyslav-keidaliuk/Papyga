import datetime
import logging
import random
import re
import signal
import threading
import time
from datetime import timedelta

import schedule
import telebot
from mysql.connector import Error
from telebot import types

import birthdays
import config
import create_tables
import database
import phrases
import spotify
import tz
import youtube_music
from birthdays import check_birthday
from database import get_quote
from phrases import mountain_phrases, mine_phrases, get_text_with_link, get_text_with_link_replied_user, \
    get_link_with_text
from what_pair_progress import what_pair

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

message_count = 0
to_unpin_message_id = None

GROUP_ID = config.GROUP_ID
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=[config.COMMAND_START])
def start(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        db_text = create_tables.create_tables()
        insert_quotes = create_tables.insert_quotes()
        insert_totems = create_tables.insert_totems()
        insert_sticker_packs = create_tables.insert_sticker_packs()
        insert_emojies = create_tables.insert_emojies()
        insert_triggers = create_tables.insert_triggers()
        hello_text = f"Вітаю, я - Папуга, буду допомагати не забувати Вам про важливі події," \
                     f" а також додам трошки фарб у буденність )\n\n" \
                     f"От Ваш GROUP_ID = [ {message.chat.id} ] ,впиши його у config.py\n\n"

        bot.send_message(message.chat.id,
                         hello_text +
                         db_text +
                         insert_quotes +
                         insert_sticker_packs +
                         insert_emojies +
                         insert_totems +
                         insert_triggers
                         )


@bot.message_handler(commands=[config.COMMAND_TIME_LEFT])
def time_left(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        today = (datetime.date.today()).strftime('%A')
        if today == "Saturday":
            if config.PAIR_OR_LESSON:
                bot.send_message(message.chat.id, "Сьогодні субота, чого ти мене питаєш за пари, йди роби лаби 👮‍♂️")
            else:
                bot.send_message(message.chat.id, "Сьогодні субота, чого ти мене питаєш за уроки, йди роби дз 👮‍♂️")
        elif today == "Sunday":
            if config.PAIR_OR_LESSON:
                bot.send_message(message.chat.id, "Сьогодні неділя, чого ти мене питаєш за пари, йди роби лаби 👮‍♂️")
            else:
                bot.send_message(message.chat.id, "Сьогодні неділя, чого ти мене питаєш за уроки, йди роби дз 👮‍♂️")
        else:

            bot.send_message(message.chat.id,
                             what_pair(),
                             reply_to_message_id=message.message_id,
                             parse_mode="HTML",
                             disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"Error in command time left: {e}")
        send_message_to_group(f"Error:{e}")


previous_number = None


def generate_random_number(a, b):
    global previous_number

    while True:
        random_number = random.randint(a, b)
        if random_number != previous_number:
            previous_number = random_number
            return random_number


@bot.message_handler(commands=[config.COMMAND_ROULETTE])
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        if message.chat.type != 'group' and message.chat.type != 'supergroup':
            bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
            return
        if message.chat.id == GROUP_ID:
            user_id = message.from_user.id
            bullet_chamber = generate_random_number(1, 6)
            data_arr = get_data_from_table(message.from_user.id)
            size = data_arr[1]
            cut_off = int((size * random.randint(5, 10)) / 100)
            if bullet_chamber == 1 or \
                    bullet_chamber == 2 or \
                    bullet_chamber == 3 or \
                    bullet_chamber == 5:
                try:
                    result = random.choice([True, False])

                    if result:
                        bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_id, can_send_messages=False,
                                                 until_date=time.time() + config.MUTE_TIME_BY_ROULETTE)
                        bot.reply_to(message,
                                     f"Ох ні, тобі не пощастило, пряме потрапляння((\n"
                                     f"Помовч тепер трохи ({int(config.MUTE_TIME_BY_ROULETTE / 60)} хвилин)")
                    else:
                        bot.reply_to(message, f"Ох ні, тобі не пощастило, пряме потрапляння((\n"
                                              f"Патрон відстрелив {cut_off} см твого байрактару((")
                        new_size = 0
                        if size < cut_off:
                            new_size = 0
                        if size >= cut_off:
                            new_size = size - cut_off
                        database.change_bayraktar_by_reel(new_size, user_id)
                except:

                    try:
                        bot.reply_to(message, f"Ох ні, тобі не пощастило, пряме потрапляння((\n"
                                              f"Патрон відстрелив {cut_off} см твого байрактару((")
                        new_size = 0
                        if size < cut_off:
                            new_size = 0
                        if size >= cut_off:
                            new_size = size - cut_off

                        database.change_bayraktar_by_reel(new_size, user_id)

                    except Error as err:
                        logging.error(f"Error in roulette db: {err}")
                    except Exception as e:
                        logging.error(f"Error in roulette: {e}")
                        send_message_to_group("Упс, щось пішло не так...\n"
                                              "(Не зміг відкусити)")
            else:
                try:
                    data_arr = get_data_from_table(message.from_user.id)
                    size = data_arr[1]

                    add = int((size * random.randint(3, 5)) / 100)
                    new_size = size + add
                    bot.reply_to(message,
                                 f"Ти щаслива людина !! Тримай поцілунок від мене 💋 та + {add} см до зброї!")

                    database.change_bayraktar_by_reel(new_size, user_id)

                except Error as err:
                    logging.error(f"Error in roulette db: {err}")
                except Exception as e:
                    logging.error(f"Error in roulette: {e}")
                    send_message_to_group("Упс, щось пішло не так...\n"
                                          "(Не зміг додати)")
        else:
            bot.send_message(message.chat.id, "Ця команда працює лише у груповому чаті.")
    except Error as err:
        logging.error(f"Error in roulette db: {err}")
    except Exception as e:
        logging.error(f"Error in roulette: {e}")
        reply_message(message, "Упс, щось пішло не так...\n"
                               "(Не зміг додати)")


def get_datetime_from_str(time_str):
    desired_hour, desired_minute = map(int, time_str.split(':'))

    now = datetime.datetime.now()
    desired_time = datetime.datetime(now.year, now.month, now.day, desired_hour, desired_minute)

    return desired_time


def happy_birthday():
    try:
        schedule.clear('birthday')
        if check_birthday():
            now = datetime.datetime.now()
            desired_time = get_datetime_from_str(config.TIME_HB)
            if now < desired_time:
                (schedule.every().day
                .at(tz.get_utc_str_hh_mm_from_str(config.TIME_HB)).do(send_message_to_group_and_pin,
                                                                      check_birthday()).tag(
                    'birthday'))
            else:
                new_time = now + datetime.timedelta(minutes=2)
                formatted_time = new_time.strftime("%H:%M")
                schedule.every().day.at(formatted_time).do(send_message_to_group, check_birthday()).tag(
                    'birthday')
    except Exception as e:
        logging.error(f"Error in happy_birthday: {e}")


def send_message_to_group(text):
    try:
        bot.send_message(GROUP_ID, text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"Error in send_message_to_group_and_pin : {e}")


def send_message_to_group_and_pin(text):
    try:
        unpin_message()
        last_message = bot.send_message(GROUP_ID, text)
        bot.pin_chat_message(GROUP_ID, last_message.message_id)
        global to_unpin_message_id
        to_unpin_message_id = last_message.message_id
        database.set_pinned_message_in_db(GROUP_ID, to_unpin_message_id)
    except Exception as e:
        logging.error(f"Error in send_message_to_group_and_pin : {e}")


def unpin_message():
    if to_unpin_message_id is None:
        pass
    else:
        bot.unpin_chat_message(GROUP_ID, to_unpin_message_id)


def schedule_message_to_group(message, send_time):
    schedule.every().day.at(send_time).do(send_message_to_group, message)


happy_birthday()


def check_timer(message, user_id, size, stop_timer, what_timer):
    try:
        now = datetime.datetime.now()
        if now < stop_timer:
            stop_timer_str = str(stop_timer + timedelta(hours=tz.get_utc_offset_hours()))[:19]
            text = get_text_with_link(message) + \
                   ", ти рано зайшов(-ла), зможеш спробувати знов після " + stop_timer_str
            return text
        elif now >= stop_timer:
            if what_timer == 0:
                database.new_try_qt(message, user_id)
                database.repeat_timer(user_id, what_timer)
            if what_timer == 1:
                database.new_try_bayraktar(user_id, size)
                database.repeat_timer(user_id, what_timer)
                return 10
            if what_timer == 2:
                database.new_try_mountain(user_id, size)
                database.repeat_timer(user_id, what_timer)
                return 20
    except Exception as e:
        logging.error(f"Error in check_timer:{e}")
        send_message_to_group("Упс, щось пішло не так...\n"
                              "(Перевірка таймеру)")


def get_data_from_table(user_id):
    try:
        res = database.db_connect()
        cursor = res[1]

        query = "SELECT * FROM Users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()

        if row:
            user_id, size, start_timer_qt, stop_timer, totem, passmountain, stop_timer_mountain, reputation, nickname = row
            data_arr = [user_id, size, start_timer_qt, stop_timer, totem, passmountain, stop_timer_mountain, reputation,
                        nickname]
            return data_arr
        else:
            return 0
    except Error as err:
        logging.error(f"Error in get_data_from_table db: {err}")
    except Exception as e:
        logging.error(f"Error in get_data_from_table: {e}")
        send_message_to_group("Упс, щось пішло не так...\n"
                              "Отримання даних з таблиці")


def reply_message(message, text):
    bot.send_message(message.chat.id,
                     text,
                     reply_to_message_id=message.message_id,
                     parse_mode="HTML",
                     disable_web_page_preview=True)


@bot.message_handler(commands=[config.COMMAND_UNPIN_BOT_MESSAGES])
def unpin_all(message):
    try:
        if message.chat.type != 'group' and message.chat.type != 'supergroup':
            bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
            return
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_info = bot.get_chat_member(chat_id, user_id)
        if user_info.status == 'administrator' or user_info.status == 'creator':
            database.unpin_and_delete_pinned_message()
            bot.reply_to(message, "Усі мої закріплені повідомлення видалені (")
        else:
            bot.reply_to(message, "В тебе нема прав на цю дію !")
    except Exception as e:
        logging.error(f"Error in unpin_all: {e}")


@bot.message_handler(commands=[config.COMMAND_WHO_I_AM])
def whoi(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.id == GROUP_ID:
        try:
            res = database.db_connect()
            cursor = res[1]
            db = res[0]

            data_arr = get_data_from_table(message.from_user.id)
            if data_arr == 0:

                text = f'{get_text_with_link(message)}, я Папуга, дивлюсь ти вперше тут.\n' \
                       f'Тут ти можеш кожні {config.TIMER_DURATION_HOURS} годин отримувати цитату дня и дізнаватись, ' \
                       f'яка твоя тотемна тварина на наступні {config.TIMER_DURATION_HOURS} годин.' \
                       f'Також ти будеш отримувати бонусом якусь пісню.'
                send_message_to_group(text)
                try:
                    new_quote = get_quote()
                    name, emoji_code = database.get_random_totem()
                    now = datetime.datetime.now()
                    date_time_stop_str = str(now + timedelta(hours=config.TIMER_DURATION_HOURS))

                    link, title, artist, playlist = spotify.get_random_track()

                    text = f"{database.get_nickname(message)}, " \
                           f"твоя тотемна тварина на наступні {config.TIMER_DURATION_HOURS} годин : {name + ' ' + database.emoji_decode(emoji_code)}\n" \
                           f"\n" \
                           f"Твоя цитата дня : {new_quote}\n" \
                           f"\n" \
                           f"\U0001F99CОсь твій трек дня\U0001F99C:\n" \
                           f"Назва треку: {title}\n" \
                           f"Виконавець: {artist}"

                    keyboard = types.InlineKeyboardMarkup()

                    button = types.InlineKeyboardButton(text="Відкрити", url=f"{link}")

                    keyboard.add(button)

                    bot.send_message(message.chat.id,
                                     text,
                                     reply_to_message_id=message.message_id,
                                     parse_mode="HTML",
                                     reply_markup=keyboard,
                                     disable_web_page_preview=True)

                    sql = "INSERT INTO Users (user_id,stop_timer_qt,totem) VALUES (%s,%s,%s)"
                    val = (message.from_user.id, date_time_stop_str, name + ' ' + emoji_code)
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                except Error as err:
                    bot.reply_to(message, f"Виникла помилка у БД : {err}")
                    logging.error(f"Error in whoi db if data_arr == 0: {err}")
                except Exception as e:
                    logging.error(f"Error in whoi if data_arr == 0: {e}")
                    bot.reply_to(message, f"Виникла помилка : {e}")

            elif data_arr[4] == None:
                text = f'{get_text_with_link(message)}, я Папуга 2.0, дивлюсь ти вперше тут.\n' \
                       f'Тут ти можеш кожні {config.TIMER_DURATION_HOURS} годин отримувати цитату дня и дізнаватись, ' \
                       f'яка твоя тотемна тварина на наступні {config.TIMER_DURATION_HOURS} годин.'
                reply_message(message, text)
                try:
                    name, emoji_code = database.get_random_totem()
                    new_quote = get_quote()
                    now = datetime.datetime.now()
                    date_time_stop_str = str(now + timedelta(hours=config.TIMER_DURATION_HOURS))
                    link, title, artist, playlist = spotify.get_random_track()

                    text = f"{database.get_nickname(message)}, " \
                           f"твоя тотемна тварина на наступні {config.TIMER_DURATION_HOURS} годин : {name + ' ' + database.emoji_decode(emoji_code)}\n" \
                           f"\n" \
                           f"Твоя цитата дня : {new_quote}\n" \
                           f"\n" \
                           f"\U0001F99CОсь твій трек дня\U0001F99C:\n" \
                           f"Назва треку: {title}\n" \
                           f"Виконавець: {artist}"

                    keyboard = types.InlineKeyboardMarkup()

                    button = types.InlineKeyboardButton(text="Відкрити", url=f"{link}")

                    keyboard.add(button)

                    bot.send_message(message.chat.id,
                                     text,
                                     reply_to_message_id=message.message_id,
                                     parse_mode="HTML",
                                     reply_markup=keyboard,
                                     disable_web_page_preview=True)

                    query = "UPDATE Users SET stop_timer_qt= %s, totem = %s WHERE user_id = %s"
                    values = (date_time_stop_str, name + ' ' + emoji_code, message.from_user.id)
                    cursor.execute(query, values)
                    db.commit()
                    cursor.close()
                    db.close()
                except Error as err:
                    bot.reply_to(message, f"Виникла помилка у БД : {err}")
                    logging.error(f"Error in whoi db if data_arr[4] == None: {err}")
                except Exception as e:
                    logging.error(f"Error in whoi if data_arr[4] == None: {e}")
                    bot.reply_to(message, f"Виникла помилка : {e}")
            else:
                data_arr = get_data_from_table(message.from_user.id)
                size = data_arr[1]
                stop_timer_qt = data_arr[2]
                totem = data_arr[4]
                passmountain = data_arr[5]

                text_from_timer = check_timer(message, message.from_user.id, size, stop_timer_qt, 0)

                data_arr = get_data_from_table(message.from_user.id)
                size = data_arr[1]
                stop_timer_qt = data_arr[2]
                totem = data_arr[4]
                nickname = data_arr[8]

                if text_from_timer is None:
                    logging.info("text_from_timer is None")
                    cursor.close()
                    db.close()

                else:
                    if passmountain >= config.MOUNTAIN_HEIGHT:
                        text = 'ТВІЙ ПРОФІЛЬ\n' \
                               f'||\U000026F0СКЕЛЕЛАЗ||\n' \
                               f'👑ЦАР ГОРИ👑\n' \
                               f'ФІО : {get_text_with_link(message)}\n' \
                               f'НІК : {get_link_with_text(message, nickname)}\n' \
                               f'Балів репутації : {database.get_reputation(message.from_user.id)}\n' \
                               f'Розмір причандала : {size} cм\n' \
                               f'Тотемна тварина : {database.get_emoji_from_text_with_text(totem)}\n' \
                               f'Пройдено гори\U000026F0 : {passmountain} м\n' \
                               f'\nP.S. : {text_from_timer}'
                    elif passmountain >= 0:
                        text = 'ТВІЙ ПРОФІЛЬ\n' \
                               f'||\U000026F0СКЕЛЕЛАЗ||\n' \
                               f'ФІО : {get_text_with_link(message)}\n' \
                               f'НІК : {get_link_with_text(message, nickname)}\n' \
                               f'Балів репутації : {database.get_reputation(message.from_user.id)}\n' \
                               f'Розмір причандала : {size} cм\n' \
                               f'Тотемна тварина : {database.get_emoji_from_text_with_text(totem)}\n' \
                               f'Пройдено гори\U000026F0 : {passmountain} м\n' \
                               f'\nP.S. : {text_from_timer}'
                    elif passmountain <= -config.MOUNTAIN_HEIGHT:
                        text = 'ТВІЙ ПРОФІЛЬ\n' \
                               '||\U000026CFШАХТАР||\n' \
                               '||\U0001FA96ГОЛОВНОКОМАНДУВАЧ\U0001FA96||\n' \
                               f'ФІО : {get_text_with_link(message)}\n' \
                               f'НІК : {get_link_with_text(message, nickname)}\n' \
                               f'Балів репутації : {database.get_reputation(message.from_user.id)}\n' \
                               f'Розмір причандала : {size} cм\n' \
                               f'Тотемна тварина : {database.get_emoji_from_text_with_text(totem)}\n' \
                               f'Пройдено шахти\U000026CF : {abs(passmountain)} м\n' \
                               f'\nP.S. : {text_from_timer}'
                    elif passmountain < 0:
                        text = 'ТВІЙ ПРОФІЛЬ\n' \
                               '||\U000026CFШАХТАР||\n' \
                               f'ФІО : {get_text_with_link(message)}\n' \
                               f'НІК : {get_link_with_text(message, nickname)}\n' \
                               f'Балів репутації : {database.get_reputation(message.from_user.id)}\n' \
                               f'Розмір причандала : {size} cм\n' \
                               f'Тотемна тварина : {database.get_emoji_from_text_with_text(totem)}\n' \
                               f'Пройдено шахти\U000026CF : {abs(passmountain)} м\n' \
                               f'\nP.S. : {text_from_timer}'
                    reply_message(message, text)
                    cursor.close()
                    db.close()
        except Error as err:
            logging.error(f"Error in whoi db: {err}")
        except Exception as e:
            send_message_to_group(f"Упс, щось пішло не так...\n"
                                  f"Помилка: {e}")
            logging.error(f"Error in whoi: {e}")
    else:
        bot.send_message(message.chat.id, "Ця команда працює лише у груповому чаті.")


@bot.message_handler(commands=[config.COMMAND_UPGRADE_BAYRAKTAR])
def upgrade(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.id == GROUP_ID:
        try:
            user_id = message.from_user.id
            res = database.db_connect()
            cursor = res[1]
            db = res[0]

            query = "SELECT * FROM Users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            if row:
                user_id, size_last, start_timer_last, stop_timer_last, totem, passmountain, stop_timer_mountain, reputation, nickname = row

                if size_last == None:
                    now = datetime.datetime.now()

                    size = str(random.randint(1, 17))

                    date_time_stop = str(now + timedelta(hours=config.TIMER_DURATION_HOURS))[:19]

                    send_message_to_group(
                        "Привіт, " + get_text_with_link(message) +
                        ", я Папуга, ти тільки-но зайшов(-ла) у режим, "
                        "де справжні хлопці та дівчата міряються своєю зброєю."
                    )

                    reply_message(message, (get_text_with_link(message) + ", твій байрактар : " + size + " см"))
                    try:
                        query = "UPDATE Users SET size = %s, stop_timer = %s WHERE user_id = %s"
                        values = (size, date_time_stop, user_id)
                        cursor.execute(query, values)

                        db.commit()

                    except Error as err:
                        bot.reply_to(message, f"Виникла помилка у БД : {err}")
                        logging.error(f"Error in upgrade db: {err}")
                    except Exception as e:
                        logging.error(f"Error in upgrade: {e}")
                        bot.reply_to(message, f"Виникла помилка : {e}")
                else:
                    status = check_timer(message, user_id, size_last, stop_timer_last, 1)

                    data_arr = get_data_from_table(user_id)
                    size = data_arr[1]

                    if len(str(status)) > 15:
                        reply_message(message, status)

                    if status == 10:
                        if size > size_last:
                            text = get_text_with_link(message) + \
                                   ', ти сьогодні добряче попрацював(-ла) руками та отримав ' \
                                   'свої ' + str(size - size_last) + ' cм. ' \
                                                                     'Тепер твій байрактар ' + str(
                                size) + ' см. Продовжуй сумлінно працювати!'
                            reply_message(message, text)
                        elif size < size_last:
                            text = get_text_with_link(message) + ', сьогодні папуга віддзьобала ' + str(
                                size_last - size) + ' cм твого ' \
                                                    'причандала. ' \
                                                    'Тепер твій байрактар ' + str(
                                size) + ' см. ЗСУ помстить найближчим часом!'
                            reply_message(message, text)
                        elif size == size_last:
                            text = get_text_with_link(message) + ', твій байрактар мов камінь. Не зрушився ні на см і ' \
                                                                 'складає ' + str(size) + ' см.'
                            reply_message(message, text)

            else:
                now = datetime.datetime.now()
                size = str(random.randint(1, 17))
                date_time_stop = str(now + timedelta(hours=config.TIMER_DURATION_HOURS))[:19]

                send_message_to_group("Привіт, " + get_text_with_link(message) +
                                      ", ти тільки-но зайшов(-ла) у режим, "
                                      "де справжні хлопці та дівчата міряються своєю зброєю."
                                      )
                reply_message(message, (get_text_with_link(message) + ", твій байрактар : " + size + " см"))
                try:
                    sql = "INSERT INTO Users (user_id,size,stop_timer) VALUES (%s, %s,%s)"
                    val = (user_id, size, date_time_stop)
                    cursor.execute(sql, val)

                    db.commit()
                except Error as err:
                    bot.reply_to(message, f"Виникла помилка у БД : {err}")
                    logging.error(f"Error in upgrade db: {err}")
                except Exception as e:
                    logging.error(f"Error in upgrade: {e}")
                    bot.reply_to(message, f"Виникла помилка : {e}")

            db.commit()
            cursor.close()
            db.close()

        except Error as err:
            bot.reply_to(message, f"Виникла помилка у БД : {err}")
            logging.error(f"Error in upgrade db: {err}")
        except Exception as e:
            logging.error(f"Error in upgrade: {e}")
            bot.reply_to(message, f"Виникла помилка : {e}")
    else:
        bot.send_message(message.chat.id, "Ця команда працює лише у груповому чаті.")


@bot.message_handler(commands=[config.COMMAND_MOUNTAIN_AND_THE_MINE])
def iwannadie(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.id == GROUP_ID:
        try:
            user_id = message.from_user.id

            res = database.db_connect()
            cursor = res[1]
            db = res[0]

            query = "SELECT * FROM Users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            if row:
                (user_id, size_last, start_timer_qt, stop_timer_last, totem, passmountain_last,
                 stop_timer_mountain_last, reputation, nickname) = row

                if passmountain_last is None:
                    now = datetime.datetime.now()

                    passmountain = str(random.randint(1, 12))

                    date_time_stop = str(now + timedelta(hours=config.TIMER_DURATION_HOURS))[:19]

                    send_message_to_group(
                        f"Привіт, " + get_text_with_link(message) +
                        f", я Папуга, ти тільки-но зайшов(-ла) у режим, "
                        f"де справжні скелелази намагаються подолати гору заввишки {config.MOUNTAIN_HEIGHT} м."
                    )

                    reply_message(message,
                                  (get_text_with_link(message) + " ти подолав(-ла) гору на : " + passmountain + " м"))
                    try:
                        query = "UPDATE Users SET passmountain = %s, stop_timer_mountain = %s WHERE user_id = %s"
                        values = (passmountain, date_time_stop, user_id)
                        cursor.execute(query, values)

                        db.commit()
                    except Error as err:
                        bot.reply_to(message, f"Виникла помилка у БД : {err}")
                        logging.error(f"Error in iwannadie db: {err}")
                    except Exception as e:
                        logging.error(f"Error in iwannadie: {e}")
                        bot.reply_to(message, f"Виникла помилка : {e}")

                else:
                    status = check_timer(message, user_id, passmountain_last, stop_timer_mountain_last, 2)

                    data_arr = get_data_from_table(user_id)
                    passmountain = data_arr[5]
                    if len(str(status)) > 15:
                        reply_message(message, status)

                    if status == 20:
                        if passmountain >= 0:
                            reply_message(message, (mountain_phrases(message, passmountain, passmountain_last)))
                        elif passmountain < 0:
                            reply_message(message, (mine_phrases(message, passmountain, passmountain_last)))
            else:
                now = datetime.datetime.now()
                passmountain = str(random.randint(1, 12))

                date_time_stop = str(now + timedelta(hours=config.TIMER_DURATION_HOURS))[:19]

                send_message_to_group(
                    f"Привіт, " + get_text_with_link(message) +
                    f", я Папуга, ти тільки-но зайшов(-ла) у режим, "
                    f"де справжні скелелази намагаються подолати гору заввишки {config.MOUNTAIN_HEIGHT} м."
                )
                reply_message(message,
                              (get_text_with_link(message) + " ти подолав(-ла) гору на : " + passmountain + " м"))
                try:
                    sql = "INSERT INTO Users (user_id,passmountain,stop_timer_mountain) VALUES (%s, %s,%s)"
                    val = (user_id, passmountain, date_time_stop)
                    cursor.execute(sql, val)

                    db.commit()
                except Error as err:
                    bot.reply_to(message, f"Виникла помилка у БД : {err}")
                    logging.error(f"Error in iwannadie db: {err}")
                except Exception as e:
                    logging.error(f"Error in iwannadie: {e}")
                    bot.reply_to(message, f"Виникла помилка : {e}")

            db.commit()
            cursor.close()
            db.close()
        except Error as err:
            bot.reply_to(message, f"Виникла помилка у БД : {err}")
            logging.error(f"Error in iwannadie db: {err}")
        except Exception as e:
            logging.error(f"Error in iwannadie: {e}")
            bot.reply_to(message, f"Виникла помилка : {e}")
    else:
        bot.send_message(message.chat.id, "Ця команда працює лише у груповому чаті.")


@bot.message_handler(commands=[config.COMMAND_TOP_BAYRAKTAR])
def top(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.top(message)


@bot.message_handler(commands=[config.COMMAND_TOP_MOUNTAIN_AND_THE_MINE])
def top_mountain(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.top_mountain(message)


@bot.message_handler(func=lambda message: message.text.lower() == config.HANDLER_SMART)
def nerd_user(message):
    if message.reply_to_message:
        response = f"🤓"
        bot.send_message(message.chat.id,
                         response,
                         reply_to_message_id=message.reply_to_message.message_id,
                         parse_mode="HTML", disable_web_page_preview=True)
    else:
        pass


@bot.message_handler(func=lambda message: message.text.lower() == config.HANDLER_WHO_YOU)
def who_you(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        if message.chat.type != 'group' and message.chat.type != 'supergroup':
            bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
            return
        if message.reply_to_message:

            if message.reply_to_message.from_user.is_bot:
                bot.send_message(message.chat.id,
                                 "Це бот, неможливо отримати інформацію про нього.",
                                 reply_to_message_id=message.reply_to_message.message_id,
                                 parse_mode="HTML", disable_web_page_preview=True)
            else:
                response = get_profile_replied_user(message)
                bot.send_message(message.chat.id,
                                 response,
                                 reply_to_message_id=message.reply_to_message.message_id,
                                 parse_mode="HTML", disable_web_page_preview=True)
        else:
            send_message_to_group("Треба надсилати у відповідь користувачеві.")
    except Exception as e:
        logging.error(f"Error in who_you: {e}")
        reply_message(message, f"Виникла помилка: {e}")


def create_interaction_handler(action_text, reaction_text):
    @bot.message_handler(func=lambda message: message.text.lower().replace(" ", "").startswith(action_text.lower()))
    def interaction_handler(message):
        database.interaction_handler(action_text, reaction_text, message)


triggers = database.get_triggers_from_db()
for trigger in triggers:
    action_text = trigger[0].strip().replace(" ", "")
    reaction_text = trigger[1]
    create_interaction_handler(action_text, reaction_text)


def get_profile_replied_user(message):
    data_arr = get_data_from_table(message.reply_to_message.from_user.id)
    size = data_arr[1]
    totem = data_arr[4]
    passmountain = data_arr[5]
    nickname = data_arr[8]

    text = ""

    if passmountain >= 300:
        text = f'ПРОФІЛЬ {get_link_with_text(message.reply_to_message, nickname)}\n' \
               f'||\U000026F0СКЕЛЕЛАЗ||\n' \
               f'👑ЦАР ГОРИ👑\n' \
               f'ФІО : {get_text_with_link_replied_user(message)}\n' \
               f'НІК : {get_link_with_text(message.reply_to_message, nickname)}\n' \
               f'Балів репутації : {database.get_reputation(message.reply_to_message.from_user.id)}\n' \
               f'Розмір причандала : {size} cм\n' \
               f'Тотемна тварина : {database.get_emoji_from_text_with_text(totem)}\n' \
               f'Пройдено гори\U000026F0 : {passmountain} м\n'
    elif passmountain >= 0:
        text = f'ПРОФІЛЬ {get_link_with_text(message.reply_to_message, nickname)}\n' \
               f'||\U000026F0СКЕЛЕЛАЗ||\n' \
               f'ФІО : {get_text_with_link_replied_user(message)}\n' \
               f'НІК : {get_link_with_text(message.reply_to_message, nickname)}\n' \
               f'Балів репутації : {database.get_reputation(message.reply_to_message.from_user.id)}\n' \
               f'Розмір причандала : {size} cм\n' \
               f'Тотемна тварина : {database.get_emoji_from_text_with_text(totem)}\n' \
               f'Пройдено гори\U000026F0 : {passmountain} м\n'

    if passmountain <= -300:
        text = f'ПРОФІЛЬ {get_link_with_text(message.reply_to_message, nickname)}\n' \
               '||\U000026CFШАХТАР||\n' \
               '||\U0001FA96ГОЛОВНОКОМАНДУВАЧ\U0001FA96||\n' \
               f'ФІО : {get_text_with_link_replied_user(message)}\n' \
               f'НІК : {get_link_with_text(message.reply_to_message, nickname)}\n' \
               f'Балів репутації : {database.get_reputation(message.reply_to_message.from_user.id)}\n' \
               f'Розмір причандала : {size} cм\n' \
               f'Тотемна тварина : {database.get_emoji_from_text_with_text(totem)}\n' \
               f'Пройдено шахти\U000026CF : {abs(passmountain)} м\n'
    elif passmountain < 0:
        text = f'ПРОФІЛЬ {get_link_with_text(message.reply_to_message, nickname)}\n' \
               '||\U000026CFШАХТАР||\n' \
               f'ФІО : {get_text_with_link_replied_user(message)}\n' \
               f'НІК : {get_link_with_text(message.reply_to_message, nickname)}\n' \
               f'Балів репутації : {database.get_reputation(message.reply_to_message.from_user.id)}\n' \
               f'Розмір причандала : {size} cм\n' \
               f'Тотемна тварина : {database.get_emoji_from_text_with_text(totem)}\n' \
               f'Пройдено шахти\U000026CF : {abs(passmountain)} м\n'
    return text


def get_username(user_id):
    try:
        chat_member = bot.get_chat_member(GROUP_ID, user_id)
        username = chat_member.user.username
        return username
    except Exception as e:
        logging.error(f"Помилка отримання нікнейма від юзера{user_id}: {e}")
        return None


@bot.message_handler(commands=[config.COMMAND_GET_TRACK])
def music(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        keyboard = types.InlineKeyboardMarkup()
        link, title, artist, playlist = spotify.get_random_track()

        text_on_button = ""
        if 'spotify' in link:
            text_on_button = "Відкрити у Spotify"
        elif 'youtube' in link:
            text_on_button = "Відкрити у YouTube Music"
        else:
            text_on_button = link

        button = types.InlineKeyboardButton(text=text_on_button, url=f"{link}")

        keyboard.add(button)

        bot.reply_to(message,
                     f"\U0001F99CОсь тобі новий трек\U0001F99C:\n"
                     f"_Плейлист : {playlist}_\n"
                     f"Назва треку: *{title}*\n"
                     f"Виконавець: *{artist}*", parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Error in music: {e}")
        reply_message(message, f"Помилка: {e}")


@bot.message_handler(commands=[config.COMMAND_ALARM])
def mention_all_users(message):
    res = database.db_connect()
    cursor = res[1]
    db = res[0]

    try:
        if message.chat.type != 'group' and message.chat.type != 'supergroup':
            bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
            return

        chat_id = message.chat.id
        query = "SELECT user_id FROM Users"
        cursor.execute(query)
        user_rows = cursor.fetchall()

        users = [row[0] for row in user_rows]

        mentions_str = ""
        for user_id in users:
            mentions_str += f' <a href="tg://user?id={user_id}">{get_username(user_id)}</a> '

        bot.send_message(chat_id, f"УВАГА!!! {mentions_str}\nВАС КЛИЧЕ @{message.from_user.username}",
                         parse_mode='HTML')

    except Error as e:
        logging.error(f"Error in mention_all_users db: {e}")
        bot.reply_to(message, f"Щось не так з БД: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@bot.message_handler(commands=[config.COMMAND_ALL_TASKS])
def get_all_tasks(message):
    bot.send_chat_action(message.chat.id, 'typing')
    chat_id = message.chat.id
    res = database.db_connect()
    cursor = res[1]
    db = res[0]
    try:
        if message.chat.type != 'group' and message.chat.type != 'supergroup':
            bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
            return

        query = "SELECT * FROM tasks"
        cursor.execute(query)
        rows = cursor.fetchall()

        days_of_week = {
            0: "Кожен день",
            1: "Понеділок",
            2: "Вівторок",
            3: "Середа",
            4: "Четвер",
            5: "П'ятниця",
            6: "Субота",
            7: "Неділя"
        }

        day_groups = {day: [] for day in range(8)}

        if rows:
            for row in rows:
                task_id = row[0]
                day = row[1]
                time = row[2]
                text = row[3]
                pairness = row[4]

                day_name = days_of_week[day]
                entry = f"*[ID: {task_id}]*\nЧас: _{time}_\nТекст: {text}\nПарність: {pairness}\n"
                day_groups[day].append(entry)

            formatted_tasks = ""
            current_message_length = 0

            for day in range(8):
                day_name = days_of_week[day]
                tasks_for_day = day_groups[day]

                if tasks_for_day:
                    sorted_tasks = sorted(tasks_for_day, key=lambda x: x.split("\nЧас: ")[1])
                    day_tasks = "\n".join(sorted_tasks)
                    formatted_day_tasks = f"*||{day_name}||*:\n{day_tasks}=========\n\n"

                    if current_message_length + len(formatted_day_tasks) <= 3800:
                        formatted_tasks += formatted_day_tasks
                        current_message_length += len(formatted_day_tasks)
                    else:
                        bot.send_message(chat_id, formatted_tasks, parse_mode="Markdown")
                        formatted_tasks = formatted_day_tasks
                        current_message_length = len(formatted_day_tasks)
            if formatted_tasks:
                bot.send_message(chat_id, formatted_tasks, parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "Нагадувань нема в БД.")
        else:
            bot.send_message(chat_id, "Нагадувань нема в БД.")
    except Error as e:
        logging.error(f"Error in get_all_tasks db: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in get_all_tasks : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@bot.message_handler(commands=[config.COMMAND_ALL_TOTEMS])
def get_totems(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.get_all_totems(message)


@bot.message_handler(commands=[config.COMMAND_ALL_EMOJIES])
def get_emojies(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.get_all_emojies(message)


@bot.message_handler(commands=[config.COMMAND_ALL_TRIGGERS])
def get_triggers(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.get_all_triggers(message)


@bot.message_handler(commands=[config.COMMAND_ALL_INTERVALS])
def get_all_intervals(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    chat_id = message.chat.id
    res = database.db_connect()
    cursor = res[1]
    db = res[0]
    try:
        query = "SELECT * FROM intervals"
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            max_message_length = 3800
            interval_info = []
            counter = 1

            for row in rows:
                interval_id = row[0]
                start = row[1]
                end = row[2]
                interval_entry = f"Порядковий номер: [{interval_id}]\nПочаток: {start}\nКінець: {end}"
                interval_info.append(interval_entry)
                counter += 1

            combined_message = ""
            current_length = 0

            for entry in interval_info:
                entry_str = entry + "\n\n"
                entry_length = len(entry_str)

                if current_length + entry_length <= max_message_length:
                    combined_message += entry_str
                    current_length += entry_length
                else:
                    bot.send_message(chat_id, combined_message)
                    combined_message = entry_str
                    current_length = entry_length

            if combined_message:
                bot.send_message(chat_id, combined_message)
            else:
                bot.send_message(chat_id, "Нема жодного інтервалу.")
        else:
            bot.send_message(chat_id, "Нема жодного інтервалу.")
    except Error as e:
        logging.error(f"Error in get_all_intervals db: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in get_all_intervals: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        cursor.close()
        db.close()


@bot.message_handler(commands=[config.COMMAND_ALL_BIRTHDAYS])
def get_all_birthdays(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    birthdays.get_all_birthdays(message)


@bot.message_handler(commands=[config.COMMAND_ALL_PLAYLISTS])
def get_all_playlists(message):
    bot.send_chat_action(message.chat.id, 'typing')

    chat_id = message.chat.id
    res = database.db_connect()
    cursor = res[1]
    db = res[0]

    try:

        query = "SELECT * FROM playlists"
        cursor.execute(query)
        rows = cursor.fetchall()

        max_message_length = 3800
        playlist_info = f"Загальна кількість треків: {spotify.get_count_tracks()}\n\nІнформація про плейлисти:\n\n"
        current_message_length = len(playlist_info)
        playlist_info_messages = []

        for row in rows:
            playlist_id = row[0]
            playlist_title = row[1]
            playlist_datetime = row[2]

            playlist_info_entry = f"|{playlist_id}| : {playlist_title}  [{playlist_datetime}]\n"
            entry_length = len(playlist_info_entry)

            if current_message_length + entry_length <= max_message_length:
                playlist_info += playlist_info_entry
                current_message_length += entry_length
            else:
                playlist_info_messages.append(playlist_info)
                playlist_info = playlist_info_entry
                current_message_length = len(playlist_info)

        if playlist_info:
            playlist_info_messages.append(playlist_info)

        for playlist_info_message in playlist_info_messages:
            bot.send_message(chat_id, playlist_info_message)

    except Error as e:
        logging.error(f"Error in get_all_playlists db : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in get_all_playlists : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")

    cursor.close()
    db.close()


@bot.message_handler(func=lambda message: config.BOT_USERNAME in message.text)
def send_random_number(message):
    if len(message.text) > len(config.BOT_USERNAME):
        if message.chat.id == GROUP_ID:
            database.send_random_number(message)
        else:
            bot.send_message(message.chat.id, "Ця команда працює лише у груповому чаті.")
    else:
        bot.reply_to(message, "Так, брате (сестро), я тут, поки що живий\U0001FAE0")


@bot.message_handler(func=lambda message: message.text.lower().startswith("папуга"))
def reply_to_papyga(message):
    bot.send_chat_action(message.chat.id, 'typing')
    phrase = random.choice(phrases.papyga_phrases)
    bot.reply_to(message, phrase)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.CHANGE_NICKNAME))
def set_nick(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.set_nick(message)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.CREATE_TASK))
def create_task_handler(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    create_task(message)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.ADD_INTERVAL))
def add_interval_handler(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    add_interval(message)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.ADD_TOTEM))
def add_totem_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.add_totem(message)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.ADD_TRIGGER))
def add_trigger_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.add_trigger(message)


@bot.message_handler(
    func=lambda message: message.text.lower().startswith(config.ADD_PLAYLIST))
def add_playlist(message):
    try:
        if message.chat.type != 'group' and message.chat.type != 'supergroup':
            bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
            return
        bot.send_chat_action(message.chat.id, 'typing')
        data = message.text.split('\n')
        playlist_link = data[1]
        text = ""
        if 'spotify.com/playlist' in playlist_link:
            text = spotify.insert_tracks_in_db(message)
        elif 'music.youtube.com/playlist' in playlist_link:
            text = youtube_music.insert_tracks_in_db(message)
        else:
            text = "Посилання даного типу не підтримується."

        reply_message(message, text)
    except Exception as e:
        logging.error(f"Error in add_playlist: {e}")
        reply_message(message, f"Помилка якась сталась: {e}")


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.DELETE_TASK))
def delete_task(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        if message.chat.type != 'group' and message.chat.type != 'supergroup':
            bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
            return
        user_id = message.from_user.id
        data = message.text.split('\n')
        id_row = data[1]

        try:
            res = database.db_connect()
            cursor = res[1]
            db = res[0]

            delete_query = "DELETE FROM tasks WHERE id = %s"
            cursor.execute(delete_query, (id_row,))
            db.commit()

            drop_column_query = "ALTER TABLE tasks DROP COLUMN id"
            cursor.execute(drop_column_query)
            db.commit()

            add_column_query = "ALTER TABLE tasks ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
            cursor.execute(add_column_query)
            db.commit()

            cursor.close()
            db.close()

            refresh_schedule()

            bot.reply_to(message, f"Завдання успішно видалено. Розклад оновлено.")

        except Error as e:
            logging.error(f"Error in delete_task db: {e}")
            bot.reply_to(message, f"Проблема якась : {e}")

    except Exception as e:
        logging.error(f"Error in delete_task : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.DELETE_TOTEM))
def delete_totem(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.delete_totem(message)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.DELETE_EMOJI_BY_INDEX))
def delete_emoji(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.delete_emoji_by_index(message)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.DELETE_TRIGGER))
def delete_trigger(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    database.delete_trigger(message)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.DELETE_INTERVAL))
def delete_interval(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    try:
        data = message.text.split('\n')
        id_row = data[1]

        try:
            res = database.db_connect()
            cursor = res[1]
            db = res[0]

            delete_query = "DELETE FROM intervals WHERE id = %s"
            cursor.execute(delete_query, (id_row,))
            db.commit()

            drop_column_query = "ALTER TABLE intervals DROP COLUMN id"
            cursor.execute(drop_column_query)
            db.commit()

            add_column_query = "ALTER TABLE intervals ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
            cursor.execute(add_column_query)
            db.commit()

            cursor.close()
            db.close()

            bot.reply_to(message, f"Інтервал успішно видалено.")

        except Error as e:
            logging.error(f"Error in delete_task db: {e}")
            bot.reply_to(message, f"Проблема якась : {e}")

    except Exception as e:
        logging.error(f"Error in delete_task : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.ADD_BIRTHDAY))
def add_birthday(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    birthdays.add_birthday(message)


@bot.message_handler(func=lambda message: message.text.lower().startswith(config.DELETE_BIRTHDAY))
def delete_birthday(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, "Ця функція доступна тільки у групових чатах.")
        return
    birthdays.delete_birthday(message)


def create_task(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        user_id = message.from_user.id
        data = message.text.split('\n')
        day = data[1]
        time = data[2]
        text = '\n'.join(data[3:-1])
        pairness = data[-1]

        if validate_time_format(time) and day.isdigit() and pairness.isdigit():
            day = int(day)
            pairness = int(pairness)
            if 0 <= day <= 7 and 0 <= pairness <= 2:
                try:
                    res = database.db_connect()
                    cursor = res[1]
                    db = res[0]

                    sql = "INSERT INTO tasks (day, time, text, pairness ) VALUES (%s, %s, %s, %s)"
                    data = (int(day), time, text, int(pairness))

                    cursor.execute(sql, data)

                    db.commit()
                    cursor.close()
                    db.close()

                    refresh_schedule()

                    bot.reply_to(message, f"Завдання успішно додано, розклад оновлено")

                except Error as e:
                    logging.error(f"Error in create_task db : {e}")
                    bot.reply_to(message, f"Трабли з записом у БД {e}")
            else:
                logging.warning(f"Warning in create_task: Out of range (day)")
                bot.reply_to(message, f"Помилка!\n"
                                      f"1) День може бути в діапазоні від 0 до 7 включно.\n"
                                      f"2) Парність може бути в діапазоні від 0 до 2 включно.")
        else:
            logging.warning(f"Warning in create_task: Incorrect time or day not digit")
            bot.reply_to(message, f"Помилка!\n"
                                  f"1) Час має бути у форматі ГГ:ХХ.\n"
                                  f"2) День має бути цілим додатним числом.\n"
                                  f"3) Парність має бути цілим додатним числом")
    except Exception as e:
        logging.error(f"Error in create_task: {e}")
        bot.reply_to(message, "Ти щось не так записав, або якась проблема виникла.Спробуй ще раз.")


def validate_time_format(time_str):
    pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    return bool(pattern.match(time_str))


def add_interval(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        data = message.text.split('\n')
        start = data[1]
        end = data[2]

        if validate_time_format(start) == True and validate_time_format(end) == True:
            start_hour, start_minute = map(int, start.split(':'))
            end_hour, end_minute = map(int, end.split(':'))
            if start_hour < end_hour or (start_hour == end_hour and start_minute < end_minute):
                try:
                    res = database.db_connect()
                    cursor = res[1]
                    db = res[0]

                    sql = "INSERT INTO intervals (start, end) VALUES (%s, %s)"
                    data = (start, end)

                    cursor.execute(sql, data)

                    db.commit()
                    cursor.close()
                    db.close()

                    bot.reply_to(message, f"Інтервал додано.")

                except Error as e:
                    logging.error(f"Error in add_interval db : {e}")
                    bot.reply_to(message, f"Трабли з записом у БД {e}")
            else:
                bot.reply_to(message, f"Кінцевий час повинен бути пізніше початкового часу.")
        else:
            bot.reply_to(message, f"Неправильний формат запису часу.\n"
                                  f"Формат: HH:MM\n"
                                  f"Наприклад: 05:08")

    except Exception as e:
        logging.error(f"Error in add_interval: {e}")
        bot.reply_to(message, "Ти щось не так записав, або якась проблема виникла.Спробуй ще раз.")


schedule_thread = None
stop_schedule_flag = False


def create_schedule_from_table():
    try:

        schedule.every().day.at(tz.get_utc_str_hh_mm_from_str(config.TIME_HB_TASKS_CHECK)).do(happy_birthday)

        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        query = "SELECT day, time, text,pairness FROM tasks"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            day = row[0]
            time_str = row[1]
            text = row[2]
            pairness = row[3]

            my_date = datetime.date(time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)
            year, week_num, day_of_week = my_date.isocalendar()
            week_shedule = week_num - config.START_OF_STUDY_WEEK_NUMBER+1

            task_time = datetime.datetime.strptime(time_str, "%H:%M")
            time_utc = tz.to_utc_from_str(time_str)  # Для хостингу
            time_utc = time_utc.strftime("%H:%M")  # Для хостингу

            if week_shedule % 2 == 0 and pairness == 2:
                if day == 0:
                    # schedule.every().day.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                         text)  # Локально
                    schedule.every().day.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 1:
                    # schedule.every().monday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().monday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 2:
                    # schedule.every().tuesday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                             text)  # Локально
                    schedule.every().tuesday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 3:
                    # schedule.every().wednesday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                               text)  # Локально
                    schedule.every().wednesday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 4:
                    # schedule.every().thursday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                              text)  # Локально
                    schedule.every().thursday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 5:
                    # schedule.every().friday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().friday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 6:
                    # schedule.every().saturday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                              text)  # Локально
                    schedule.every().saturday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 7:
                    # schedule.every().sunday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().sunday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу

            elif week_shedule % 2 != 0 and pairness == 1:
                if day == 0:
                    # schedule.every().day.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                         text)  # Локально
                    schedule.every().day.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 1:
                    # schedule.every().monday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().monday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 2:
                    # schedule.every().tuesday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                             text)  # Локально
                    schedule.every().tuesday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 3:
                    # schedule.every().wednesday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                               text)  # Локально
                    schedule.every().wednesday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 4:
                    # schedule.every().thursday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                              text)  # Локально
                    schedule.every().thursday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 5:
                    # schedule.every().friday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().friday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 6:
                    # schedule.every().saturday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                              text)  # Локально
                    schedule.every().saturday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 7:
                    # schedule.every().sunday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().sunday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
            elif pairness == 0:
                if day == 0:
                    # schedule.every().day.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                         text)  # Локально
                    schedule.every().day.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 1:
                    # schedule.every().monday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().monday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 2:
                    # schedule.every().tuesday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                             text)  # Локально
                    schedule.every().tuesday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 3:
                    # schedule.every().wednesday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                               text)  # Локально
                    schedule.every().wednesday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 4:
                    # schedule.every().thursday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                              text)  # Локально
                    schedule.every().thursday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 5:
                    # schedule.every().friday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().friday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 6:
                    # schedule.every().saturday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                              text)  # Локально
                    schedule.every().saturday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу
                if day == 7:
                    # schedule.every().sunday.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin,
                    #                                                            text)  # Локально
                    schedule.every().sunday.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу

                # schedule.every().day.at(task_time.strftime("%H:%M")).do(send_message_to_group_and_pin, text)  # Локально
                # schedule.every().day.at(time_utc).do(send_message_to_group_and_pin, text)  # Для хостингу

            schedule.every().day.at(tz.get_utc_str_hh_mm_from_str(config.TIME_UNPIN_LAST_MESSAGE)).do(unpin_message)

        cursor.close()
        db.close()
        global stop_schedule_flag
        while not stop_schedule_flag:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        logging.error(f"Error in create_schedule_from_table: {e}")
        send_message_to_group(f"Помилка: {e}")


schedule_thread = threading.Thread(target=create_schedule_from_table)
schedule_thread.start()


def refresh_schedule():
    global schedule_thread
    global stop_schedule_flag

    try:
        for job in list(schedule.get_jobs()):
            schedule.cancel_job(job)

        stop_schedule_flag = True

        schedule_thread.join()

        stop_schedule_flag = False
        schedule_thread = threading.Thread(target=create_schedule_from_table)
        schedule_thread.start()

    except Exception as e:
        logging.error(f"Error in refresh_schedule : {e}")
        send_message_to_group(f"Трабли якісь: {e}")


schedule.every().day.at(tz.get_utc_str_hh_mm_from_str(config.TIME_HB_TASKS_CHECK)).do(refresh_schedule)


@bot.message_handler(content_types=['text', 'photo', 'video', 'document',
                                    'audio', 'voice', 'sticker', 'video_note', 'animation'])
def reaction_message(message):
    try:
        if message.chat.id == GROUP_ID:
            global message_count
            message_count += 1

            if config.REACTION_FREQUENCY > 0:
                reactions = database.get_emojies()
                if message_count % config.REACTION_FREQUENCY == 0:
                    reaction = random.choice(reactions)
                    reaction = database.emoji_decode(reaction)
                    bot.reply_to(message, reaction)

            if config.STICKER_FREQUENCY > 0:
                if message_count % config.STICKER_FREQUENCY == 0:
                    sticker_pack_ids = database.get_sticker_packs()
                    random_pack_id = random.choice(sticker_pack_ids)
                    sticker_pack = bot.get_sticker_set(random_pack_id)
                    stickers = sticker_pack.stickers
                    random_sticker = random.choice(stickers)
                    bot.send_sticker(message.chat.id, random_sticker.file_id, reply_to_message_id=message.message_id)

    except Exception as e:
        logging.error(f"Error in reaction_message : {e}")
        bot.reply_to(message, f"Трабли якісь: {e}")


def start_polling():
    try:
        updates = bot.get_updates()
        last_update_id = updates[-1].update_id if updates else None
        bot.get_updates(offset=last_update_id)
        bot.polling(none_stop=True)
        time.sleep(60)
    except Exception as e:
        logging.error(f"Error in start_polling : {e}")


polling_thread = threading.Thread(target=start_polling)
polling_thread.start()


def stop_bot():
    chat_id = GROUP_ID
    bot.send_message(chat_id, 'Я знову в ауті, смикайте сісадміна((')


signal.signal(signal.SIGINT, lambda signum, frame: stop_bot())
while True:
    schedule.run_pending()
    time.sleep(60)
