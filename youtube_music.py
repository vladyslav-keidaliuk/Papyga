import logging

import mysql.connector
from googleapiclient.discovery import build
import re
import config
import datetime
import database


def insert_tracks_in_db(message):
    res = database.db_connect()
    cursor = res[1]
    db = res[0]
    try:
        data = message.text.split('\n')
        playlist__link = data[1]
        count_tracks = int(data[2])

        api_key = config.YOUTUBE_MUSIC_API_KEY

        playlist_id = re.findall(r'list=([a-zA-Z0-9_-]+)', playlist__link)

        if not playlist_id:
            return "Посилання на плейлист - інвалід."

        youtube = build('youtube', 'v3', developerKey=api_key)

        playlist_response = youtube.playlists().list(
            part='snippet',
            id=playlist_id[0]
        ).execute()

        playlist_title = playlist_response['items'][0]['snippet']['title']

        next_page_token = None
        playlist_items = []
        while len(playlist_items) < count_tracks:
            playlist_items_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id[0],
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            playlist_items.extend(playlist_items_response['items'])
            next_page_token = playlist_items_response.get('nextPageToken')

            if next_page_token is None:
                break

        playlist_items = playlist_items[:count_tracks]

        for track in playlist_items:
            track_title = track['snippet']['title']
            track_video_id = track['snippet']['resourceId']['videoId']
            track_url = f"https://www.youtube.com/watch?v={track_video_id}"

            insert_query = "INSERT INTO music (link, title, artist, playlist) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (track_url, track_title, "Нема", playlist_title))
            db.commit()

        current_date = datetime.date.today()
        dtime = current_date.strftime("%d.%m.%Y")
        query = "INSERT INTO playlists (playlist,datetime) VALUES (%s,%s)"
        cursor.execute(query, (playlist_title, dtime))
        db.commit()

        drop_column_query = "ALTER TABLE music DROP COLUMN id"
        cursor.execute(drop_column_query)
        db.commit()

        add_column_query = "ALTER TABLE music ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
        cursor.execute(add_column_query)
        db.commit()

        cursor.close()
        db.close()

        cursor.close()
        db.close()

        return "Плейлист успішно додано!"
    except mysql.connector.Error as e:
        logging.error(f"Error in insert_tracks_in_db db: {e}")
        return f"Не вдалось додати плейлист Помилка: {str(e)}"
    except Exception as e:
        logging.error(f"Error in insert_tracks_in_db : {e}")
        return f"Не вдалось додати плейлист.\n" \
               f"Можливі помилки: \n" \
               f"- Відсутній API ключ.\n" \
               f"- Бите посилання.\n" \
               f"- Вказано треків більше ніж у плейлисті.\n" \
               f"- Невірний формат запису."
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
