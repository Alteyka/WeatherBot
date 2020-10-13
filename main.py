from flask import Flask
from flask import jsonify
from flask import request
import requests
import re
import os

port = int(os.environ.get("PORT", 5000))
app = Flask(__name__)
TOKEN = os.environ['TOKEN']
WEATHER_TOKEN = os.environ['WEATHER_TOKEN']


def parse_message(text):
    pattern = r'[\w+а-яА-Я ]+'
    city = re.search(pattern, text).group()
    return city


"""
                                        DOCUMENTATION
function get_weather_morning() get argument which in turn parse_message() get as input word..
Then gets a dictionary in response object.
If message contains an word which not in list cities in API, has return answer with explanatory text as string.
dtlist is a list of dictionaries which contains an weather information on every 3 hour.
current_date - the first date of the nearest hour. At this point script define a date of a day which will be show users.
current_day - the list generator which forms a list of hours of current day.
First "for loop" - going through the list of hours of the current day.
If he find a needed time in list he launch a second for loop which in turn find first item
 with correct time in general dtlist.
If dictionary contains time, performed searching for keys and return formatted method join() string.
"""


def get_weather_morning(city):
    weather_url = 'http://api.openweathermap.org/data/2.5/forecast' \
                  '?q={}&units=metric&appid={}&lang=ru'.format(city, WEATHER_TOKEN)
    response_dict = requests.get(weather_url).json()
    if 'message' in response_dict and response_dict['message'] == 'city not found':
        response_dict = {'answer': 'Введите корректное название города'}
        return response_dict['answer']
    dtlist = response_dict['list'][0:40]
    city_name = response_dict['city']['name']
    current_date = response_dict['list'][0]['dt_txt'].split()
    current_day = [day.get('dt_txt', '') for day in dtlist if current_date[0] in day['dt_txt']]
    for time in current_day:
        if '06:00:00' in time:
            for item in dtlist:
                if '06:00:00' in item['dt_txt']:
                    temperature = item['main']['temp']
                    weather = item['weather'][0]['description']
                    wind = item['wind']['speed']
                    result = city_name.capitalize() + ', '.join([
                        '\n'
                        'утром: ' + str(temperature) + ' градусов',
                        weather.capitalize(),
                        'ветер ' + str(wind) + 'м в с \n',
                    ])
                    return result
    return city_name.capitalize() + '\n'


def get_weather_afternoon(city):
    weather_url = 'http://api.openweathermap.org/data/2.5/forecast' \
                  '?q={}&units=metric&&appid={}&lang=ru'.format(city, WEATHER_TOKEN)
    response_dict = requests.get(weather_url).json()
    if 'message' in response_dict and response_dict['message'] == 'city not found':
        return ''
    dtlist = response_dict['list'][0:40]
    current_date = response_dict['list'][0]['dt_txt'].split()
    current_day = [day.get('dt_txt', '') for day in dtlist if current_date[0] in day['dt_txt']]
    for time in current_day:
        if '12:00:00' in time:
            for item in dtlist:
                if '12:00:00' in item['dt_txt']:
                    temperature = item['main']['temp']
                    weather = item['weather'][0]['description']
                    wind = item['wind']['speed']
                    result = ', '.join([
                        'днем: ' + str(temperature) + ' градусов',
                        weather.capitalize(),
                        'ветер ' + str(wind) + 'м в с \n',
                    ])
                    return result
    return ''


def get_weather_evening(city):
    weather_url = 'http://api.openweathermap.org/data/2.5/forecast' \
                  '?q={}&units=metric&&appid={}&lang=ru'.format(city, WEATHER_TOKEN)
    response_dict = requests.get(weather_url).json()
    if 'message' in response_dict and response_dict['message'] == 'city not found':
        return ''
    dtlist = response_dict['list'][0:40]
    current_date = response_dict['list'][0]['dt_txt'].split()
    current_day = [day.get('dt_txt', '') for day in dtlist if current_date[0] in day['dt_txt']]
    for time in current_day:
        if '21:00:00' in time:
            for item in dtlist:
                if '21:00:00' in item['dt_txt']:
                    temperature = item['main']['temp']
                    weather = item['weather'][0]['description']
                    wind = item['wind']['speed']
                    result = ', '.join([
                        'вечером: ' + str(temperature) + ' градусов',
                        weather.capitalize(),
                        'ветер ' + str(wind) + 'м в с',
                    ])
                    return result
    return ''


telegram_url = 'https://api.telegram.org/bot{}/'.format(TOKEN)


def send_message(chat_id, text='bla-bla-bla'):
    url = telegram_url + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    result = requests.post(url, json=answer)
    return result.json()


@app.route('/{}'.format(TOKEN), methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        result = request.get_json()
        chat_id = result['message']['chat']['id']
        message_text = result['message']['text']
        pattern = r'[\w+а-яА-Я ]+'
        if re.search(pattern, message_text):
            weather_morning = get_weather_morning(parse_message(message_text))
            weather_afternoon = get_weather_afternoon(parse_message(message_text))
            weather_evening = get_weather_evening(parse_message(message_text))
            weather = weather_morning + weather_afternoon + weather_evening
            send_message(chat_id, text=str(weather))
        return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)
