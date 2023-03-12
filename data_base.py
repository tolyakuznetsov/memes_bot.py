import sqlite3

# Создаем соединение с базой данных
conn = sqlite3.connect('data_base/db.db')
cursor = conn.cursor()

# Создаем таблицу, если ее еще нет
cursor.execute('''CREATE TABLE IF NOT EXISTS sent_images
                  (id INTEGER, user_id TEXT, chat_id TEXT, image_path TEXT, in_hand BOOLEAN, PRIMARY KEY (id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS user_chat
                  (id INTEGER, user_id TEXT, chat_id TEXT, PRIMARY KEY (id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS card_in_hand
                  (id INTEGER, user_id TEXT, chat_id TEXT, file_id TEXT, in_hand BOOLEAN, PRIMARY KEY (id))''')

conn.commit()
