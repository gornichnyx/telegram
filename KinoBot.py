import telebot
from telebot import types
import config
import tmdbsimple as tmdb
import requests
import json
import requests
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


def search_by_film_name(message):
    response = search.movie(query=message.text)
    print(search.results)
    for s in search.results:
        bot.reply_to(message, s['title'])



def genres(message):
    try:
        genres_list = message.text.split(', ')
        for genre in genres_list:
            bot.reply_to(message, genre)
    except Exception as e:
        bot.reply_to(message, 'Неправильный ввод, попробуйте снова, через запятую.')




# run
bot.polling(none_stop=True)
