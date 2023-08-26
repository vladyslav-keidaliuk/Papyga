import datetime
import telebot
import database
import config
from mysql.connector import Error
from dateutil import parser
import logging

bot = telebot.TeleBot(config.TOKEN)
date_format = "%d.%m.%Y"


def check_valid_date(date_string, format_string):
    try:
        parsed_date = parser.parse(date_string, dayfirst=True)
        formatted_date = parsed_date.strftime(format_string)
        return formatted_date == date_string
    except ValueError as e:
        logging.error(f"Error in birthdays.py - check_valid_date: {e}")
        return False


def check_birthday():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        query = "SELECT date_birthday, full_name FROM birthdays"
        cursor.execute(query)
        rows = cursor.fetchall()

        today = datetime.datetime.today().date()

        birthday_info = {}

        for row in rows:
            date_str = row[0]
            full_name = row[1]

            if date_str in birthday_info:
                birthday_info[date_str].append(full_name)
            else:
                birthday_info[date_str] = [full_name]

        greetings = []

        for date_str, names in birthday_info.items():
            day, month, year = date_str.split(".")
            if int(month) == today.month and int(day) == today.day:
                birth_date = datetime.date(int(year), int(month), int(day))
                ages = []
                for name in names:
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    ages.append(str(age))
                if len(names) == 1:
                    text = f"Cьогодні день народження у {names[0]}!!! Вітаємо 🥂🥳, сьогодні тобі {ages[0]} років"
                else:
                    text = f"Cьогодні день народження у {', '.join(names)}!!! Вітаємо 🥂🥳, сьогодні вам {', '.join(ages)} років"
                greetings.append(text)

        cursor.close()
        db.close()

        return "\n".join(greetings)

    except Error as e:
        logging.error(f"Error in check_birthday db: {e}")
    except Exception as e:
        logging.error(f"Error in check_birthday: {e}")


def add_birthday(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        data = message.text.split('\n')
        date = data[1]
        full_name = '\n'.join(data[2:])

        if check_valid_date(date, date_format) and len(full_name) > 0:
            try:
                res = database.db_connect()
                cursor = res[1]
                db = res[0]

                sql = "INSERT INTO birthdays (date_birthday, full_name) VALUES (%s, %s)"
                data = (date, full_name)

                cursor.execute(sql, data)

                db.commit()
                cursor.close()
                db.close()
                bot.reply_to(message, f"Дані про День Народження додано.")

            except Error as e:
                bot.reply_to(message, f"Трабли з записом у БД {e}")
        else:
            bot.reply_to(message, "Виникла помилка!\n\n"
                                  "Можливі помилки:\n"
                                  "1) Введена дата не існує або не відповідає формату.\n"
                                  "Формат : дд.мм.рррр\n"
                                  "2) Не введено ПІБ людини в якої День Народження.")
    except Error as e:
        logging.error(f"Error in add_birthday db :{e}")
        bot.reply_to(message, f"Ти щось не так записав.Спробуй ще раз. Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in add_birthday :{e}")
        bot.reply_to(message, f"Ти щось не так записав.Спробуй ще раз. Помилка: {e}")


def delete_birthday(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_info = bot.get_chat_member(chat_id, user_id)

        if user_info.status == 'administrator' or user_info.status == 'creator':

            data = message.text.split('\n')
            id_row = data[1]

            try:
                res = database.db_connect()
                cursor = res[1]
                db = res[0]

                delete_query = "DELETE FROM birthdays WHERE id = %s"
                cursor.execute(delete_query, (id_row,))
                db.commit()

                drop_column_query = "ALTER TABLE birthdays DROP COLUMN id"
                cursor.execute(drop_column_query)
                db.commit()

                add_column_query = "ALTER TABLE birthdays ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
                cursor.execute(add_column_query)
                db.commit()

                cursor.close()
                db.close()
                bot.reply_to(message, f"Дані про День Народження успішно видалено")

            except Error as e:
                logging.error(f"Error in delete_birthday db : {e}")
                bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
        else:
            bot.reply_to(message, "В тебе нема прав на цю дію !")
    except Exception as e:
        logging.error(f"Error in delete_birthday : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")


def get_season(month):
    if 3 <= month <= 5:
        return "Весна"
    elif 6 <= month <= 8:
        return "Літо"
    elif 9 <= month <= 11:
        return "Осінь"
    else:
        return "Зима"


def get_all_birthdays(message):
    res = database.db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = "SELECT * FROM birthdays ORDER BY DATE_FORMAT(str_to_date(date_birthday, '%d.%m.%Y'), '%m-%d')"
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            max_message_length = 3800
            birthdays_info = {
                "Зима": [],
                "Весна": [],
                "Літо": [],
                "Осінь": []
            }
            counter = {}
            order_numbers = {}

            for season in birthdays_info.keys():
                counter[season] = 1

            for row in rows:
                id = row[0]
                date_birthday = row[1]
                full_name = row[2]
                month = int(date_birthday.split(".")[1])

                season = get_season(month)
                order_numbers[id] = counter[season]
                birthday_entry = f"<{counter[season]}>[{id}] : {full_name}  [{date_birthday}]"
                birthdays_info[season].append(birthday_entry)
                counter[season] += 1

            combined_message = ""
            current_length = 0

            for season, info in birthdays_info.items():
                if info:
                    season_message = f"\n{season}:\n"
                    sorted_info = sorted(info, key=lambda x: order_numbers[
                        int(x.split('[')[1].split(']')[0])])

                    for entry in sorted_info:
                        entry_str = entry + "\n"
                        entry_length = len(entry_str)

                        if current_length + entry_length + len(season_message) <= max_message_length:
                            season_message += entry_str
                            current_length += entry_length
                        else:
                            combined_message += season_message
                            season_message = f"\n{season}:\n{entry_str}"
                            current_length = len(season_message)

                    combined_message += season_message

            if combined_message:
                messages = []
                for i in range(0, len(combined_message), max_message_length):
                    messages.append(combined_message[i:i + max_message_length])
                for msg in messages:
                    bot.reply_to(message, msg)
            else:
                bot.reply_to(message, "Жодного дня народження нема в БД.")

        else:
            bot.reply_to(message, "Жодного дня народження нема в БД.")

    except Error as e:
        logging.error(f"Error in get_all_birthdays db : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    except Exception as e:
        logging.error(f"Error in get_all_birthdays : {e}")
        bot.reply_to(message, f"Щось не так. Спробуй знов. Помилка: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def send_message_to_group(message):
    bot.send_message(config.GROUP_ID, message, parse_mode="HTML", disable_web_page_preview=True)
