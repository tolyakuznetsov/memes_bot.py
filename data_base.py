import sqlite3

# Создаем соединение с базой данных
conn = sqlite3.connect('sent_images.db')
cursor = conn.cursor()

# Создаем таблицу, если ее еще нет
cursor.execute('''CREATE TABLE IF NOT EXISTS sent_images
                  (id INTEGER, user_id INTEGER, image_path TEXT, chat_id INTEGER, PRIMARY KEY (id))''')
conn.commit()
