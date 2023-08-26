import subprocess

def install_libraries():
    libraries = ['telebot',
                 'schedule',
                 'mysql',
                 'mysql-connector-python',
                 'python-dateutil',
                 'emoji',
                 'matplotlib',
                 'spotipy',
                 'pytz',
                 'google-api-python-client'
                 ]

    for lib in libraries:
        try:
            subprocess.check_call(['pip', 'install', lib])
            print(f"\n!!! {lib} встановлена успішно.\n")
        except subprocess.CalledProcessError:
            print(f"\n!!! Помилка при установці {lib}.\n")
    print("Усі бібліотеки встановлені !")


if __name__ == "__main__":
    install_libraries()
