# config.py
import configparser
import os

# Získání kořenového adresáře projektu
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = configparser.ConfigParser()
config.read(os.path.join(ROOT_DIR, 'config.ini'))

FB_EMAIL = config['Facebook']['email']
FB_PASSWORD = config['Facebook']['password']

OPENAI_API_KEY = config['OpenAI']['api_key']

DEAFAULT_MODEL = "gpt-3.5-turbo"