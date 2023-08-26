import io
import matplotlib.pyplot as plt
import database
import logging


def get_plot_top_mountain(user_id):
    res = database.db_connect()
    cursor = res[1]
    db = res[0]
    try:
        query = "SELECT user_id, passmountain FROM Users WHERE passmountain IS NOT NULL"
        cursor.execute(query)
        data = cursor.fetchall()
        if data:
            db.close()

            user_ids, passmountains = zip(*data)

            usernames = []
            for user_id in user_ids:
                username = database.get_username(user_id)
                usernames.append(username)

            sorted_indices = sorted(range(len(passmountains)), key=lambda k: passmountains[k])
            usernames = [usernames[i] for i in sorted_indices]
            passmountains = [passmountains[i] for i in sorted_indices]

            plt.subplots_adjust(left=0.3)

            fig, ax = plt.subplots(figsize=(8, 6))

            colors = ['#540d0d' if pm < 0 else '#0252a3' for pm in passmountains]

            ax.barh(usernames, passmountains, color=colors)
            ax.set_xlabel('')
            ax.set_ylabel('Імена користувачів')
            ax.set_title('Шахта     ||     Гора')
            fig.subplots_adjust(left=0.3)

            image_stream = io.BytesIO()
            plt.savefig(image_stream, format='png')
            image_stream.seek(0)

            return image_stream
    except Exception as e:
        logging.error(f"Error in plots.py - get_plot_top_mountain: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_plot_top_bayraktar():
    res = database.db_connect()
    cursor = res[1]
    db = res[0]
    try:

        query = "SELECT user_id, size FROM Users WHERE size IS NOT NULL"
        cursor.execute(query)
        data = cursor.fetchall()

        db.close()

        user_ids, size = zip(*data)

        usernames = []
        for user_id in user_ids:
            username = database.get_username(user_id)
            usernames.append(username)

        sorted_indices = sorted(range(len(size)), key=lambda k: size[k])
        usernames = [usernames[i] for i in sorted_indices]
        size = [size[i] for i in sorted_indices]

        plt.subplots_adjust(left=0.3)

        fig, ax = plt.subplots(figsize=(8, 6))

        color = '#0057B7'
        edge_color = '#FFDD00'
        linewidth = 2

        ax.barh(usernames, size, color=color, edgecolor=edge_color, linewidth=linewidth)
        ax.set_xlabel('')
        ax.set_ylabel('Імена користувачів')
        ax.set_title('Таблиця Байрактарів')
        fig.subplots_adjust(left=0.3)

        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)

        return image_stream
    except Exception as e:
        logging.error(f"Error in plots: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
