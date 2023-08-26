import logging

import database


def drop_all_tables():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        tables_to_drop = [
            "Users",
            "tasks",
            "music",
            "playlists",
            "birthdays",
            "pinned_messages",
            "sticker_packs",
            "emojies",
            "intervals",
            "quotes",
            "totems",
            "triggers"
        ]
        text = ""
        for table_name in tables_to_drop:
            sql = f"DROP TABLE {table_name};"
            cursor.execute(sql)
            text += f"\nТаблиця {table_name} була видалена."

        cursor.close()
        db.close()
        print(text)
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error in drop_all_tables db: {e}")


drop_all_tables()
