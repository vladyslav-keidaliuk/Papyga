import mysql.connector
import all_quotes
import database
import logging
import config


def create_tables():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        sql_queries = [

            """
            CREATE TABLE IF NOT EXISTS Users (
                user_id BIGINT PRIMARY KEY,
                size INT,
                stop_timer_qt DATETIME,
                stop_timer DATETIME,
                totem TINYTEXT,
                passmountain INT,
                stop_timer_mountain DATETIME,
                reputation INT,
                nickname TEXT
            );
            """,

            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY ,
                day INT,
                time TEXT,
                text TEXT,
                pairness INT
            );
            """,

            """
            ALTER TABLE tasks CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """,

            """
            CREATE TABLE IF NOT EXISTS music (
                id INT AUTO_INCREMENT PRIMARY KEY ,
                link TEXT,
                title TEXT,
                artist TEXT,
                playlist TEXT
            );
            """,

            """
            CREATE TABLE IF NOT EXISTS playlists(
                id INT AUTO_INCREMENT PRIMARY KEY ,
                playlist TEXT,
                datetime TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS birthdays(
              id INT AUTO_INCREMENT PRIMARY KEY,
              date_birthday TEXT,
              full_name TEXT
            );
            """,

            """
            ALTER TABLE birthdays CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """,

            """
            CREATE TABLE IF NOT EXISTS pinned_messages(
                id BIGINT ,
                message_id BIGINT
            );
            """,

            """
            ALTER TABLE pinned_messages CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """,

            """
            
            CREATE TABLE IF NOT EXISTS sticker_packs(
                id INT AUTO_INCREMENT PRIMARY KEY ,
                sticker_pack_name TINYTEXT
            );
            """,

            """
            CREATE TABLE IF NOT EXISTS emojies(
                id INT AUTO_INCREMENT PRIMARY KEY ,
                emoji_code TINYTEXT
            );
            """,

            """
            ALTER TABLE emojies CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """,

            """
            CREATE TABLE IF NOT EXISTS intervals(
                id INT AUTO_INCREMENT PRIMARY KEY ,
                start TINYTEXT,
                end TINYTEXT
            );
            """,

            """
            CREATE TABLE IF NOT EXISTS quotes(
                id INT AUTO_INCREMENT PRIMARY KEY ,
                quote TEXT
            );
            """,

            """
            CREATE TABLE IF NOT EXISTS totems(
                id INT AUTO_INCREMENT PRIMARY KEY ,
                emoji_code TINYTEXT,
                text TINYTEXT
            );
            """,

            """
            ALTER TABLE totems CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """,

            """
            CREATE TABLE IF NOT EXISTS triggers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                action_text TEXT,
                reaction_text TEXT
            );
            """,

            """
            ALTER TABLE triggers CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """,

        ]

        for query in sql_queries:
            cursor.execute(query)

        db.commit()
        cursor.close()
        db.close()
        return f"Повідомлення від БАЗИ:\nТаблиці успішно створені ! Тепер можеш використовувати інші команди\n\n"
    except mysql.connector.Error as e:
        logging.warning(f"Warning in create_tables: {e}")
        return f"Повідомлення від БАЗИ:\nОй, а таблиці то вже створені. Можеш більше не тикати цю команду )\n\n"


def insert_totems():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        cursor.execute("SELECT COUNT(*) FROM totems")
        row_count = cursor.fetchone()[0]
        if row_count == 0:

            for text, emoji_code in all_quotes.animals_dict.items():
                sql = "INSERT INTO totems (emoji_code, text) VALUES (%s, %s)"
                values = (emoji_code.encode('unicode-escape').decode('utf-8'), text)
                cursor.execute(sql, values)
                db.commit()

            cursor.close()
            db.close()
            return f"Повідомлення від БАЗИ:\nБазові тотеми додані у таблицю.\n\n"
        else:
            return f"Повідомлення від БАЗИ:\nТотеми вже є у таблиці.\n\n"
    except mysql.connector.Error as e:
        logging.error(f"Error in insert_totems: {e}")


def insert_quotes():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        cursor.execute("SELECT COUNT(*) FROM quotes")
        row_count = cursor.fetchone()[0]

        if row_count == 0:

            all_quotes_lists = [
                all_quotes.quotes_from_rozdil_lviv_ua_aphorisms,
                all_quotes.ukrainian_writers_quotes,
                all_quotes.programming_quotes,
                all_quotes.for_students_quotes,
                all_quotes.ukrainian_quotes_1,
                all_quotes.ukrainian_quotes_2
            ]

            for quotes_list in all_quotes_lists:
                for quote in quotes_list:
                    sql = "INSERT INTO quotes (quote) VALUES (%s)"
                    values = (quote,)
                    cursor.execute(sql, values)
                db.commit()

            cursor.close()
            db.close()
            return f"Повідомлення від БАЗИ:\nЦитати додані у таблицю.\n\n"
        else:
            return f"Повідомлення від БАЗИ:\nЦитати вже є у таблиці.\n\n"

    except mysql.connector.Error as e:
        logging.error(f"Error in insert_quotes: {e}")


def insert_sticker_packs():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        cursor.execute("SELECT COUNT(*) FROM sticker_packs")
        row_count = cursor.fetchone()[0]

        if row_count == 0:

            sticker_packs = [
                "going_insane",
                "kdflgklgsgrejkl",
                "jeeba"
            ]

            for sticker_pack in sticker_packs:
                sql = "INSERT INTO sticker_packs (sticker_pack_name) VALUES (%s)"
                values = (sticker_pack,)
                cursor.execute(sql, values)
                db.commit()

            cursor.close()
            db.close()
            return f"Повідомлення від БАЗИ:\nДефолтні стікерпаки додані у таблицю.\n\n"
        else:
            return f"Повідомлення від БАЗИ:\nСтікерпаки вже є у таблиці.\n\n"

    except mysql.connector.Error as e:
        logging.error(f"Error in insert_sticker_packs: {e}")


def insert_emojies():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        cursor.execute("SELECT COUNT(*) FROM emojies")
        row_count = cursor.fetchone()[0]

        if row_count == 0:

            emoji_code_list = [
                "\U0001F642",
                "\U0001F602",
                "\U0001F618"
            ]

            for emoji_code in emoji_code_list:
                sql = "INSERT INTO emojies (emoji_code) VALUES (%s)"
                values = (database.get_emoji_unicode(emoji_code),)
                cursor.execute(sql, values)
                db.commit()

            cursor.close()
            db.close()
            return f"Повідомлення від БАЗИ:\nДефолтні emojies додані у таблицю.\n\n"
        else:
            return f"Повідомлення від БАЗИ:\nEmojies вже є у таблиці.\n\n"

    except mysql.connector.Error as e:
        logging.error(f"Error in insert_emojies: {e}")


def insert_triggers():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        cursor.execute("SELECT COUNT(*) FROM triggers")
        row_count = cursor.fetchone()[0]

        if row_count == 0:
            triggers_list = [
                (config.ADD_STICKER_PACK, 'Додає стікерпак'),
                (config.DELETE_STICKER_PACK, 'Видаляє стікерпак'),
                (config.ADD_EMOJI, 'Додає емодзі'),
                (config.DELETE_EMOJI, 'Видаляє емодзі'),
                ('+', 'Додає репутацію'),
                ('-', 'Забирає репутацію'),
                (config.MUTE_USER, 'Замутити юзера'),
                (config.UNMUTE_USER, 'Размутити юзера'),
                ("дякую", "ПОДЯКУВАЛА(-В)"),
            ]

            for action_text, reaction_text in triggers_list:
                sql = "INSERT INTO triggers (action_text, reaction_text) VALUES (%s, %s)"
                values = (action_text, reaction_text)
                cursor.execute(sql, values)
                db.commit()

            cursor.close()
            db.close()
            return f"Повідомлення від БАЗИ:\nТриггери додані у таблицю.\n\n"
        else:
            return f"Повідомлення від БАЗИ:\nТриггери вже є у таблиці.\n\n"

    except mysql.connector.Error as e:
        logging.error(f"Error in insert_triggers: {e}")
