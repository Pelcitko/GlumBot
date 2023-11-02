# config.py
import configparser
import os

# Získání kořenového adresáře projektu
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = configparser.ConfigParser()
config.read(os.path.join(ROOT_DIR, 'config.ini'))

FB_EMAIL = config['Facebook']['email']
FB_PASSWORD = config['Facebook']['password']
FB_COOKIES = os.path.join(
    ROOT_DIR,
    config['Facebook'].get('cookies', 'session.json')
)

OPENAI_API_KEY = config['OpenAI']['api_key']
DEAFAULT_MODEL = config['OpenAI'].get('model', 'gpt-3.5-turbo')

# Vzorová postava
GLUM = {
    "name": "Glum",
    "character_setting": "Jsi Glum, postava z knihy Pán prstenů. Používej jeho repliky, aby tvé odpovědi byly co nejvíce v jeho stylu. Používej hodně slova 'my', 'Glum', 'můj a 'milášek'.",
    "temperature": 0.7,
    "max_tokens": 512,
    "logit_bias": {"11906": 2},
    "presence_penalty": 0.2
}
# Defaultní postava
NO_ONE = {
    "name": "No One",
    "character_setting": "Jsi charakter ze Hry o trůny, jsi Nikdo. Nikdo je ztělesněním emocionálního odloučení, je nemilosrdný a chladnokrevný. Vyhýbáš se osobním zájmenům a čehokoliv, co by odhalilo osobní identitu. Nikdo mluví stručně a neosobně.",
    "temperature": 0.1,
    "max_tokens": 512,
}