import random
import create_data_base


def send_rules():
    with open("text_files/rules.txt", "r", encoding="utf-8") as file_rules:
        text_2 = file_rules.read()
    return text_2


def send_situation(chat_id):
    query = 'select situation from sent_situation WHERE chat_id =?'
    create_data_base.cursor.execute(query, (chat_id,))
    last_record = create_data_base.cursor.fetchall()
    sent_situations = [row[0] for row in last_record]

    with open("text_files/situation.txt", "r", encoding="utf-8") as file:
        text = file.read().splitlines()

    avialible_situations = set(text) - set(sent_situations)
    if len(avialible_situations) > 0:
        random_str = random.randint(0, len(avialible_situations) - 1)
        sit_to_send = list(avialible_situations)[random_str].strip()
    else:
        sit_to_send = 'Ситуации закончились :('

    return sit_to_send


def send_welcome_text():
    with open("text_files/welcome_text.txt", "r", encoding="utf-8") as file:
        text = file.read()
    return text


def dilimeter():
    path = 'img/delimiter/1.png'
    file = read_image_bytes(path)
    return file


def send_description():
    with open("text_files/description.txt", "r", encoding="utf-8") as file:
        text = file.read()
    return text


def read_image_bytes(image_path: str):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    return image_bytes
