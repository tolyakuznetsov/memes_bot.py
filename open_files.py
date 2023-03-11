import random
import os
import data_base


def send_rules():
    with open("rules.txt", "r", encoding="utf-8") as file_rules:
        text_2 = file_rules.read()
    return text_2


def send_situation():
    random_str = random.randint(0, 3)
    with open("/Users/anatoliykuznecov/PycharmProjects/bot/situation.txt", "r", encoding="utf-8") as file:
        text = file.readlines()
    return text[random_str]


def send_welcome_text():
    with open("/Users/anatoliykuznecov/PycharmProjects/bot/welcome_text.txt", "r", encoding="utf-8") as file:
        text = file.read()
    return text


def open_random_images(path, count):
    files = os.listdir(path)
    image_files = [f for f in files if f.endswith('.jpg') or f.endswith('.png')]
    if len(image_files) < count:
        count = len(image_files)
    random_images = random.sample(image_files, count)  # выбираем случайные картинки из списка
    image_paths = [os.path.join(path, img) for img in random_images]  # полные пути к случайным картинкам
    images = []
    for img_path in image_paths:
        with open(img_path, 'rb') as f:
            images.append(f.read())
    return images


def open_random_images(callback_query):
    path = '/Users/anatoliykuznecov/PycharmProjects/bot/img/'
    files = os.listdir(path)
    count_images = 5
    image_files = [f for f in files if f.endswith('.jpg') or f.endswith('.png')]
    if image_files:
        query = 'SELECT image_path FROM sent_images WHERE chat_id =? or user_id =?'
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        data_base.cursor.execute(query, (chat_id, user_id,))
        sent_images = data_base.cursor.fetchall()
        sent_image_paths = [img[0] for img in sent_images]

        image_files_path = [path + i for i in image_files]
        available_images = list(set(image_files_path) - set(sent_image_paths))
        num_available_images = len(available_images)
        if num_available_images > 0:
            count_images = min(count_images, num_available_images)
            random_images = random.sample(available_images, count_images)
            image_bytes_list = []
            for random_image in random_images:
                image_path = os.path.join(path, random_image)
                with open(image_path, 'rb') as f:
                    # Добавляем информацию об отправленной картинке в базу данных
                    data_base.cursor.execute("INSERT INTO sent_images (user_id, chat_id, image_path) VALUES (?, ?, ?)",
                                             (user_id, chat_id, image_path))
                    data_base.conn.commit()
                    image_bytes_list.append(f.read())
            return image_bytes_list
    return None




    """if image_files:
        # Формируем запрос к базе данных для получения списка отправленных картинок текущего пользователя
        query = "SELECT image_path FROM sent_images WHERE user_id = ?"
        user_id = callback_query.from_user.id
        data_base.cursor.execute(query, (user_id,))
        sent_images = data_base.cursor.fetchall()
        sent_image_paths = [img[0] for img in sent_images]

        # Формируем запрос к базе данных для получения списка отправленных картинок всеми пользователями чата
        query = "SELECT image_path FROM sent_images WHERE chat_id = ?"
        chat_id = callback_query.message.chat.id
        data_base.cursor.execute(query, (chat_id,))
        all_sent_images = data_base.cursor.fetchall()
        all_sent_image_paths = [img[0] for img in all_sent_images]

        # Выбираем случайные картинки из списка, не входящие в список отправленных картинок
        available_images = list(set(image_files) - set(sent_image_paths) - set(all_sent_image_paths))
        num_available_images = len(available_images)
        if num_available_images > 0:
            count_images = min(count_images, num_available_images)
            random_images = random.sample(available_images, count_images)
            image_bytes_list = []
            for random_image in random_images:
                image_path = os.path.join(path, random_image)
                with open(image_path, 'rb') as f:
                    # Добавляем информацию об отправленной картинке в базу данных
                    data_base.cursor.execute("INSERT INTO sent_images (user_id, chat_id, image_path) VALUES (?, ?, ?)",
                                   (user_id, chat_id, image_path))
                    data_base.conn.commit()
                    image_bytes_list.append(f.read())
            return image_bytes_list
    return None"""







