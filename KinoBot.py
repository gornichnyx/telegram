import telebot
from telebot import types
import config
import tmdbsimple as tmdb
import requests
import json
import requests
from urllib.request import urlopen
tmdb.REQUESTS_SESSION = requests.Session()
tmdb.API_KEY = config.TOKENTMDB
search = tmdb.Search()

bot = telebot.TeleBot(config.TOKENTELEBOT)

@bot.message_handler(commands=['start'])
def welcome(message):

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Я примерно знаю, что хочу посмотреть")
    btn2 = types.KeyboardButton("Рандомный фильм")
    markup.add(btn1, btn2)

    bot.send_message(message.chat.id, 'Здравствуйте, {}, я - бот, созданный для поиска фильмов!'.format(message.from_user.first_name), parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def text(message):
    if message.chat.type == 'private':
        if message.text == "Я примерно знаю, что хочу посмотреть":

            bot.send_message(message.chat.id, ttt, parse_mode='MarkdownV2')
        elif message.text == "Рандомный фильм":
            movie = tmdb.Movies(769694)
            response = movie.info()
            bot.send_message(message.chat.id, '[{}](https://www.themoviedb.org/movie/769694-russian-gay-dude)'.format(movie.title), parse_mode='MarkdownV2')

        if message.text == "актер":
            sent_message = bot.send_message((message.chat.id, "Введите имя и фамилию интересущего вас актера"))
            bot.register_next_step_handler(sent_message, search_by_actor)


def search_by_film_name(message):
    response = search.movie(query=message.text)
    try:
        for s in search.results:
            bot.send_message(message.chat.id, '[{}](https://www.themoviedb.org/movie/{}-{})'.format(s['title'], s['id'], '-'.join(s['title'].lower().split(' '))), parse_mode='MarkdownV2')
            print('-'.join(s['title'].lower().split(' ')))
    except Exception as e:
        bot.send_message(message.chat.id, '{}  https://www.themoviedb.org/movie/{}'.format(s['title'], s['id']))

def genres(message):
    try:
        genres_list = message.text.split(', ')
        for genre in genres_list:
            bot.reply_to(message, genre)
    except Exception as e:
        bot.reply_to(message, 'Неправильный ввод, попробуйте снова, через запятую.')

def search_by_actor(message):





# run
bot.polling(none_stop=True)
