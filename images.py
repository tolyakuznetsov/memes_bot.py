import os
import json

import data_base
import random
import uuid
from typing import List, Tuple


def get_image_files(path: str):
    files = os.listdir(path)
    image_files = [f for f in files if f.endswith('.jpg') or f.endswith('.png')]
    return image_files


def get_available_images(chat_id: int, user_id: int, available_images: list):
    query_in_hand = 'SELECT image_path from sent_images si \
             JOIN card_in_hand cih on si.uniq_id = cih.uniq_id \
             WHERE (si.chat_id =? and si.user_id =? and cih.in_hand =?)'
    data_base.cursor.execute(query_in_hand, (chat_id, user_id, True))
    sent_images_in_hand = data_base.cursor.fetchall()

    query_not_hand = 'SELECT image_path from sent_images si \
                 JOIN card_in_hand cih on si.uniq_id = cih.uniq_id \
                 WHERE (si.chat_id =? and si.user_id =? and cih.in_hand =?)'
    data_base.cursor.execute(query_not_hand, (chat_id, user_id, False))
    sent_images_not_hand = data_base.cursor.fetchall()

    sent_images_not_hand_paths = set([img[0] for img in sent_images_not_hand])

    sent_image_in_hand_paths = set([img[0] for img in sent_images_in_hand])
    available_images = list(set(available_images) - set(sent_image_in_hand_paths) - set(sent_images_not_hand_paths))
    return sent_image_in_hand_paths, available_images


def add_image_to_database(uniq_id, user_id: int, chat_id: int, image_path: str, in_hand: bool):
    data_base.cursor.execute("INSERT INTO sent_images (uniq_id, user_id, chat_id, image_path, in_hand) "
                             "VALUES (?, ?, ?, ?, ?)",
                             (uniq_id, user_id, chat_id, image_path, in_hand))
    data_base.conn.commit()


def read_image_bytes(image_path: str):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    return image_bytes


def open_random_images(chat_id: int, user_id: int) -> List[Tuple[bytes, str]]:
    path = '/Users/anatoliykuznecov/PycharmProjects/bot/img'
    image_files = get_image_files(path)
    if image_files:
        available_images = [os.path.join(path, i) for i in image_files]
        available_images = get_available_images(chat_id, user_id, available_images)
        sent_images = list(available_images[0])
        available_images = available_images[1]
        count_sent_images = len(sent_images)
        count_available_images = len(available_images)
        if count_sent_images < 5:
            count = 5 - count_sent_images
            if count_available_images + count_sent_images < 5:
                return []
            else:
                random_images = random.sample(available_images, count)
                list_images_to_send = sent_images + random_images
                image_list = []
                for random_image in list_images_to_send:
                    image_path = random_image
                    image_bytes = read_image_bytes(image_path)
                    image_list.append((image_bytes, image_path))
                return image_list
        return []
    elif image_files == 5:
        return []


def generate_uuid():
    return str(uuid.uuid4())


def save_user_chat_to_db(uniq_id, user_id, chat_id, file_id):
    data_base.cursor.execute("INSERT INTO user_chat_file_id (uniq_id, user_id, chat_id, file_id) VALUES (?, ?, ?, ?)",
                             (uniq_id, user_id, chat_id, file_id))
    data_base.conn.commit()


def get_mapp_user_chat(user_id):
    query = 'select chat_id from user_chat_file_id WHERE user_id =? ORDER by id DESC LIMIT 1'
    data_base.cursor.execute(query, (user_id,))
    last_record = data_base.cursor.fetchall()
    sent_image_paths = [i[0] for i in last_record]
    return sent_image_paths[0]


