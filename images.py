import os
import data_base
import random
import uuid
from typing import List, Tuple


def get_image_files(path: str):
    files = os.listdir(path)
    image_files = [f for f in files if f.endswith('.jpg') or f.endswith('.png')]
    return image_files


def get_available_images(chat_id: int, user_id: int, available_images: list):
    in_hand = True
    query = 'SELECT image_path from sent_images si \
             JOIN card_in_hand cih on si.uniq_id = cih.uniq_id \
             WHERE (si.chat_id =? and si.user_id =? and cih.in_hand =?)'
    data_base.cursor.execute(query, (chat_id, user_id, in_hand))
    sent_images = data_base.cursor.fetchall()
    sent_image_paths = [img[0] for img in sent_images]
    available_images = list(set(available_images) - set(sent_image_paths))
    return available_images


def add_image_to_database(uniq_id, user_id: int, chat_id: int, image_path: str, in_hand: bool):
    data_base.cursor.execute("INSERT INTO sent_images (uniq_id, user_id, chat_id, image_path, in_hand) "
                             "VALUES (?, ?, ?, ?, ?)",
                             (uniq_id, user_id, chat_id, image_path, in_hand))
    data_base.conn.commit()


def read_image_bytes(image_path: str):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    return image_bytes


def open_random_images(count_images: int, path: str, chat_id: int, user_id: int) -> List[Tuple[bytes, str]]:
    image_files = get_image_files(path)
    if image_files:
        available_images = [os.path.join(path, i) for i in image_files]
        available_images = get_available_images(chat_id, user_id, available_images)
        num_available_images = len(available_images)
        if num_available_images > 0:
            count_images = min(count_images, num_available_images)
            random_images = random.sample(available_images, count_images)
            image_list = []
            for random_image in random_images:
                image_path = random_image
                image_bytes = read_image_bytes(image_path)
                image_list.append((image_bytes, image_path))
            return image_list
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
