import os
import json
import create_data_base
import random
import uuid
from typing import List, Tuple
import open_files as of


def generate_uuid():
    return str(uuid.uuid4())


def get_image_files(path: str):
    files = os.listdir(path)
    image_files = [f for f in files if f.endswith('.jpg') or f.endswith('.png')]
    return image_files


def clean_db(chat_id):
    db_clean_keyboard(chat_id)
    db_clean_situations(chat_id)
    db_clean_user_hero(chat_id)
    db_clean_user_sent_card(chat_id)
    db_clean_user_sent_cards(chat_id)
    db_clean_card_in_hand(chat_id)
    db_clean_states(chat_id)


def get_available_images(chat_id: int, user_id: int, available_images: list):
    query_in_hand = 'SELECT image_path from sent_images si \
             JOIN card_in_hand cih on si.uniq_id = cih.uniq_id \
             WHERE (si.chat_id =? and si.user_id =? and cih.in_hand =?)'
    create_data_base.cursor.execute(query_in_hand, (chat_id, user_id, True))
    sent_images_in_hand = create_data_base.cursor.fetchall()

    query_not_hand = 'SELECT image_path from sent_images si \
                 JOIN card_in_hand cih on si.uniq_id = cih.uniq_id \
                 WHERE (si.chat_id =? and si.user_id =? and cih.in_hand =?)'
    create_data_base.cursor.execute(query_not_hand, (chat_id, user_id, False))
    sent_images_not_hand = create_data_base.cursor.fetchall()

    sent_images_not_hand_paths = set([img[0] for img in sent_images_not_hand])

    sent_image_in_hand_paths = set([img[0] for img in sent_images_in_hand])
    available_images = list(set(available_images) - set(sent_image_in_hand_paths) - set(sent_images_not_hand_paths))
    return sent_image_in_hand_paths, available_images


def add_image_to_database(uniq_id, user_id: int, chat_id: int, image_path: str, in_hand: bool):
    create_data_base.cursor.execute("INSERT INTO sent_images (uniq_id, user_id, chat_id, image_path, in_hand) "
                                    "VALUES (?, ?, ?, ?, ?)",
                                    (uniq_id, user_id, chat_id, image_path, in_hand))
    create_data_base.conn.commit()


def open_random_images(chat_id: int, user_id: int) -> List[Tuple[bytes, str]]:
    path = 'img'
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
                    image_bytes = of.read_image_bytes(image_path)
                    image_list.append((image_bytes, image_path))
                return image_list
        return []
    elif image_files == 5:
        return []


def save_user_chat_to_db(uniq_id, user_id, chat_id, file_id):
    create_data_base.cursor.execute("INSERT INTO user_chat_file_id (uniq_id, user_id, chat_id, file_id) VALUES (?, ?, "
                                    "?, ?)",
                                    (uniq_id, user_id, chat_id, file_id))
    create_data_base.conn.commit()


def get_mapp_user_chat(user_id):
    query = 'select chat_id from user_chat_file_id WHERE user_id =? ORDER by id DESC LIMIT 1'
    create_data_base.cursor.execute(query, (user_id,))
    last_record = create_data_base.cursor.fetchall()
    sent_image_paths = [i[0] for i in last_record]
    return sent_image_paths[0]


def db_save_card_in_hand(uniq_id, user_id, chat_id, file_id, in_hand):
    query = 'INSERT INTO card_in_hand (uniq_id, user_id, chat_id, file_id, in_hand) VALUES (?, ?, ?, ?, ?)'
    values = (uniq_id, user_id, chat_id, file_id, in_hand)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def update_in_hand_flag(file_id, user_id, in_hand):
    query = "UPDATE card_in_hand SET in_hand = ? WHERE file_id = ? AND user_id = ?"
    values = (in_hand, file_id, user_id)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def delete_images_from_db(user_id, chat_id):
    query_sent_images = 'DELETE FROM sent_images ' \
                        'WHERE chat_id = ?'
    values_sent_images = (chat_id,)
    create_data_base.cursor.execute(query_sent_images, values_sent_images)
    create_data_base.conn.commit()

    query_card_in_hand = 'DELETE FROM card_in_hand ' \
                         'WHERE user_id = ?'
    values_card_in_hand = (user_id,)
    create_data_base.cursor.execute(query_card_in_hand, values_card_in_hand)
    create_data_base.conn.commit()

    query_card_in_hand = 'DELETE FROM user_chat_file_id ' \
                         'WHERE chat_id = ?'
    values_user_chat_file_id = (chat_id,)
    create_data_base.cursor.execute(query_card_in_hand, values_user_chat_file_id)
    create_data_base.conn.commit()
    return 'Игра закончена'


def check_image_in_db(file_id):
    query = 'SELECT file_id from user_sent_card ' \
            'WHERE file_id =?'
    values = (file_id,)
    create_data_base.cursor.execute(query, values)
    images = create_data_base.cursor.fetchall()
    if images:
        return True
    elif not images:
        return False


