import datetime
import logging
import random

import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import config
import database

try:
    client_id = config.SPOTIFY_CLIENT_ID
    client_secret = config.SPOTIFY_CLIENT_SECRET
    redirect_uri = 'http://localhost:8000/callback'

    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
except:
    print("ERROR")


def get_track_info(track_url):
    track_id = track_url.split('/')[-1].split('?')[0]
    track_info = sp.track(track_id)
    track_name = track_info['name']
    composer = track_info['album']['artists'][0]['name']

    return track_name, composer


def get_playlist_tracks_links(playlist_id):
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    offset = 0
    limit = 100
    tracks_links = []

    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        items = results['items']
        if len(items) == 0:
            break
        for item in items:
            track_link = item['track']['external_urls']['spotify']
            tracks_links.append(track_link)
        offset += limit

    return tracks_links


def get_favorite_tracks_links():
    scope = 'user-library-read'
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri,
                                  scope=scope))

    offset = 0
    limit = 50
    tracks_links = []

    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = results['items']
        if len(items) == 0:
            break
        for item in items:
            track_link = item['track']['external_urls']['spotify']
            tracks_links.append(track_link)
        offset += limit

    return tracks_links


def get_playlist_title(message):
    data = message.text.split('\n')
    link = data[1]
    playlist = sp.playlist(link)
    playlist_name = playlist['name']
    return playlist_name


def get_songs_from_playlist(message):
    try:
        data = message.text.split('\n')
        link = data[1]
        playlist_tracks = get_playlist_tracks_links(link)
        tmp_tracks = {}
        for track_link in playlist_tracks:
            track_info = get_track_info(track_link)
            key = track_link
            value = track_info
            tmp_tracks[key] = value

        text = ""
        counter = 0
        for track_link, track_info in tmp_tracks.items():
            counter += 1
            text += f'\n{counter} Track Link: {track_link} Track Info: Title:{track_info[0]} Artist: {track_info[1]}'

        playlist_title = get_playlist_title(message)

        return text

    except Exception as e:
        return f"Ти щось не так записав.Спробуй ще раз. Помилка({e})"


def insert_tracks_in_db(message):
    try:
        data = message.text.split('\n')
        link = data[1]
        playlist_tracks = get_playlist_tracks_links(link)
        tmp_tracks = {}
        for track_link in playlist_tracks:
            track_info = get_track_info(track_link)
            key = track_link
            value = track_info
            tmp_tracks[key] = value

        res = database.db_connect()
        cursor = res[1]
        db = res[0]
        playlist_title = get_playlist_title(message)

        for track_link, track_info in tmp_tracks.items():
            link = track_link
            title = track_info[0]
            artist = track_info[1]
            playlist = playlist_title

            insert_query = "INSERT INTO music (link, title, artist, playlist) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (link, title, artist, playlist))

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

        return "Плейлист успішно додано!"

    except mysql.connector.Error as e:
        logging.error(f"Error in insert_tracks_in_db db : {e}")
        return f"Не вдалось додати плейлист Помилка: {str(e)}"
    except Exception as e:
        logging.error(f"Error in insert_tracks_in_db: {e}")
        return f"Не вдалось додати плейлист.\n" \
               f"Можлива помилка: Відсутній API ключ.\n" \
               f"Детальна помилка: {e}"


def get_count_tracks():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        query = "SELECT COUNT(*) FROM music"
        cursor.execute(query)

        result = cursor.fetchone()
        row_count = result[0]

        cursor.close()
        db.close()
        return row_count

    except Exception as e:
        logging.error(f"Error in get_count_tracks : {e}")


def get_random_track():
    try:
        res = database.db_connect()
        cursor = res[1]
        db = res[0]

        track_id = random.randint(1, database.get_count_rows_in_table("music"))

        query = "SELECT link, title, artist, playlist FROM music WHERE id = %s"
        cursor.execute(query, (track_id,))

        result = cursor.fetchone()

        cursor.close()
        db.close()

        link, title, artist, playlist = result

        return link, title, artist, playlist

    except mysql.connector.Error as e:
        logging.error(f"Error in get_random_track db : {e}")
    except Exception as e:
        logging.error(f"Error in get_random_track : {e}")
        return "https://open.spotify.com/", f"Помилка: {e}", "Можливо у БД нема жодного треку.", "Помилка"
