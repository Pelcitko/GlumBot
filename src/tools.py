
import json
import logging
import os

from colorama import Fore, Style
from character import Character

from config import NO_ONE, ROOT_DIR


def json_load(file_name) -> dict:
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return json.load(file)
    
def json_write(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file)
