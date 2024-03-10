import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()


def weather(city):
    try:
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv("API_KEY")}&units=metric')
        data = json.loads(response.content)
        result = f'''
City: {data['name']}
Temperature: {round(data['main']['temp'])}°C 
Feels Like: {round(data['main']['feels_like'])}°C 
Humidity: {data['main']['humidity']} %
Description: {data['weather'][0]['description']}
        '''
        return response.status_code, result, data['weather'][0]['icon']
    except KeyError:
        return None
