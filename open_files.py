import random


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
