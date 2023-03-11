import sqlite3

# Создаем соединение с базой данных
conn = sqlite3.connect('data_base/sent_images.db')
cursor = conn.cursor()

# Создаем таблицу, если ее еще нет
cursor.execute('''CREATE TABLE IF NOT EXISTS sent_images
                  (id INTEGER, user_id TEXT, image_path TEXT, chat_id TEXT, PRIMARY KEY (id))''')
conn.commit()
