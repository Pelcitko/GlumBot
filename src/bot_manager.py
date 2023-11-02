from messenger_client import MessengerClient  # Import MessengerClient třídy
from character import Character  # Import Character třídy
from colorama import Fore, Style
from config import FB_COOKIES, NO_ONE, ROOT_DIR
import json
import logging
import os

from tools import json_load

logging.basicConfig(level=logging.INFO, format=f"{Fore.LIGHTBLUE_EX}%(message)s{Style.RESET_ALL}")

class BotManager(MessengerClient):
    def __init__(self, email: str, password: str):
        super().__init__(email, password, session_cookies=self.load_session())
        self.available_characters: list[Character] = []
        
    def initialize(self) -> None:
        self.load_characters()
        logging.info(f"Loaded {len(self.available_characters)} characters.")

    def run(self) -> None:
        super().listen()
        logging.info("BotManager is now running.")

    def shutdown(self) -> None:
        logging.info("Shutting down the bot.")
        self.save_session()
        os._exit(0) 

    def save_session(self, coookie_file=FB_COOKIES) -> None:
        session_cookies = self.getSession()
        with open(coookie_file, "w") as file:
            json.dump(session_cookies, file)
        logging.info("Saved session cookies.")

    def load_session(self, cookie_file=FB_COOKIES) -> dict | None:
        print("Loading session cookies file.", cookie_file)
        if os.path.exists(cookie_file):
            with open(cookie_file, "r") as file:
                session_cookies = json.load(file)
            logging.info("Loaded session cookies.")
            return session_cookies
        else:
            logging.info("Session cookies not found.")
            return None
        
    def load_characters(self):
        characters_path = os.path.join(ROOT_DIR, 'characters')  # Cesta ke složce s postavami
        character_files = [f for f in os.listdir(characters_path) if f.endswith('.json')]  # Filtr pro JSON soubory

        for character_file in character_files:
            full_path = os.path.join(characters_path, character_file)
            try:
                character = self.load_character(full_path)  # Použije tvou funkci na načtení postavy
                self.available_characters.append(character)
                logging.info(f"Loaded character: {character.name}")
            except Exception as e:
                logging.error(f"Failed to load character from {character_file}: {e}")

        logging.info(f"Total characters loaded: {len(self.available_characters)}")

    @staticmethod
    def load_character(config_file: str):
        config_file = os.path.join(ROOT_DIR, 'characters', config_file)
        character_dict = json_load(config_file)

        if not character_dict or not character_dict.get('name') or not character_dict.get('character_setting'):
            print(f"{Fore.YELLOW}Invalid or missing configuration file {config_file}. Defaulting to character 'No One'.{Style.RESET_ALL}")
            character_dict = NO_ONE

        return Character(
            name=character_dict['name'],
            character_setting=character_dict['character_setting'],
            temperature=character_dict.get('temperature'),
            max_tokens=character_dict.get('max_tokens'),
            logit_bias=character_dict.get('logit_bias'),
            presence_penalty=character_dict.get('presence_penalty')
        )