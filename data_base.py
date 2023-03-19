import sqlite3

# Создаем соединение с базой данных
conn = sqlite3.connect('data_base/db.db')
cursor = conn.cursor()

# Создаем таблицу, если ее еще нет
cursor.execute('''CREATE TABLE IF NOT EXISTS sent_images
                  (id INTEGER, uniq_id TEXT, user_id TEXT, chat_id TEXT, image_path TEXT, in_hand BOOLEAN, 
                  PRIMARY KEY (id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS user_chat_file_id
                  (id INTEGER, uniq_id TEXT, user_id TEXT, chat_id TEXT, file_id TEXT, PRIMARY KEY (id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS card_in_hand
                  (id INTEGER, uniq_id TEXT, user_id TEXT, file_id TEXT, in_hand BOOLEAN, PRIMARY KEY (id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS user_sent_card
                  (id INTEGER, user_id TEXT, file_id TEXT, PRIMARY KEY (id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS user_sent_cards
                  (id INTEGER, user_id TEXT, chat_id TEXT, sent_card BOOLEAN, PRIMARY KEY (id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS sent_situation
                  (id INTEGER, chat_id TEXT, situation TEXT, PRIMARY KEY (id))''')

conn.commit()
