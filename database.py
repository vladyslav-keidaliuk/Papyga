import datetime
import logging
import random
from datetime import timedelta

import emoji
import requests
import telebot
from mysql.connector import Error
from telebot import types
import time
import config
import plots
import spotify
from config import db_connection
from phrases import get_link_with_text, get_text_with_link_replied_user, get_text_with_link

bot = telebot.TeleBot(config.TOKEN)


def db_connect():
    try:
        mydb = db_connection()
        mycursor = mydb.cursor(buffered=True)
        return [mydb, mycursor]
    except Error as e:
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(З'єднання з БД)\n"
                              f"Помилка: {e}")


def set_pinned_message_in_db(chat_id, message_id):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = "INSERT INTO pinned_messages (id, message_id) VALUES (%s, %s)"
        values = (chat_id, message_id)
        cursor.execute(query, values)
        db.commit()

        cursor.close()
        db.close()
    except Error as e:
        logging.error(f"Error in set_pinned_message_in_db db:{e}")
        send_message_to_group(f"Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in set_pinned_message_in_db :{e}")
        send_message_to_group(f"Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def unpin_and_delete_pinned_message():
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = "SELECT id, message_id FROM pinned_messages"
        cursor.execute(query)
        data = cursor.fetchall()

        for row in data:
            id, message_id = row
            bot.unpin_chat_message(id, message_id)
            delete_query = "DELETE FROM pinned_messages WHERE id = %s"
            cursor.execute(delete_query, (id,))
            db.commit()

        cursor.close()
        db.close()
    except Error as e:
        logging.error(f"Error in unpin_and_delete_pinned_message db:{e}")
        send_message_to_group(f"Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in  unpin_and_delete_pinned_message :{e}")
        send_message_to_group(f"Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def change_bayraktar_by_reel(new_size, user_id):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = "UPDATE Users SET size = %s WHERE user_id = %s"
        values = (str(new_size), user_id)

        cursor.execute(query, values)
        db.commit()

        cursor.close()
        db.close()
    except Error as e:
        logging.error(f"Error in change_bayraktar_by_reel db:{e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Не зміг відкусити)\n"
                              f"Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in  change_bayraktar_by_reel :{e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Не зміг відкусити)\n"
                              f"Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def new_try_mountain(user_id, passmountain):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        new_passmountain = random.randint(0, config.LIMIT_IN_DE_MOUNTAIN)
        status = random.randint(0, 100)

        if status == 66 or status == 69 or status == 96 or status == 99:
            new_passmountain = passmountain * -1
        elif 30 >= status >= 0:
            new_passmountain = passmountain + new_passmountain
        elif 31 <= status <= 40:
            new_passmountain = passmountain
        elif 41 <= status <= 99:
            new_passmountain = passmountain - new_passmountain
        elif status == 100:
            new_passmountain = 0

        query = "UPDATE Users SET passmountain = %s WHERE user_id = %s"
        values = (str(new_passmountain), user_id)

        cursor.execute(query, values)
        db.commit()

        cursor.close()
        db.close()
    except Error as e:
        logging.error(f"Error in  new_try_mountain db :{e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Нова спроба у скелелазах)"
                              f"Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in  new_try_mountain :{e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Нова спроба у скелелазах)\n"
                              f"Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def new_try_bayraktar(user_id, size):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        new_size = random.randint(0, config.LIMIT_IN_DE_BAYRAKTAR)
        status = random.randint(0, 100)

        if 60 >= status >= 0:
            new_size = size + new_size
        if 61 <= status <= 65:
            new_size = size
        if 66 <= status <= 99:
            if size < new_size:
                new_size = 0
            if size >= new_size:
                new_size = size - new_size
        if status == 100:
            new_size = size * 2

        query = "UPDATE Users SET size = %s WHERE user_id = %s"
        values = (str(new_size), user_id)

        cursor.execute(query, values)
        db.commit()

        cursor.close()
        db.close()
    except Error as e:
        logging.error(f"Error in new_try_bayraktar db: {e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Нова спроба у байрактарах)\n"
                              f"Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in new_try_bayraktar : {e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Нова спроба у байрактарах)\n"
                              f"Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def new_try_qt(message, user_id):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        new_quote = get_quote()
        text, emoji_code = get_random_totem()

        query = "UPDATE Users SET totem = %s WHERE user_id = %s"
        values = (text + ' ' + emoji_code, user_id)

        cursor.execute(query, values)
        db.commit()

        if cursor.rowcount > 0:

            link, title, artist, playlist = spotify.get_random_track()

            text = f"{get_nickname(message)}, " \
                   f"твоя тотемна тварина на наступні {config.TIMER_DURATION_HOURS} годин :" \
                   f" {text + ' ' + emoji_decode(emoji_code)}\n" \
                   f"\n" \
                   f"Твоя цитата дня : {new_quote}\n" \
                   f"\n" \
                   f"\U0001F99CОсь твій трек дня\U0001F99C:\n" \
                   f"Назва треку: {title}\n" \
                   f"Виконавець: {artist}"

            text_on_button = ""
            if 'spotify' in link:
                text_on_button = "Відкрити у Spotify"
            elif 'youtube' in link:
                text_on_button = "Відкрити у YouTube Music"

            keyboard = types.InlineKeyboardMarkup()

            button = types.InlineKeyboardButton(text=text_on_button, url=f"{link}")
            keyboard.add(button)

            bot.send_message(message.chat.id,
                             text,
                             reply_to_message_id=message.message_id,
                             parse_mode="HTML",
                             reply_markup=keyboard,
                             disable_web_page_preview=True)
        else:
            send_message_to_group("Не відбулось змін для БД.")
        cursor.close()
        db.close()
    except Error as e:
        logging.error(f"Error in new_try_qt db: {e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Нова спроба у цитаті та тотемі)\n"
                              f"Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in new_try_qt : {e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Нова спроба у цитаті та тотемі)\n"
                              f"Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def repeat_timer(user_id, what_timer):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        now = datetime.datetime.now()
        date_time_stop_str = str(now + timedelta(hours=config.TIMER_DURATION_HOURS))

        if what_timer == 0:
            query = "UPDATE Users SET stop_timer_qt = %s WHERE user_id = %s"
            values = (date_time_stop_str, user_id)
            cursor.execute(query, values)
            db.commit()

        elif what_timer == 1:
            query = "UPDATE Users SET stop_timer = %s WHERE user_id = %s"
            values = (date_time_stop_str, user_id)
            cursor.execute(query, values)
            db.commit()

        elif what_timer == 2:
            query = "UPDATE Users SET stop_timer_mountain = %s WHERE user_id = %s"
            values = (date_time_stop_str, user_id)
            cursor.execute(query, values)
            db.commit()

        cursor.close()
        db.close()
    except Error as e:
        logging.error(f"Error in repeat_timer db : {e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Оновлення таймеру)\n"
                              f"Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in repeat_timer : {e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"(Оновлення таймеру)\n"
                              f"Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_text_with_link_for_top5(user_id):
    try:
        chat_member = bot.get_chat_member(chat_id=config.GROUP_ID, user_id=user_id)
        username = chat_member.user.username
        first_name = chat_member.user.first_name
        last_name = chat_member.user.last_name

        if first_name is None and last_name is not None:
            text = f"<a href='http://t.me/{username}'>" \
                   f"{last_name}</a>"
            return text
        if first_name is not None and last_name is None:
            text = f"<a href='http://t.me/{username}'>" \
                   f"{first_name}</a>"
            return text
        if first_name is None and last_name is None:
            text = f"<a href='http://t.me/{username}'>" \
                   f"{username}</a>"
            return text
        else:
            text = f"<a href='http://t.me/{username}'>" \
                   f"{first_name + ' ' + last_name}</a>"
            return text
    except Error as e:
        logging.error(f"Error in get_text_with_link_for_top5 db : {e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"Помилка : {e}")
    except Exception as e:
        logging.error(f"Error in get_text_with_link_for_top5 : {e}")
        send_message_to_group(f"Упс, щось пішло не так...\n"
                              f"Помилка : {e}")


def set_nick(message):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        user_id = message.from_user.id

        your_nick = message.text[5:]
        text = f"*Твій нік змінено на:* {your_nick}"

        try:
            query = "UPDATE Users SET nickname = %s WHERE user_id = %s"
            values = (your_nick, user_id)
            cursor.execute(query, values)

            db.commit()
            cursor.close()
            db.close()
        except Error as e:
            logging.error(f"Error in set_nick db : {e}")
        except Exception as e:
            logging.error(f"Error in set_nick : {e}")
        bot.reply_to(message, text, parse_mode="Markdown")

    except Error as e:
        logging.error(f"Error in set_nick db : {e}")
        send_message_to_group(f"Помилка : {e}")
    except Exception as e:
        logging.error(f"Error in set_nick : {e}")
        send_message_to_group(f"Помилка : {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def send_random_number(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        text = message.text[14:]
        if ',' in text.replace(" ", ""):
            number_range = text.split(",")

            start = int(number_range[0])
            end = int(number_range[1])
            roll_text = number_range[2] if len(number_range) >= 3 else " "

            random_number = random.randint(start, end)
            response = f"Ролл на: {roll_text} \nТобі випало: {random_number}"
            bot.reply_to(message, response)

        elif text.replace(" ", "") in ["цитата", "Цитата", "Quote", "quote"]:
            quote = get_quote()
            response = f"Я дивлюсь ти хочеш нову цитату))\n" \
                       f"Не можу тобі у цьому відмовити, тож тримай:\n" \
                       f"{quote}"
            bot.reply_to(message, response)

        elif text.replace(" ", "").lower() in ["втрати", "рф"]:

            try:
                session = requests.Session()
                resp = session.get('https://russianwarship.rip/api/v2/statistics/latest')
                data = resp.json()

                text = f'''<b>🪖 Загальні бойові втрати російського окупанта.\n</b>'''
                text += f'''<b>📋 <a href = "{data["data"]["resource"]}">Станом на {data["data"]["date"]}</a></b>\n'''
                text += f'''<b>🗓 День війни: {data["data"]["day"]}-й </b>\n\n'''
                text += f'''<b>- Особовий склад: {data["data"]["stats"]["personnel_units"]} {f"(+{data['data']['increase']['personnel_units']})" if data['data']['increase']['personnel_units'] > 0 else ''}</b>\n'''
                text += f'''<b>- Танки: {data["data"]["stats"]["tanks"]} {f"(+{data['data']['increase']['tanks']})" if data['data']['increase']['tanks'] > 0 else ''}</b>\n'''
                text += f'''<b>- ББМ: {data['data']['stats']['armoured_fighting_vehicles']} {f"(+{data['data']['increase']['armoured_fighting_vehicles']})" if data['data']['increase']['armoured_fighting_vehicles'] > 0 else ''}\n</b>'''
                text += f'''<b>- Арт. системи: {data['data']['stats']['artillery_systems']} {f"(+{data['data']['increase']['artillery_systems']})" if data['data']['increase']['artillery_systems'] > 0 else ''}\n</b>'''
                text += f'''<b>- РСЗВ: {data['data']['stats']['mlrs']} {f"(+{data['data']['increase']['mlrs']})" if data['data']['increase']['mlrs'] > 0 else ''}\n</b>'''
                text += f'''<b>- Засоби ППО: {data['data']['stats']['aa_warfare_systems']} {f"(+{data['data']['increase']['aa_warfare_systems']})" if data['data']['increase']['aa_warfare_systems'] > 0 else ''}\n</b>'''
                text += f'''<b>- Літаки: {data['data']['stats']['planes']} {f"(+{data['data']['increase']['planes']})" if data['data']['increase']['planes'] > 0 else ''}\n</b>'''
                text += f'''<b>- Гелікоптери: {data['data']['stats']['helicopters']} {f"(+{data['data']['increase']['helicopters']})" if data['data']['increase']['helicopters'] > 0 else ''}\n</b>'''
                text += f'''<b>- Автотехніка/автоцистерни: {data['data']['stats']['vehicles_fuel_tanks']} {f"(+{data['data']['increase']['vehicles_fuel_tanks']})" if data['data']['increase']['vehicles_fuel_tanks'] > 0 else ''}\n</b>'''
                text += f'''<b>- Кораблі/катери: {data['data']['stats']['warships_cutters']} {f"(+{data['data']['increase']['warships_cutters']})" if data['data']['increase']['warships_cutters'] > 0 else ''}\n</b>'''
                text += f'''<b>- БПЛА: {data['data']['stats']['uav_systems']} {f"(+{data['data']['increase']['uav_systems']})" if data['data']['increase']['uav_systems'] > 0 else ''}\n</b>'''
                text += f'''<b>- Спец. техніка: {data['data']['stats']['special_military_equip']} {f"(+{data['data']['increase']['special_military_equip']})" if data['data']['increase']['special_military_equip'] > 0 else ''}\n</b>'''
                text += f'''<b>- Установки ОТРК/ТРК: {data['data']['stats']['atgm_srbm_systems']} {f"(+{data['data']['increase']['atgm_srbm_systems']})" if data['data']['increase']['atgm_srbm_systems'] > 0 else ''}\n</b>'''
                text += f'''<b>- Крилаті ракети: {data['data']['stats']['cruise_missiles']} {f"(+{data['data']['increase']['cruise_missiles']})" if data['data']['increase']['cruise_missiles'] > 0 else ''}\n\n</b>'''
                text += f'''<b>🇺🇦 Слава Україні! Героям Слава!</b>'''
                bot.reply_to(message, text, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logging.error(f"Error with API russianwarship.rip : {e}")
                bot.send_message(message, '⚠<b>Помилка при отриманні даних.</b>', parse_mode='HTML',
                                 disable_web_page_preview=True)
    except Exception as e:
        send_message_to_group(f"Ти щось не так записав.Спробуй ще раз.\n"
                              f"Формат:\n"
                              f"1) Для роллу: start , stop , text(за бажання\n"
                              f"2) Для цитати просто пиши 'цитата' чи 'Цитата' чи 'Quote'\n"
                              f"3) Для того, щоб дізнатись скільки втрат у рф, пиши 'втрати','рф'\n"
                              f"Детальна помилка: {e}")


def update_reputation(user_id, new_reputation):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        update_query = "UPDATE Users SET reputation = %s WHERE user_id = %s"
        update_values = (new_reputation, user_id)

        cursor.execute(update_query, update_values)
        db.commit()

        cursor.close()
        db.close()
    except Error as e:
        logging.error(f"Error in update_reputation db : {e}")
    except Exception as e:
        logging.error(f"Error in update_reputation : {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_reputation(user_id):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        select_query = "SELECT reputation FROM Users WHERE user_id = %s"
        select_values = (user_id,)

        cursor.execute(select_query, select_values)
        reputation = cursor.fetchone()[0]

        cursor.close()
        db.close()

        if reputation is None:
            reputation = 0
        return reputation
    except Error as e:
        logging.error(f"Error in get_reputation db : {e}")
    except Exception as e:
        logging.error(f"Error in get_reputation : {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_nickname(message):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = "SELECT nickname FROM Users WHERE user_id = %s"
        cursor.execute(query, (message.from_user.id,))
        row1 = cursor.fetchone()

        if row1[0] is not None:
            nick = get_link_with_text(message, row1[0])
        else:
            nick = get_text_with_link(message)
        db.commit()
        cursor.close()
        db.close()
        return nick
    except Error as e:
        logging.error(f"Error in get_nicknamen db : {e}")
    except Exception as e:
        logging.error(f"Error in get_nickname : {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def interaction_handler(action_text, reaction_text, message):
    bot.send_chat_action(message.chat.id, 'typing')
    res = db_connect()
    cursor = res[1]
    db = res[0]

    try:
        if message.reply_to_message:

            if action_text == config.ADD_STICKER_PACK:
                add_sticker_pack(message)
            elif action_text == config.DELETE_STICKER_PACK:
                delete_sticker_pack(message)
            elif action_text == config.ADD_EMOJI:
                add_emoji(message)
            elif action_text == config.DELETE_EMOJI:
                delete_emoji(message)
            elif action_text == config.MUTE_USER:
                if config.AGGRESSIVE_MODE_ENABLE:
                    mute_user(message)
                else:
                    send_message_to_group("Агресивний мод вимкнений, "
                                          "Ви не можете заборонити користувачеві писати.")
            elif action_text == config.UNMUTE_USER:
                if config.AGGRESSIVE_MODE_ENABLE:
                    unmute_user(message)
                else:
                    send_message_to_group("Агресивний мод вимкнено."
                                          "Ви не можете дозволити користувачеві писати.")
            else:
                query = "SELECT nickname FROM Users WHERE user_id = %s"
                cursor.execute(query, (message.from_user.id,))
                row1 = cursor.fetchone()

                if row1[0] is not None:
                    text1 = get_link_with_text(message, row1[0])
                else:
                    text1 = get_text_with_link(message)

                query = "SELECT nickname FROM Users WHERE user_id = %s"
                cursor.execute(query, (message.reply_to_message.from_user.id,))
                row2 = cursor.fetchone()

                if row2 is not None and row2[0] is not None:
                    text2 = get_link_with_text(message.reply_to_message, row2[0])
                else:
                    text2 = get_text_with_link_replied_user(message)
                db.commit()
                cursor.close()
                db.close()

                additional_text = message.text.strip()
                respect = 0
                if additional_text.startswith("+"):
                    count = additional_text.count("+")
                    if message.from_user.id == message.reply_to_message.from_user.id:
                        response = f"Ах ти пустун, хотів зчитерити і поставити +{count} САМОМУ СОБІ.\n" \
                                   f"Тут таке не прокатить. Ти не маєш права висловлювати повагу самому собі."
                        bot.send_message(message.chat.id,
                                         response,
                                         reply_to_message_id=message.reply_to_message.message_id,
                                         parse_mode="HTML",
                                         disable_web_page_preview=True)
                    else:
                        if count > 5:
                            respect += 5

                            update_reputation(message.reply_to_message.from_user.id,
                                              get_reputation(message.reply_to_message.from_user.id) + respect)
                            response = f"{text1}, ах ти пустун, хотів зчитерити і поставити {text2} +{count}. Таке тут не прокатить 🙂. Вказано повагу +{respect}, поточне значення поваги: {get_reputation(message.reply_to_message.from_user.id)}"
                            bot.send_message(message.chat.id,
                                             response,
                                             reply_to_message_id=message.reply_to_message.message_id,
                                             parse_mode="HTML",
                                             disable_web_page_preview=True)
                        else:
                            respect += count
                            update_reputation(message.reply_to_message.from_user.id,
                                              get_reputation(message.reply_to_message.from_user.id) + respect)
                            response = f"{text1} виказав повагу +{count} {text2}, поточне значення поваги: {get_reputation(message.reply_to_message.from_user.id)}"
                            bot.send_message(message.chat.id,
                                             response,
                                             reply_to_message_id=message.reply_to_message.message_id,
                                             parse_mode="HTML",
                                             disable_web_page_preview=True)

                elif additional_text.startswith("-"):
                    count = additional_text.count("-")
                    if count > 5:
                        respect += 5
                        update_reputation(message.reply_to_message.from_user.id,
                                          get_reputation(message.reply_to_message.from_user.id) - respect)
                        response = f"{text1}, ах ти пустун, хотів зчитерити і забрати -{count} в {text2}. Таке тут не прокатить 🙂. Забрано поваги -{respect}, поточне значення поваги: {get_reputation(message.reply_to_message.from_user.id)}"
                        bot.send_message(message.chat.id,
                                         response,
                                         reply_to_message_id=message.reply_to_message.message_id,
                                         parse_mode="HTML",
                                         disable_web_page_preview=True)
                    else:
                        respect += count
                        update_reputation(message.reply_to_message.from_user.id,
                                          get_reputation(message.reply_to_message.from_user.id) - respect)
                        response = f"{text1} забрав в {text2} -{count} поваги, поточне значення поваги: {get_reputation(message.reply_to_message.from_user.id)}"
                        bot.send_message(message.chat.id,
                                         response,
                                         reply_to_message_id=message.reply_to_message.message_id,
                                         parse_mode="HTML",
                                         disable_web_page_preview=True)

                else:
                    additional_text = message.text[len(action_text):].strip()
                    if len(additional_text) == 0:
                        response = f"{text1} {reaction_text} {text2} !!!!"
                    else:
                        response = f"{text1} {reaction_text} {text2}\nС репликой\U0001F4AC': {additional_text}!'"
                    bot.send_message(message.chat.id,
                                     response,
                                     reply_to_message_id=message.reply_to_message.message_id,
                                     parse_mode="HTML",
                                     disable_web_page_preview=True)

                    return interaction_handler
    except Error as e:
        logging.error(f"Error in interaction_handler db: {e}")
        bot.reply_to(message, f"Трабли якісь з БД : {e}")
    except Exception as e:
        logging.error(f"Error in interaction_handler : {e}")
        bot.reply_to(message, f"Трабли якісь : {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def top(message):
    bot.send_chat_action(message.chat.id, 'typing')
    res = db_connect()
    cursor = res[1]
    db = res[0]
    if message.chat.id == config.GROUP_ID:
        try:

            cursor.execute("SELECT user_id, size FROM Users ORDER BY size DESC LIMIT 5")
            db.commit()
            top_users = cursor.fetchall()

            top_users_str = "TОП 5 БАЙРАКТАРІВ ЧАТУ:\n\n"
            for i, user in enumerate(top_users):
                top_users_str += f"{i + 1}. {get_text_with_link_for_top5(user[0])} -> {user[1]} см\n"

            if config.PLOTS_ENABLE is True:
                bot.send_photo(config.GROUP_ID, photo=plots.get_plot_top_bayraktar(), caption="БАЙРАКТАРИ")
            send_message_to_group(top_users_str)

            cursor.close()
            db.close()
        except Error as e:
            logging.error(f"Error in top db : {e}")
            send_message_to_group(f"Упс, щось пішло не так... \n"
                                  f"Помилка :{e} ")
        except Exception as e:
            logging.error(f"Error in top : {e}")
            send_message_to_group(f"Упс, щось пішло не так... \n"
                                  f"Помилка :{e} ")
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    else:
        bot.send_message(message.chat.id, "Ця команда працює лише у груповому чаті.")


def top_mountain(message):
    user_id = message.from_user.id
    bot.send_chat_action(message.chat.id, 'typing')
    res = db_connect()
    mycursor = res[1]
    mydb = res[0]
    if message.chat.id == config.GROUP_ID:
        try:

            mycursor.execute(
                "SELECT user_id, passmountain FROM Users WHERE passmountain >= 0 ORDER BY passmountain DESC LIMIT 5")
            mydb.commit()
            top_users = mycursor.fetchall()

            top_users_str = "TОП 5 \U000026F0СКЕЛЕЛАЗІВ ЧАТУ:\n\n"
            for i, user in enumerate(top_users):
                top_users_str += f"{i + 1}. {get_text_with_link_for_top5(user[0])} >> {user[1]} м ^\n"

            mycursor.execute(
                "SELECT user_id, passmountain FROM Users WHERE passmountain < 0 ORDER BY passmountain LIMIT 5")
            mydb.commit()
            top_negative_users = mycursor.fetchall()

            tmp_arr_str = []
            top_users_str += "\n\nТОП 5 \U000026CFШАХТАРІВ ЧАТУ :\n\n"
            for i, user in enumerate(top_negative_users):
                tmp_arr_str.append(f"{i + 1}. {get_text_with_link_for_top5(user[0])} >> {user[1]} м ^(-1)\n")
            for i in reversed(tmp_arr_str):
                top_users_str += i
            if config.PLOTS_ENABLE is True:
                bot.send_photo(config.GROUP_ID, photo=plots.get_plot_top_mountain(user_id), caption="Шахта || Гора")
            send_message_to_group(top_users_str)

            mycursor.close()
            mydb.close()
        except Error as e:
            logging.error(f"Error in top_mountain db : {e}")
            send_message_to_group(f"Упс, щось пішло не так...\n"
                                  f"Помилка : {e}")
        except Exception as e:
            logging.error(f"Error in top_mountain : {e}")
            send_message_to_group(f"Упс, щось пішло не так...\n"
                                  f"Помилка : {e}")
        finally:
            if mycursor:
                mycursor.close()
            if mydb:
                mydb.close()
    else:
        bot.send_message(message.chat.id, "Ця команда працює лише у груповому чаті.")


def send_message_to_group(message):
    try:
        bot.send_message(config.GROUP_ID, message, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"Error in database.send_message_to_group : {e}")


def get_username(user_id):
    try:
        user = bot.get_chat(user_id)
        if user.username:
            return user.username
        else:
            return f"User with id:{user_id}"
    except Exception as e:
        logging.error(f"Error in get_username {user_id} : {e}")
        return "Помилка в отриманні username"


def add_sticker_pack(message):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        sticker_pack_name = message.reply_to_message.sticker.set_name

        sql_check = "SELECT * FROM sticker_packs WHERE sticker_pack_name = %s"
        cursor.execute(sql_check, (sticker_pack_name,))
        existing_sticker_pack = cursor.fetchone()

        if existing_sticker_pack:
            bot.reply_to(message, f"Цей стікерпак вже є в БД.")
        else:
            sql_insert = "INSERT INTO sticker_packs(sticker_pack_name) VALUES (%s)"
            cursor.execute(sql_insert, (sticker_pack_name,))
            db.commit()
            cursor.close()
            db.close()
            bot.reply_to(message, f"Стікерпак додано в БД.")

    except Error as e:
        logging.error(f"Error in add_sticker_pack db: {e}")
        bot.reply_to(message, f"Трабли якісь з БД : {e}")
    except Exception as e:
        logging.error(f"Error in add_sticker_pack : {e}")
        bot.reply_to(message, f"Трабли якісь : {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_sticker_packs():
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        sql = "SELECT sticker_pack_name FROM sticker_packs"
        cursor.execute(sql)

        sticker_pack_ids = [row[0] for row in cursor.fetchall()]

        cursor.close()
        db.close()

        return sticker_pack_ids

    except Error as e:
        logging.error(f"Error in get_sticker_packs db: {e}")
        return []

    except Exception as e:
        logging.error(f"Error in get_sticker_packs: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def delete_sticker_pack(message):
    res = db_connect()
    cursor = res[1]
    db = res[0]

    try:

        sticker_pack_name = message.reply_to_message.sticker.set_name

        sql_check = "SELECT * FROM sticker_packs WHERE sticker_pack_name = %s"
        cursor.execute(sql_check, (sticker_pack_name,))
        existing_sticker_pack = cursor.fetchone()

        if not existing_sticker_pack:
            bot.reply_to(message, f"Такого стікерпаку нема в БД.")
        else:
            sql_delete = "DELETE FROM sticker_packs WHERE sticker_pack_name = %s"
            cursor.execute(sql_delete, (sticker_pack_name,))
            db.commit()

            drop_column_query = "ALTER TABLE sticker_packs DROP COLUMN id"
            cursor.execute(drop_column_query)
            db.commit()

            add_column_query = "ALTER TABLE sticker_packs ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
            cursor.execute(add_column_query)
            db.commit()

            cursor.close()
            db.close()

            bot.reply_to(message, f"Стікерпак успішно видалено з БД.")

    except Error as e:
        logging.error(f"Error in delete_sticker_pack db: {e}")
        return False

    except Exception as e:
        logging.error(f"Error in delete_sticker_pack: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_emoji_unicode(input_emoji):
    try:
        emoji_code = ord(input_emoji)
        emoji_unicode = f"\\U{emoji_code:08X}"
        return emoji_unicode

    except Exception as e:
        try:
            logging.error(f"Error in get_emoji_unicode: {e}")
            return input_emoji
        except Exception as e:
            logging.error(f"Error in get_emoji_unicode: {e}")
            return None


def add_emoji(message):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        emoji_text = message.reply_to_message.text
        emoji_count = emoji.emoji_count(emoji_text)
        if emoji_count > 1:
            bot.reply_to(message, f"Помилка, щось не так.")
        else:
            emoji_result = get_emoji_unicode(emoji_text)

            if emoji.emoji_count(emoji_text) > 0:
                sql_check = "SELECT * FROM emojies WHERE emoji_code = %s"
                cursor.execute(sql_check, (emoji_result,))
                existing_emoji = cursor.fetchone()

                if existing_emoji:
                    bot.reply_to(message, f"Цей емодзі вже є в БД.")
                else:
                    sql_insert = "INSERT INTO emojies(emoji_code) VALUES (%s)"
                    cursor.execute(sql_insert, (emoji_result,))
                    db.commit()
                    cursor.close()
                    db.close()
                    bot.reply_to(message, f"Емодзі додано в БД.")
            else:
                bot.reply_to(message, f"Помилка, це не емодзі.")
    except Error as e:
        logging.error(f"Error in add_emoji db: {e}")
        bot.reply_to(message, f"Трабли якісь з БД : {e}")
    except Exception as e:
        logging.error(f"Error in add_emoji : {e}")
        bot.reply_to(message, f"Трабли якісь : {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def delete_emoji(message):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        emoji_text = message.reply_to_message.text
        emoji_result = get_emoji_unicode(emoji_text)

        sql_check = "SELECT * FROM emojies WHERE emoji_code = %s"
        cursor.execute(sql_check, (emoji_result,))
        existing_emoji = cursor.fetchone()

        if not existing_emoji:
            bot.reply_to(message, f"Такого емодзі нема в БД.")
        else:
            sql_delete = "DELETE FROM emojies WHERE emoji_code = %s"
            cursor.execute(sql_delete, (emoji_result,))
            db.commit()

            drop_column_query = "ALTER TABLE emojies DROP COLUMN id"
            cursor.execute(drop_column_query)
            db.commit()

            add_column_query = "ALTER TABLE emojies ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
            cursor.execute(add_column_query)
            db.commit()

            cursor.close()
            db.close()

            bot.reply_to(message, f"Емодзі успішно видалено з БД.")

    except Error as e:
        logging.error(f"Error in delete_emoji db: {e}")
        return False

    except Exception as e:
        logging.error(f"Error in delete_emoji: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_emojies():
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        sql = "SELECT emoji_code FROM emojies"
        cursor.execute(sql)

        emoji_codes = [row[0] for row in cursor.fetchall()]

        cursor.close()
        db.close()

        return emoji_codes

    except Error as e:
        logging.error(f"Error in get_emojies db: {e}")
        return []

    except Exception as e:
        logging.error(f"Error in get_emojies : {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_all_emojies(message):
    chat_id = message.chat.id
    res = db_connect()
    cursor = res[1]
    db = res[0]

    try:

        query = "SELECT * FROM emojies"
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            max_message_length = 3800
            interval_info = []
            counter = 1

            for row in rows:
                emoji_id = row[0]
                emoji_code = row[1]

                interval_entry = f"Порядковий номер: [{emoji_id}]" \
                                 f"\nКод емодзі: {emoji_code}" \
                                 f"\nЕмодзі: {emoji_decode(emoji_code)}"
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
                bot.send_message(chat_id, "Нема жодного емодзі.")
        else:
            bot.send_message(chat_id, "Нема жодного емодзі.")
    except Error as e:
        logging.error(f"Error in get_all_emojies db: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in get_all_emojies: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        cursor.close()
        db.close()


def delete_emoji_by_index(message):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        data = message.text.split('\n')
        id_row = data[1]

        try:

            delete_query = "DELETE FROM emojies WHERE id = %s"
            cursor.execute(delete_query, (id_row,))
            db.commit()

            drop_column_query = "ALTER TABLE emojies DROP COLUMN id"
            cursor.execute(drop_column_query)
            db.commit()

            add_column_query = "ALTER TABLE emojies ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
            cursor.execute(add_column_query)
            db.commit()

            cursor.close()
            db.close()

            bot.reply_to(message, f"Емодзі успішно видалено.")

        except Error as e:
            logging.error(f"Error in delete_emoji db: {e}")
            bot.reply_to(message, f"Проблема якась : {e}")
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    except Exception as e:
        logging.error(f"Error in delete_emoji : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_count_rows_in_table(table):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = f"SELECT COUNT(*) FROM {table}"
        cursor.execute(query)

        result = cursor.fetchone()
        row_count = result[0]

        cursor.close()
        db.close()
        return row_count

    except Exception as e:
        logging.error(f"Error in get_count_rows_in_table [{table}] : {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_quote():
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        quote_id = random.randint(1, get_count_rows_in_table("quotes"))

        query = "SELECT * FROM quotes WHERE id = %s"
        cursor.execute(query, (quote_id,))

        result = cursor.fetchone()

        cursor.close()
        db.close()

        quote_id, quote = result
        quote = f'"{quote}"'

        return quote

    except Error as e:
        logging.error(f"Error in get_random_quote db : {e}")
    except Exception as e:
        logging.error(f"Error in get_random_quote : {e}")
        return f"Помилка: {e}"
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def add_totem(message):
    bot.send_chat_action(message.chat.id, 'typing')
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:
        user_id = message.from_user.id
        data = message.text.split('\n')
        totem = data[1]
        text = data[2]
        totem_count = emoji.emoji_count(totem)

        if totem_count > 1 or len(text) > 30:
            bot.reply_to(message, "Має бути лише одне емодзі і текст не більше 30 символів.")
        else:
            try:

                totem = get_emoji_unicode(totem)

                sql = "INSERT INTO totems (emoji_code, text) VALUES (%s, %s)"
                data = (totem, text)

                cursor.execute(sql, data)

                db.commit()
                cursor.close()
                db.close()

                bot.reply_to(message, f"Тотем успішно додано")

            except Error as e:
                logging.error(f"Error in add_totem db : {e}")
                bot.reply_to(message, f"Трабли з записом у БД {e}")
            finally:
                if cursor:
                    cursor.close()
                if db:
                    db.close()

    except Exception as e:
        logging.error(f"Error in add_totem: {e}")
        bot.reply_to(message, "Ти щось не так записав, або якась проблема виникла.Спробуй ще раз.")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def delete_totem(message):
    res = db_connect()
    cursor = res[1]
    db = res[0]
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        data = message.text.split('\n')
        id_row = data[1]

        try:

            delete_query = "DELETE FROM totems WHERE id = %s"
            cursor.execute(delete_query, (id_row,))
            db.commit()

            drop_column_query = "ALTER TABLE totems DROP COLUMN id"
            cursor.execute(drop_column_query)
            db.commit()

            add_column_query = "ALTER TABLE totems ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
            cursor.execute(add_column_query)
            db.commit()

            cursor.close()
            db.close()

            bot.reply_to(message, f"Тотем успішно видалено.")

        except Error as e:
            logging.error(f"Error in delete_totem db: {e}")
            bot.reply_to(message, f"Проблема якась : {e}")

    except Exception as e:
        logging.error(f"Error in delete_totem : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_all_totems(message):
    chat_id = message.chat.id
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = "SELECT * FROM totems"
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            max_message_length = 3800
            interval_info = []
            counter = 1

            for row in rows:
                totem_id = row[0]
                emoji_code = row[1]
                text = row[2]
                interval_entry = f"Порядковий номер: [{totem_id}]" \
                                 f"\nКод емодзі: {emoji_code}" \
                                 f"\nЕмодзі: {emoji_decode(emoji_code)}" \
                                 f"\nТекст: {text}"
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
                bot.send_message(chat_id, "Нема жодного тотему.")
        else:
            bot.send_message(chat_id, "Нема жодного тотему.")
    except Error as e:
        logging.error(f"Error in get_all_totemss db: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in get_all_totems: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_random_totem():
    res = db_connect()
    cursor = res[1]
    db = res[0]

    try:

        totem_id = random.randint(1, get_count_rows_in_table("totems"))

        query = "SELECT emoji_code, text FROM totems WHERE id = %s"
        cursor.execute(query, (totem_id,))

        result = cursor.fetchone()

        cursor.close()
        db.close()

        emoji_code, text = result

        return text, emoji_code

    except Error as e:
        logging.error(f"Error in get_totem db : {e}")
    except Exception as e:
        logging.error(f"Error in get_totem : {e}")
        return "Помилка!\n", f"Можливо у БД нема жодного тотему.\nДетальна інформація:{e}"
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def emoji_decode(emoji_code):
    try:
        emoji_res = emoji_code.encode('utf-8').decode('unicode-escape')
        if emoji.emoji_count(emoji_res) > 0:
            return emoji_res
        else:
            return emoji_code
    except Exception as e:
        logging.error(f"Error in emoji_decode: {e}")
        return None


def get_emoji_from_text_with_text(text):
    try:
        parts = text.split(' ')
        name = parts[0]
        emoji_code = parts[-1]
        return name + ' ' + emoji_decode(emoji_code)
    except Exception as e:
        logging.error(f"Error in database [get_emoji_from_text_with_text]: {e}")
        return None


def add_trigger(message):
    bot.send_chat_action(message.chat.id, 'typing')
    res = db_connect()
    cursor = res[1]
    db = res[0]

    try:
        data = message.text.split('\n')
        action_text = data[1].lower()
        reaction_text = data[2]

        if len(action_text) > 50 or len(reaction_text) > 200:
            bot.reply_to(message, "Довжина фрази-тригера має бути до 50 символів, відповіді до 200.")
        else:
            try:

                sql = "INSERT INTO triggers (action_text, reaction_text) VALUES (%s, %s)"
                data = (action_text, reaction_text)

                cursor.execute(sql, data)

                db.commit()
                cursor.close()
                db.close()

                bot.reply_to(message, f"Тригер успішно додано")

            except Error as e:
                logging.error(f"Error in add_trigger db : {e}")
                bot.reply_to(message, f"Трабли з записом у БД {e}")
            finally:
                if cursor:
                    cursor.close()
                if db:
                    db.close()

    except Exception as e:
        logging.error(f"Error in add_trigger: {e}")
        bot.reply_to(message, "Ти щось не так записав, або якась проблема виникла.Спробуй ще раз.")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_all_triggers(message):
    chat_id = message.chat.id
    res = db_connect()
    cursor = res[1]
    db = res[0]

    try:

        query = "SELECT * FROM triggers"
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            max_message_length = 3800
            interval_info = []
            counter = 1

            for row in rows:
                totem_id = row[0]
                action_text = row[1]
                reaction_text = row[2]
                interval_entry = f"Порядковий номер: [[{totem_id}]]" \
                                 f"\nФраза-тригер: `{action_text}`" \
                                 f"\nТекст відповіді: {reaction_text}"
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
                bot.send_message(chat_id, combined_message, parse_mode='Markdown')
            else:
                bot.send_message(chat_id, "Нема жодного тригеру.")
        else:
            bot.send_message(chat_id, "Нема жодного тригеру.")
    except Error as e:
        logging.error(f"Error in get_all_triggers db: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in get_all_triggers: {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_triggers_from_db():
    triggers = []
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = "SELECT action_text, reaction_text FROM triggers"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            action_text = row[0]
            reaction_text = row[1]
            triggers.append((action_text, reaction_text))

    except Error as e:
        logging.error(f"Error in get_triggers_from_db: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return triggers


def delete_trigger(message):
    bot.send_chat_action(message.chat.id, 'typing')
    res = db_connect()
    cursor = res[1]
    db = res[0]
    try:
        data = message.text.split('\n')
        id_row = data[1]

        try:

            if int(id_row) in range(1, 9):
                bot.reply_to(message, f"Системні тригери заборонено видаляти!")
            else:
                delete_query = "DELETE FROM triggers WHERE id = %s"
                cursor.execute(delete_query, (id_row,))
                db.commit()

                drop_column_query = "ALTER TABLE triggers DROP COLUMN id"
                cursor.execute(drop_column_query)
                db.commit()

                add_column_query = "ALTER TABLE triggers ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
                cursor.execute(add_column_query)
                db.commit()

                bot.reply_to(message, f"Тригер успішно видалено.")

        except Error as e:
            logging.error(f"Error in delete_trigger db: {e}")
            bot.reply_to(message, f"Проблема якась : {e}")

    except Exception as e:
        logging.error(f"Error in delete_trigger : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def mute_user(message):
    try:
        parts = message.text.split(config.MUTE_USER)
        user = message.reply_to_message.from_user
        if len(parts) == 2:
            duration_seconds = int(parts[1])
            if int(duration_seconds) < 60:
                send_message_to_group(f"Помилка. Значення має бути додатнім, та не менше 60.")
            else:
                if user.username:
                    target_id = user.username
                elif not user.username:
                    target_id = user.id

                bot.restrict_chat_member(chat_id=message.chat.id,
                                         user_id=user.id,
                                         can_send_messages=False,
                                         until_date=time.time() + duration_seconds)
                send_message_to_group(f"Користувач @{target_id} втратив право надсилати повідомлення"
                                      f" на {duration_seconds} секунд.")
    except Exception as e:
        send_message_to_group(f"Помилка: {e}")
        logging.error(f"Error in mute_user:{e}")


def unmute_user(message):
    try:
        user = message.reply_to_message.from_user
        if user.username:
            target_id = user.username
        else:
            target_id = user.id
        bot.restrict_chat_member(chat_id=message.chat.id, user_id=user.id, can_send_messages=True,
                                 can_send_media_messages=True, can_send_other_messages=True,
                                 can_add_web_page_previews=True)
        send_message_to_group(f"Користувачу @{target_id} дозволено розмовляти.")
    except Exception as e:
        send_message_to_group(f"Помилка: {e}")
        logging.error(f"Error in unmute_user:{e}")
