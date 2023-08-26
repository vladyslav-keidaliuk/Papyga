import datetime
import logging
import mysql.connector
import pytz
from phrases import lists_phrases
import tz
import database
import config

def what_progress_in_percent(start_time, target_time, num_pair):
    try:
        start_datetime = datetime.datetime(datetime.date.today().year, datetime.date.today().month,
                                           datetime.date.today().day, start_time.hour, start_time.minute,
                                           start_time.second, start_time.microsecond)
        target_datetime = datetime.datetime(datetime.date.today().year, datetime.date.today().month,
                                            datetime.date.today().day, target_time.hour, target_time.minute,
                                            target_time.second, target_time.microsecond)

        if target_time < start_time:
            target_datetime += datetime.timedelta(days=1)

        time_diff = target_datetime - start_datetime
        total_seconds = time_diff.total_seconds()
        elapsed_seconds = (datetime.datetime.now() - start_datetime).total_seconds()
        percentage_elapsed = int(elapsed_seconds / total_seconds * 100)


        if config.PAIR_OR_LESSON:
            result = "Пройдено " + str(percentage_elapsed) + "% " + str(num_pair) + "-ї пари.\n"
        else:
            result = "Пройдено " + str(percentage_elapsed) + "% " + str(num_pair) + "-го уроки.\n"

        if 0 <= percentage_elapsed < 20:
            result = result + lists_phrases(20)
            return result
        elif 20 <= percentage_elapsed < 25:
            result = result + lists_phrases(2025)
            return result
        elif 25 <= percentage_elapsed < 50:
            result = result + lists_phrases(2550)
            return result
        elif 50 <= percentage_elapsed < 80:
            result = result + lists_phrases(5080)
            return result
        elif 80 <= percentage_elapsed <= 90:
            result = result + lists_phrases(8090)
            return result
        elif percentage_elapsed < 100:
            result = result + lists_phrases(90100)
            return result
    except Exception as e:
        logging.error(f"Error in what_pair_progress - what_progress_in_percent: {e}")


def what_pair():
    res = database.db_connect()
    cursor = res[1]
    db = res[0]
    try:

        cursor.execute("SELECT * FROM intervals")
        rows = cursor.fetchall()

        now = datetime.datetime.now().time()
        now_str = now.strftime("%H:%M")

        for row in rows:
            interval_id = row[0]
            start = row[1]
            end = row[2]
            start_time = datetime.datetime.strptime(start, "%H:%M").time()
            now_time = datetime.datetime.strptime(now_str, "%H:%M").time()
            end_time = datetime.datetime.strptime(end, "%H:%M").time()

            start_time_utc = tz.to_utc(start_time)
            end_time_utc = tz.to_utc(end_time)
            now_utc = tz.to_utc(now_time)


            current_time = datetime.datetime.now(pytz.utc).time()
            current_time_str = current_time.strftime("%H:%M:%S")
            current_date = datetime.datetime.now(pytz.utc).date()
            time_obj = datetime.datetime.strptime(current_time_str, "%H:%M:%S").time()
            result_datetime = datetime.datetime.combine(current_date, time_obj, tzinfo=pytz.utc)

            # Для хостингу
            if start_time_utc <= result_datetime <= end_time_utc:
                text = f"{what_progress_in_percent(start_time_utc, end_time_utc, interval_id)}"
                return text

            # # Локально
            # if start_time <= now_time <= end_time:
            #     text = f"{what_progress_in_percent(start_time, end_time, interval_id)}"
            #     return text

        if config.PAIR_OR_LESSON:
            text = "Зараз нема жодної пари, відпочиваємо 😴"
        else:
            text = "Зараз нема жодного уроку, відпочиваємо 😴"

        return text
    except mysql.connector.Error as e:
        logging.error(f"Error in what_pair db: {e}")
    except Exception as e:
        logging.error(f"Error in what_pair: {e}")
    finally:
        cursor.close()
        db.close()
