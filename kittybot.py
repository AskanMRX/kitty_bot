import logging
import os
import requests

from dotenv import load_dotenv
from telebot import TeleBot, types
from googletrans import Translator


load_dotenv()

secret_token = os.getenv('TOKEN')
bot = TeleBot(token=secret_token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

CAT_API_URL = 'https://api.thecatapi.com/v1/images/search'
CAT_FACT_API_URL = 'https://catfact.ninja/fact'
DOG_API_URL = 'https://api.thedogapi.com/v1/images/search'

def get_new_image():
    try:
        response = requests.get(CAT_API_URL)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        response = requests.get(DOG_API_URL)
    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def get_funny_cat():
    try:
        response = requests.get(CAT_FACT_API_URL)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        response = requests.get(CAT_API_URL)
    response = response.json()
    funny_cat_image = get_new_image()
    funny_cat_fact = response['fact']
    return funny_cat_image, funny_cat_fact


def get_new_funny_cat():
    funny_cat_image = get_new_image()
    try:
        response = requests.get(CAT_FACT_API_URL)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        funny_cat_fact = 'Котик слишком ленив, чтобы придумать факт'
    else:
        response = response.json()
        funny_cat_fact = response['fact']
    return funny_cat_image, funny_cat_fact


def get_dog():
    try:
        response = requests.get(DOG_API_URL)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        response = requests.get(CAT_API_URL)
    response = response.json()
    random_dog = response[0].get('url')
    return random_dog


def translate_text(text):
    translator = Translator()
    translated_text = translator.translate(text, dest='ru').text
    return translated_text


@bot.message_handler(commands=['start'])
def wake_up(message):
    chat_id = message.chat.id
    name = message.from_user.first_name
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_new_funny_cat = types.KeyboardButton('Новые смешные котики')
    button_dog = types.KeyboardButton('Я устал от котиков')
    button_axolotl = types.KeyboardButton('Хочу экзотики')
    keyboard.add(button_new_funny_cat)
    keyboard.add(button_dog)
    keyboard.add(button_axolotl)

    bot.send_message(
        chat_id=chat_id,
        text=f'Привет, {name}. Посмотри, какого котика я тебе нашел',
        reply_markup=keyboard,
    )

    bot.send_photo(chat_id, get_new_image())


@bot.message_handler(content_types=['text'])
def say_hi(message):
    chat = message.chat
    chat_id = chat.id
    if message.text.lower() == 'новые смешные котики':
        funny_cat_image, funny_cat_fact = get_new_funny_cat()
        translated_fact = translate_text(funny_cat_fact)
        bot.send_photo(chat_id, funny_cat_image)
        bot.send_message(chat_id, translated_fact)
    elif message.text.lower() == 'я устал от котиков':
        bot.send_photo(chat_id, get_dog())
    else:
        bot.send_message(chat_id=chat_id, text='Привет, я KittyBot!')



def main():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()