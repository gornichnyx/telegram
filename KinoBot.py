import telebot
from telebot import types
import config
import tmdbsimple as tmdb
import requests
tmdb.REQUESTS_SESSION = requests.Session()
tmdb.API_KEY = '89b7322e6a500625af7a481b32251e9d'

bot = telebot.TeleBot(config.TOKEN)

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
        movie = tmdb.Movies(769694)
        response = movie.info()
        ttt = '[{}](https://www.themoviedb.org/movie/769694-russian-gay-dude)'.format(movie.title)
        if message.text == "Я примерно знаю, что хочу посмотреть":

            bot.send_message(message.chat.id, ttt, parse_mode='MarkdownV2')
        elif message.text == "Рандомный фильм":

            bot.send_message(message.chat.id, ttt, parse_mode='MarkdownV2')


# run
bot.polling(none_stop=True)
