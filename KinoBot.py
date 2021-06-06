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
    btn1 = types.KeyboardButton("Search for the movie")
    markup.add(btn1)
    # greeting message
    bot.send_message(message.chat.id, 'Hello, {}, I am a bot for films searching!'.format(message.from_user.first_name), parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
# reaction on some words in the chat
def text(message):
    if message.chat.type == 'private':
        if message.text == "Search for the movie" or 'back':
            # keyboard
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton("genre")
            btn2 = types.KeyboardButton("top films")
            btn3 = types.KeyboardButton('actor')
            btn4 = types.KeyboardButton('film name')
            markup.add(btn4, btn1, btn2, btn3)
            bot.send_message(message.chat.id, 'Choose the base of the search', parse_mode='html', reply_markup=markup)

        if message.text == 'film name':
            try:
                sent_message = bot.send_message(message.chat.id, 'enter movies title')
                bot.register_next_step_handler(sent_message, search_by_film_name)
            except Exception as e:
                bot.send_message(message.chat.id, 'wrong input')

        if message.text == 'genre':
            markup = types.ForceReply(selective=False)
            sent_message = bot.send_message(message.chat.id, "Choose from those genres: action, adventure, animation, comedy, crime, documentary, drama, family, fantasy, history, horror, music, mystery, romance, science fiction, TV movie, thriller, war, western.", parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(sent_message, genres)

        if message.text == "actor":
            sent_message = bot.send_message(message.chat.id, "Enter actors name and surname")
            bot.register_next_step_handler(sent_message, search_by_actor)

        # top rated movies output
        if message.text == "top films":
            url = 'https://api.themoviedb.org/3/movie/top_rated?api_key={}'.format(config.TOKENTMDB)
            response = requests.get(url)
            top = response.json()
            i = 0
            # films for the more_movie_info function
            global films
            films = {}
            answer = ''
            for result in top['results']:
                films[i] = {'id': result['id']}
                answer += '{}. {}, {}({})\n'.format(str(i + 1), result['title'], result['vote_average'], result['release_date'][:4])
                i += 1
            bot.send_message(message.chat.id, answer[:4000])
            sent_message = bot.send_message(message.chat.id, 'enter movies number')
            bot.register_next_step_handler(sent_message, more_movie_info)


@bot.callback_query_handler(func=lambda call: True)
# for inline keyboard callback
def query_handler(call):
    # for more_movie_info function
    global films
    # movie search by actor(s)
    if call.data == '1':
        try:
            actors = ','.join(persons.keys())
            print(actors)
            url = 'https://api.themoviedb.org/3/discover/movie?api_key={}&with_people={}'.format(config.TOKENTMDB, actors)
            print(url)
            response = requests.get(url)
            actors = response.json()
            films = {}
            answer = ''
            i = 0
            for result in actors['results']:
                films[i] = {'id': result['id']}
                answer += '{}. {}, {}({})\n'.format(str(i + 1), result['title'], result['vote_average'], result['release_date'][:4])
                i += 1
            bot.send_message(call.message.chat.id, answer[:4000])
            sent_message = bot.send_message(call.message.chat.id, 'Enrter movies number')
            bot.register_next_step_handler(sent_message, more_movie_info)
        except Exception as e:
            bot.send_message(call.message.chat. id, 'Wrong input or those actors didn"t work together')
    # add actor to search
    if call.data == '2':
        try:
            sent_message = bot.send_message(call.message.chat.id, 'enter the name and surname of the actor')
            bot.register_next_step_handler(sent_message, search_by_actor)
            print(persons)
        except Exception as e:
            bot.send_message(call.mesage.chat.id, 'wrong actors name or surname')


    # similar movies
    if call.data == '3':
        url = 'https://api.themoviedb.org/3/movie/{}/similar?api_key={}'.format(movie_id, config.TOKENTMDB)
        response = requests.get(url)
        movie_info = response.json()
        films = {}
        answer = ''
        i = 0
        for result in movie_info['results']:
            answer += '{}. {}, {}({})\n'.format(i + 1, result['title'], result['vote_average'],
                                                result['release_date'][:4])
            films[i] = {'id': result['id']}
            i += 1
        bot.send_message(call.message.chat.id, answer)
        sent_message = bot.send_message(call.message.chat.id, 'enter the number of the movie you are interested in')
        bot.register_next_step_handler(sent_message, more_movie_info)

    # movie recomendations
    if call.data == '4':
        url = 'https://api.themoviedb.org/3/movie/{}/recommendations?api_key={}'.format(movie_id, config.TOKENTMDB)
        response = requests.get(url)
        movie_info = response.json()
        films = {}
        answer = ''
        i = 0
        for result in movie_info['results']:
            answer += '{}. {}, {}({})\n'.format(i + 1, result['title'], result['vote_average'],
                                                result['release_date'][:4])
            films[i] = {'id': result['id']}
            i += 1
        bot.send_message(call.message.chat.id, answer)
        sent_message = bot.send_message(call.message.chat.id, 'enter the number of the movie you are interested in')
        bot.register_next_step_handler(sent_message, more_movie_info)


# search based on genres
def genres(message):
    try:
        lst = message.text.split(', ')
        lst_genres = []
        for item in lst:
            lst_genres.append(item.lower())
        # getting all genres info
        url = 'https://api.themoviedb.org/3/genre/movie/list?api_key={}'.format(config.TOKENTMDB)
        response = requests.get(url)
        genres_lib = response.json()
        ids = []
        for genre in genres_lib['genres']:
            if genre['name'].lower() in lst_genres:
                ids.append(str(genre['id']))
        idd = ','.join(ids)
        url = 'https://api.themoviedb.org/3/discover/movie?api_key={}&with_genres={}'.format(config.TOKENTMDB, idd)
        response = requests.get(url)
        genre = response.json()
        global films
        films = {}
        answer = ''
        i = 0
        for result in genre['results']:
            answer += '{}. {}, {}({})\n'.format(i+1, result['title'], result['vote_average'], result['release_date'][:4])
            films[i] = {'id': result['id']}
            i += 1
        bot.send_message(message.chat.id, answer)
        sent_message = bot.send_message(message.chat.id, 'enter the number of the movie you are interested in')
        bot.register_next_step_handler(sent_message, more_movie_info)


    except Exception as e:
        bot.reply_to(message, 'Wrong input')
        print(e)


# search for the actor info, can get films on inline keyboard
def search_by_actor(message):
    try:
        url = 'https://api.themoviedb.org/3/search/person?api_key={}&query={}'.format(config.TOKENTMDB, message.text)
        response = requests.get(url)
        actor = response.json()
        # to search with several actors
        global person_id
        global persons
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
        try:
            persons[str(person_id)] = actor['results'][0]['name']
        except Exception as e:
            persons = {}
            persons[str(person_id)] = actor['results'][0]['name']
        if actor_info['deathday'] == None:
            result_printed = '{}, ({}), {}\nFamous for: {}'\
                .format(actor['results'][0]['name'], actor_info['birthday'][:4], actor_info['place_of_birth'], famous_for[:-1])
        else:
            result_printed = '{}, ({}-{}), {}\nFamous for: {}'\
                .format(actor['results'][0]['name'], actor_info['birthday'][:4], actor_info['deathday'][:4], actor_info['place_of_birth'], famous_for[:-1])
        # if there are more then 1 actor
        if len(persons) != 1:
            chosen = ''
            for key in persons:
                chosen += persons[key] + ', '
            if actor_info['deathday'] == None:
                result_printed = '{}, ({}), {}\nFamous for: {}\nChosen actors({}).' \
                    .format(actor['results'][0]['name'], actor_info['birthday'][:4], actor_info['place_of_birth'], famous_for[:-1], chosen[:-2])
            else:
                result_printed = '{}, ({}-{}), {}\nFamous for: {}\nChosen actors({}).' \
                    .format(actor['results'][0]['name'], actor_info['birthday'][:4], actor_info['deathday'][:4], actor_info['place_of_birth'], famous_for[:-1], chosen[:-2])
        bot.send_message(message.chat.id, result_printed)
        # inline keyboard
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="все фильмы", callback_data=1)
        btn2 = types.InlineKeyboardButton(text="добавить актера", callback_data=2)
        markup.add(btn1, btn2)
        bot.send_photo(message.chat.id, urlopen('https://www.themoviedb.org/t/p/w500{}'.format(actor_photo['profiles'][0]['file_path'])).read(), reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, 'Wrong input.')
        print(e)


def search_by_film_name(message):
    try:
        url = 'https://api.themoviedb.org/3/search/movie?api_key={}&query={})'.format(config.TOKENTMDB, message.text)
        response = requests.get(url)
        result = response.json()
        i = 0
        # for the more_movie_info function
        global films
        films = {}
        # sends 2 messages with text and picture
        for s in result['results'][i:i+5]:
            url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(s['id'], config.TOKENTMDB)
            response = requests.get(url)
            result = response.json()
            genres = ''
            for genre in result['genres']:
                genres += genre['name'] + ", "
            result_printed = '{}. {}({}),  {}minutes,  {},  {}\n{}'.format(i+1, result['title'], result['release_date'][:4], result['runtime'], result['vote_average'], genres[:-2], result['overview'])
            films[i] = result
            bot.send_message(message.chat.id, result_printed)
            if s['poster_path'] != None:
                bot.send_photo(message.chat.id, urlopen('https://www.themoviedb.org/t/p/w500{}'.format(s['poster_path'])).read())
            i += 1
        sent_message = bot.send_message(message.chat.id, 'Enter movies number')
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
        global movie_id
        movie_id = movie_info['id']
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
            .format(movie_info['title'], movie_info['runtime'], movie_info['vote_average'], genres[:-2], budget, revenue, production[:-2], direction[:-2], cred[:-1])
        # inline keyboard to get similar and recomendated movies
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="similar movies", callback_data=3)
        btn2 = types.InlineKeyboardButton(text="recomendations", callback_data=4)
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, result_printed, reply_markup=markup)
        if movie_info['backdrop_path'] != None:
            bot.send_photo(message.chat.id, urlopen('https://www.themoviedb.org/t/p/w500{}'.format(movie_info['backdrop_path'])).read())
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'неправильный ввод')


# run
bot.polling(none_stop=True)