def db_insert_user_sent_card(user_id, chat_id, file_id):
    query = 'INSERT INTO user_sent_card (user_id, chat_id, file_id) VALUES (?, ?, ?)'
    values = (user_id, chat_id, file_id)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_insert_user_done_turn(user_id, chat_id, sent_card):
    query = 'INSERT INTO user_sent_cards (user_id, chat_id, sent_card) VALUES (?, ?, ?)'
    values = (user_id, chat_id, sent_card)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_update_user_done_turn(user_id, chat_id, sent_card):
    query = "UPDATE user_sent_cards SET sent_card = ? WHERE user_id = ? AND chat_id = ?"
    values = (sent_card, user_id, chat_id)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def user_sent_cards_in_turn(user_id, chat_id, sent_card):
    query = 'SELECT user_id from user_sent_cards ' \
            'WHERE user_id =? and chat_id =? and sent_card=?'
    values = (user_id, chat_id, sent_card)
    create_data_base.cursor.execute(query, values)
    images = create_data_base.cursor.fetchall()
    if images:
        return True
    elif not images:
        return False


def db_delete_sent_cards_in_turn(user_id, chat_id):
    query_sent_images = 'DELETE FROM user_sent_cards ' \
                        'WHERE user_id = ? and chat_id =?'
    values_sent_images = (user_id, chat_id)
    create_data_base.cursor.execute(query_sent_images, values_sent_images)
    create_data_base.conn.commit()


def db_insert_situation(chat_id, situation):
    query = 'INSERT INTO sent_situation (chat_id, situation) VALUES (?, ?)'
    values = (chat_id, situation)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_clean_situations(chat_id):
    query = 'DELETE FROM sent_situation ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_insert_keyboard(keyboard, chat_id, user_id, button):
    query = 'INSERT INTO keyboards (keyboard, chat_id, user_id, button) VALUES (?, ?, ?, ?)'
    values = (keyboard, chat_id, user_id, button)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_select_keyboard(keyboard, chat_id):
    query = 'SELECT button from keyboards ' \
            'WHERE keyboard =? and chat_id =?'
    values = (keyboard, chat_id)
    create_data_base.cursor.execute(query, values)
    button_str = create_data_base.cursor.fetchone()[0]
    button = json.loads(button_str)
    return button


def db_update_keyboard(button, keyboard, chat_id):
    query = "UPDATE keyboards SET button = ? WHERE keyboard =? and chat_id = ?"
    values = (button, keyboard, chat_id)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_delete_keyboard(keyboard, chat_id):
    query = 'DELETE FROM keyboards ' \
            'WHERE keyboard =? and chat_id =?'
    values = (keyboard, chat_id,)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_clean_keyboard(chat_id):
    query = 'DELETE FROM keyboards ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_insert_user_hero(chat_id, user_id, hero):
    query = 'INSERT INTO user_hero (chat_id, user_id, hero) VALUES (?, ?, ?)'
    values = (chat_id, user_id, hero)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_select_user_hero(chat_id, user_id):
    query = 'SELECT hero from user_hero ' \
            'WHERE chat_id =? and user_id =?'
    values = (chat_id, user_id)
    create_data_base.cursor.execute(query, values)
    hero = create_data_base.cursor.fetchall()
    if hero:
        return hero[0][0]
    else:
        return False


def db_select_check_count_players(chat_id):
    query = 'SELECT count(hero) from user_hero ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    count_users = create_data_base.cursor.fetchall()[0][0]
    return count_users


def db_select_pool_heroes(chat_id):
    query = 'SELECT hero from user_hero ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    heroes = create_data_base.cursor.fetchall()
    to_return = []
    for i in heroes:
        for j in i:
            to_return.append(j)
    return to_return

def db_select_pool_users(chat_id):
    query = 'SELECT user_id from user_hero ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    heroes = create_data_base.cursor.fetchall()
    to_return = []
    for i in heroes:
        for j in i:
            to_return.append(j)
    return to_return


def db_clean_user_hero(chat_id):
    query = "DELETE FROM user_hero " \
            "WHERE chat_id =?"
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_clean_user_sent_card(chat_id):
    query = 'DELETE FROM user_sent_card ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_clean_user_sent_cards(chat_id):
    query = 'DELETE FROM user_sent_cards ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()


def db_clean_card_in_hand(chat_id):
    query = 'DELETE FROM card_in_hand ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()

def db_update_state(chat_id, type, state):
    query = 'INSERT INTO states (chat_id, type, active) VALUES (?, ?, ?) ' \
            'ON CONFLICT(chat_id) DO UPDATE SET type=?, active=?'
    values = (chat_id, type, state, type, state)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()

def db_get_state(chat_id, type):
    query = 'SELECT active FROM states ' \
            'WHERE chat_id=? AND type=?'
    values = (chat_id, type)
    create_data_base.cursor.execute(query, values)
    state = create_data_base.cursor.fetchall()[0][0]
    return state

def db_clean_states(chat_id):
    query = 'DELETE FROM states ' \
            'WHERE chat_id =?'
    values = (chat_id,)
    create_data_base.cursor.execute(query, values)
    create_data_base.conn.commit()
