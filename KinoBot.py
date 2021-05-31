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
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("жанр")
            btn2 = types.KeyboardButton("рейтинг")
            btn3 = types.KeyboardButton('актер')
            btn4 = types.KeyboardButton('название')
            btn5 = types.KeyboardButton('назад')
            markup.add(btn4, btn1, btn2, btn3, btn5)
            bot.send_message(message.chat.id, 'Выберите критерии поиска.', parse_mode='html', reply_markup=markup)

        if message.text == 'название':
            sent_message = bot.send_message(message.chat.id, 'Введите название фильма')
            bot.register_next_step_handler(sent_message, search_by_film_name)

        if message.text == 'жанр':
            markup = types.ForceReply(selective=False)
            sent_message = bot.send_message(message.chat.id, "Введите через запятую интересный(е) вам жанр(ы): боевик, вестерн, военный, детектив, документальный, драма, история, комедия, криминал, мелодрама, музыка, мультфильм, приключения, семейный, телевезионный фильм, триллер, ужасы, фантастика, фентези.", parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(sent_message, genres)

        if message.text == "Рандомный фильм":
            movie = tmdb.Movies(769694)
            response = movie.info()
            bot.send_message(message.chat.id, '[{}](https://www.themoviedb.org/movie/769694-russian-gay-dude)'.format(movie.title), parse_mode='MarkdownV2')

        if message.text == "актер":
            sent_message = bot.send_message(message.chat.id, "Введите имя и фамилию интересущего вас актера")
            bot.register_next_step_handler(sent_message, search_by_actor)


def genres(message):
    try:
        genres_list = message.text.split(', ')
        for genre in genres_list:
            bot.reply_to(message, genre)
    except Exception as e:
        bot.reply_to(message, 'Неправильный ввод, попробуйте снова, через запятую.')

def search_by_actor(message):
    url = 'https://api.themoviedb.org/3/movie/157336?api_key={}'.format(config.TOKENTMDB)
    response = requests.get(url)
    print(response.json())

def search_by_film_name(message):
    try:
        url = 'https://api.themoviedb.org/3/search/movie?api_key={}&query={})'.format(config.TOKENTMDB, message.text)
        response = requests.get(url)
        result = response.json()
        i = 1
        for s in result['results'][:5]:
            url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(s['id'], config.TOKENTMDB)
            response = requests.get(url)
            result = response.json()
            # print(result)
            genres = ''
            for genre in result['genres']:
                genres += genre['name'] + ", "
            if result['budget'] == 0:
                result_printed = '{}. {},  {}минут,  {},  {}\nБюджет-неизвестен\n{}'.format(i, result['title'], result['runtime'], result['vote_average'], genres[:-2], result['overview'])
            else:
                result_printed = '{}. {},  {}минут,  {},  {}\nБюджет: {}$\n{}'.format(i, result['title'], result['runtime'], result['vote_average'], genres[:-2], result['budget'], result['overview'])
            bot.send_message(message.chat.id, result_printed)
            bot.send_photo(message.chat.id, urlopen('https://www.themoviedb.org/t/p/w500{}'.format(s['poster_path'])).read())
            i += 1
        bot.send_message(message.chat.id, 'Введите номер заинтересовавшего вас фильма')
    except Exception as e:
        pass







# run
bot.polling(none_stop=True)