def db_save_card_in_hand(uniq_id, user_id, file_id, in_hand):
    query = 'INSERT INTO card_in_hand (uniq_id, user_id, file_id, in_hand) VALUES (?, ?, ?, ?)'
    values = (uniq_id, user_id, file_id, in_hand)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def update_in_hand_flag(file_id, user_id, in_hand):
    query = "UPDATE card_in_hand SET in_hand = ? WHERE file_id = ? AND user_id = ?"
    values = (in_hand, file_id, user_id)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def delete_images_from_db(user_id, chat_id):
    query_sent_images = 'DELETE FROM sent_images ' \
                        'WHERE chat_id = ?'
    values_sent_images = (chat_id,)
    data_base.cursor.execute(query_sent_images, values_sent_images)
    data_base.conn.commit()

    query_card_in_hand = 'DELETE FROM card_in_hand ' \
                         'WHERE user_id = ?'
    values_card_in_hand = (user_id,)
    data_base.cursor.execute(query_card_in_hand, values_card_in_hand)
    data_base.conn.commit()

    query_card_in_hand = 'DELETE FROM user_chat_file_id ' \
                         'WHERE user_id = ? and chat_id = ?'
    values_user_chat_file_id = (user_id, chat_id)
    data_base.cursor.execute(query_card_in_hand, values_user_chat_file_id)
    data_base.conn.commit()
    return 'Игра закончена'


def check_image_in_db(file_id):
    query = 'SELECT file_id from user_sent_card ' \
            'WHERE file_id =?'
    values = (file_id,)
    data_base.cursor.execute(query, values)
    images = data_base.cursor.fetchall()
    if images:
        return True
    elif not images:
        return False


def db_insert_user_sent_card(user_id, file_id):
    query = 'INSERT INTO user_sent_card (user_id, file_id) VALUES (?, ?)'
    values = (user_id, file_id)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def db_insert_user_done_turn(user_id, chat_id, sent_card):
    query = 'INSERT INTO user_sent_cards (user_id, chat_id, sent_card) VALUES (?, ?, ?)'
    values = (user_id, chat_id, sent_card)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def db_update_user_done_turn(user_id, chat_id, sent_card):
    query = "UPDATE user_sent_cards SET sent_card = ? WHERE user_id = ? AND chat_id = ?"
    values = (sent_card, user_id, chat_id)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def user_sent_cards_in_turn(user_id, chat_id, sent_card):
    query = 'SELECT user_id from user_sent_cards ' \
            'WHERE user_id =? and chat_id =? and sent_card=?'
    values = (user_id, chat_id, sent_card)
    data_base.cursor.execute(query, values)
    images = data_base.cursor.fetchall()
    if images:
        return True
    elif not images:
        return False


def db_delete_sent_cards_in_turn(user_id, chat_id):
    query_sent_images = 'DELETE FROM user_sent_cards ' \
                        'WHERE user_id = ? and chat_id =?'
    values_sent_images = (user_id, chat_id)
    data_base.cursor.execute(query_sent_images, values_sent_images)
    data_base.conn.commit()


def db_insert_situation(chat_id, situation):
    query = 'INSERT INTO sent_situation (chat_id, situation) VALUES (?, ?)'
    values = (chat_id, situation)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def db_insert_pick_hero(chat_id, user_id, button):
    query = 'INSERT INTO buttons_pick_hero (chat_id, user_id, button) VALUES (?, ?, ?)'
    values = (chat_id, user_id, button)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def db_select_pick_hero(chat_id):
    query = 'SELECT button from buttons_pick_hero ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    data_base.cursor.execute(query, values)
    button_str = data_base.cursor.fetchone()[0]
    button = json.loads(button_str)
    return button


def db_update_pick_hero(keyboard, chat_id):
    query = "UPDATE buttons_pick_hero SET button = ? WHERE chat_id = ?"
    values = (keyboard, chat_id)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def db_delete_pick_hero(chat_id):
    query = 'DELETE FROM buttons_pick_hero ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def db_insert_user_hero(chat_id, user_id, hero):
    query = 'INSERT INTO user_hero (chat_id, user_id, hero) VALUES (?, ?, ?)'
    values = (chat_id, user_id, hero)
    data_base.cursor.execute(query, values)
    data_base.conn.commit()


def db_select_user_hero(chat_id, user_id):
    query = 'SELECT hero from user_hero ' \
            'WHERE chat_id =? and user_id =?'
    values = (chat_id, user_id)
    data_base.cursor.execute(query, values)
    hero = data_base.cursor.fetchall()[0][0]
    return hero
