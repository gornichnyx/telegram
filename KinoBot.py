import telebot
from telebot import types
import config
import tmdbsimple as tmdb
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
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
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



@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == '1':
        url = 'https://api.themoviedb.org/3/person/{}/movie_credits?api_key={}'.format(person_id, config.TOKENTMDB)
        response = requests.get(url)
        actor = response.json()
        answer = ''
        global films
        films = {}
        i = 0
        for cast in actor['cast']:
            films[i] = cast
            try:
                answer += '{}. {}, {}({})\n'.format(str(i+1), cast['title'], cast['vote_average'], cast['release_date'][:4])
                i += 1
            except Exception as e:
                pass

        bot.send_message(call.message.chat.id, answer[:4000])
        sent_message = bot.send_message(call.message.chat.id, 'введите номер заинтереовавшего вас фильма')
        bot.register_next_step_handler(sent_message, more_movie_info)



def genres(message):
    try:
        genres_list = message.text.split(', ')
        for genre in genres_list:
            bot.reply_to(message, genre)
    except Exception as e:
        bot.reply_to(message, 'Неправильный ввод, попробуйте снова, через запятую.')

def search_by_actor(message):
    try:
        url = 'https://api.themoviedb.org/3/search/person?api_key={}&query={}'.format(config.TOKENTMDB, message.text)
        response = requests.get(url)
        actor = response.json()
        global person_id
        person_id = actor['results'][0]['id']
        famous_for = ''
        for film in actor['results'][0]['known_for']:
            famous_for += film['title'] + '\n'
        url = 'https://api.themoviedb.org/3/person/{}?api_key={}'.format(person_id, config.TOKENTMDB)
        response = requests.get(url)
        actor_info = response.json()
        url = 'https://api.themoviedb.org/3/person/{}/images?api_key={}'.format(person_id, config.TOKENTMDB)
        response = requests.get(url)
        actor_photo = response.json()
        result_printed = '{}, ({}-{}), {}\nFamous for: {}'\
            .format(actor['results'][0]['name'], actor_info['birthday'][:4], actor_info['deathday'][:4], actor_info['place_of_birth'], famous_for[:-1])
        bot.send_message(message.chat.id, result_printed)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="все фильмы", callback_data=1)
        btn2 = types.InlineKeyboardButton(text="добавить актера", callback_data=2)
        markup.add(btn1, btn2)
        bot.send_photo(message.chat.id, urlopen('https://www.themoviedb.org/t/p/w500{}'.format(actor_photo['profiles'][0]['file_path'])).read(), reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, 'Неверный ввод.')
        print(e)

def search_by_film_name(message):
    try:
        url = 'https://api.themoviedb.org/3/search/movie?api_key={}&query={})'.format(config.TOKENTMDB, message.text)
        response = requests.get(url)
        result = response.json()
        i = 0
        global films
        films = {}
        for s in result['results'][i:i+5]:
            url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(s['id'], config.TOKENTMDB)
            response = requests.get(url)
            result = response.json()
            genres = ''
            for genre in result['genres']:
                genres += genre['name'] + ", "
            result_printed = '{}. {}({}),  {}минут,  {},  {}\n{}'.format(i+1, result['title'], result['release_date'][:4], result['runtime'], result['vote_average'], genres[:-2], result['overview'])
            films[i] = result
            bot.send_message(message.chat.id, result_printed)
            bot.send_photo(message.chat.id, urlopen('https://www.themoviedb.org/t/p/w500{}'.format(s['poster_path'])).read())
            i += 1
        sent_message = bot.send_message(message.chat.id, 'Введите номер заинтересовавшего вас фильма')
        bot.register_next_step_handler(sent_message, more_movie_info)
    except Exception as e:
        pass


def more_movie_info(message):
    try:
        movie_info = films[-1+int(message.text)]
        url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_info['id'], config.TOKENTMDB)
        response = requests.get(url)
        movie_info = response.json()
        response = requests.get('https://api.themoviedb.org/3/movie/{}/credits?api_key={}'.format(movie_info['id'], config.TOKENTMDB))
        credits_info = response.json()
        cred = 'Credits: '
        for cast in credits_info['cast'][:5]:
            cred += cast['name'] + ' - ' + cast['character'] + '\n'
        genres = ''
        for genre in movie_info['genres']:
            genres += genre['name'] + ", "
        production = ''
        for company in movie_info['production_companies']:
            production += company['name'] + ', '
        if movie_info['budget'] == 0:
            budget = 'Budget is unknown'
        else:
            budget = 'Budget: {}$'.format(movie_info['budget'])
        if movie_info['revenue'] == 0:
            revenue = 'Revenue is unknown'
        else:
            revenue = 'Revenue: {}$'.format(movie_info['revenue'])
        direction = ''
        for name in credits_info['crew']:
            if name['job'] == 'Director':
                direction += name['name'] + ", "
        result_printed = '{}, {} minutes, {}, {}.\n' \
                         '{}.\n' \
                         '{}.\n' \
                         'Production: {}.\n'\
                         'Directed by {}.\n'\
                         '{}.'\
            .format(movie_info['title'], movie_info['runtime'], movie_info['vote_average'], genres[:-2], budget, revenue, production[:-2], direction[:-2], cred[:-2])
        bot.send_message(message.chat.id, result_printed)
        if movie_info['backdrop_path'] != None:
            bot.send_photo(message.chat.id, urlopen('https://www.themoviedb.org/t/p/w500{}'.format(movie_info['backdrop_path'])).read())
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'неправильный ввод')








# run
bot.polling(none_stop=True)
