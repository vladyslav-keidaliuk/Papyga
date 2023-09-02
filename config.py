import mysql
import mysql.connector
import os

TOKEN = os.environ['TOKEN']
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
YOUTUBE_MUSIC_API_KEY = os.environ['YOUTUBE_MUSIC_API_KEY']

GROUP_ID = 0

def db_connection():
    db = mysql.connector.connect(
        host=os.environ['MYSQL_HOST'],
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        database=os.environ['MYSQL_DATABASE']
    )
    return db

REACTION_FREQUENCY = 102
# Як часто буде реакція випадати, тобто через яку кількість повідомлень,
# позитивне число, рекомендується ставити від 100
# Якщо хочете відключити цю функцію, поставте 0
STICKER_FREQUENCY = 61
# Як часто буде стікер випадати, тобто через яку кількість повідомлень,
# позитивне число, рекомендується ставити від 50
# Якщо хочете відключити цю функцію, поставте 0

MOUNTAIN_HEIGHT = 300
# Висота гори (шахта протяжністю як і гора), допускаються тільки позитивні числа

BOT_USERNAME = os.environ['BOT_USERNAME']
# Після створення бота в BotFather замініть на username свого бота

TIMER_DURATION_HOURS = 12
# Відповідати буде за те, через яку кількість годин знову можна буде спробувати отримати нову цитату і тд
# Позитивне число


PLOTS_ENABLE = True
# Відповідає за наявність графіків для команд top і topm
# Графіки споживають досить багато ресурсів
# Тому якщо будете часто використовувати ці команди,
# рекомендується встановити значення False
# Якщо будете використовувати їх 1-2 рази на день, можете залишити True


LIMIT_IN_DE_BAYRAKTAR = 17
# Це значення відповідає за те,
# скільки максимально можливо отримати см (або втратити) за один прокрут.
# Це має бути позитивне ціле число

LIMIT_IN_DE_MOUNTAIN = 25
# Це значення відповідає за те,
# на скільки метрів можна піднятися (або впасти) за один прокрут.
# Це має бути позитивне ціле число

AGGRESSIVE_MODE_ENABLE = True
# якщо стоїть True, то адміністратори (і не тільки) зможуть мутити людей


START_OF_STUDY_WEEK_NUMBER = 36
# Тут треба вказати номер тижня (початку навчання) відносно року

MUTE_TIME_BY_ROULETTE = 600
# якщо юзеру випадає мут, то на таку кількість секунд йому буде заборонено писати в чат
# значення в секундах, НЕ МЕНШЕ 60, інакше йому взагалі буде заборонено писати в чат назавжди.

TIME_HB_TASKS_CHECK = "06:00"

TIME_HB = "07:50"
# У який час за дефолтом буде приходити привітання людини з ДН

TIME_UNPIN_LAST_MESSAGE = "20:00"
# У який час буде відкріплюватися останнє прикріплене ботом повідомлення


# КОМАНДИ
COMMAND_START = 'start'
COMMAND_TIME_LEFT = 'tleft'
COMMAND_ROULETTE = 'reel'
COMMAND_TRIGGERS = 'triggers'
COMMAND_UNPIN_BOT_MESSAGES = 'unpin'
COMMAND_WHO_I_AM = 'whoi'
COMMAND_UPGRADE_BAYRAKTAR = 'upgrade'
COMMAND_MOUNTAIN_AND_THE_MINE = 'mountain'
COMMAND_TOP_BAYRAKTAR = 'top'
COMMAND_TOP_MOUNTAIN_AND_THE_MINE = 'topm'
COMMAND_GET_TRACK = 'music'
COMMAND_ALARM = 'alarm'
COMMAND_ALL_TASKS = 'tasks'
COMMAND_ALL_INTERVALS = 'intervals'
COMMAND_ALL_PLAYLISTS = 'playlists'
COMMAND_ALL_BIRTHDAYS = 'birthdays'
COMMAND_ALL_TOTEMS = 'totems'
COMMAND_ALL_EMOJIES = 'emojies'
COMMAND_ALL_TRIGGERS = 'triggers'

ADD_PLAYLIST = "add_playlist"

ADD_BIRTHDAY = "add_birthday"
DELETE_BIRTHDAY = "delete_birthday"

ADD_TOTEM = "add_totem"
DELETE_TOTEM = "delete_totem"

CREATE_TASK = "ctask"
DELETE_TASK = "dtask"

CHANGE_NICKNAME = "нік++"

ADD_INTERVAL = "in_add"
DELETE_INTERVAL = "in_delete"

ADD_STICKER_PACK = 'sp_add'
DELETE_STICKER_PACK = 'sp_delete'

MUTE_USER = 'mute'
UNMUTE_USER = 'unmute'

ADD_EMOJI = 'em_add'
DELETE_EMOJI = 'em_delete'# у відповідь на емодзі відправити
DELETE_EMOJI_BY_INDEX = 'emi_delete'

ADD_TRIGGER = 'add_trigger'
DELETE_TRIGGER = 'delete_trigger'

HANDLER_WHO_YOU = 'хто ти'
HANDLER_SMART = 'розумник'

PAIR_OR_LESSON = True
# Це треба для коректного відображення в tleft
# Якщо у Вас пари (універ) залишаєте True, якщо ж у Вас уроки,
# то змінюємо значення на False

