import signal
import sys
from openai import OpenAIError
from character import Character  # Import Character třídy
from colorama import Fore, Style, init
from fbchat import Client, ThreadType
from fbchat.models import Message, Thread
from config import FB_COOKIES, NO_ONE, ROOT_DIR
import json
import logging
import os
from conversation import Conversation
from log_formatter import CustomFormatter
from tools import json_load

init(autoreset=True)  # Inicializace colorama

# Nastavení loggeru
logger = logging.getLogger(__name__)
logger.propagate = False
logger.handlers.clear() 
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class ClientManager(Client):

    def __init__(self, email, password):
        logger.info("Initializing the bot.")
        super().__init__(email, password, max_tries=2, session_cookies=self.load_session())
        self.available_characters: dict[str, Character] = {}  # postavy: {name: Character}
        self.conversations: dict[str, Conversation] = {}      # threads: {thread_id: Conversation}

    def set_conversation(self, thread_id: str) -> Conversation:
        if thread_id in self.conversations:
            return self.conversations[thread_id]
        else:
            thread = self.fetchThreadInfo(thread_id)[thread_id]
            if thread.type == ThreadType.USER:
                auto_response = True
            else:
                auto_response = False
            participant = self.fetch_participants(thread)
            conversation = Conversation(thread, participant, auto_response)
            bot_name = conversation.get_participant_nickname(self.uid)
            character = self.available_characters.get(bot_name, self.available_characters['NO_ONE'])
            conversation.set_character(character)
            self.conversations[thread_id] = conversation
            logger.info(f"Added thread: {conversation}")
            return conversation
        
    def fetch_character(self, thread: Thread) -> Character:
        bot_name = self.fetch_bot_name(thread)
        logger.debug(f"Bot name: {bot_name}")
        character = self.available_characters.get(bot_name, self.available_characters['NO_ONE'])
        logger.debug(f"Character: {character}")
        return character

    def onMessage(self, mid=None, author_id=None, message=None, message_object: Message=None, thread_id=None, thread_type=None, ts=None, metadata=None, msg={}):
        self.markAsDelivered(thread_id, message_object.uid)

        conversation = self.set_conversation(thread_id)
        
        # Uložení vlastních zpráv do historie
        print(f"{Fore.YELLOW}author_id: {author_id}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}self.uid: {self.uid}{Style.RESET_ALL}")
        if author_id == self.uid:
            conversation.add_message("assistant", message_object.text)
            return
        
        # Zjištění charakteru pro dané vlákno na základě přezdívky
        nickname = conversation.get_participant_nickname(author_id)
        print(f"{Fore.YELLOW}Přezdívka: {nickname}{Style.RESET_ALL}")
        bot_name = conversation.character.name
        logger.debug(f"Bot name: {bot_name}")
        character = self.available_characters.get(bot_name, self.available_characters['NO_ONE'])
        logger.debug(f"Character: {character}")
        conversation.set_character(character)

        
        conversation.add_message("user", message_object.text, author_id)

        self.markAsRead(thread_id)
        
        if conversation.auto_response or message_object.mentions:
            ai_response = self.handle_send(conversation)
            if ai_response:
                self.send_message(ai_response, thread_id, thread_type)


    def handle_send(self, conversation: Conversation) -> str:
        logger.info(f"Handling send for {conversation}")
        character = conversation.character
        mess = [{"role": "system", "content": character.character_setting}] + conversation.memory.history

        try:
            response = character.ai.get_response(mess)
            return response
        except OpenAIError as e:
            print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}\n')

            if "max tokens" in str(e):
                conversation.memory.manage_history(0.5)
                print(f"{Fore.YELLOW}Právě jsem zapomněl půku své identity.{Style.RESET_ALL}")

            return self.handle_send(conversation)  # rekurzivní volání s ořezanými zprávami
        except Exception as e:
            print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}\n')
            return None

    def send_message(self, message, thread_id, thread_type=ThreadType.USER):
        self.send(
            Message(text=message),
            thread_id=thread_id,
            thread_type=thread_type
        )
 
    def initialize(self) -> None:
        self.load_characters()
        logger.info(f"Loaded {len(self.available_characters)} characters.")

    def run(self) -> None:
        # handlery pro signály ukončení
        signal.signal(signal.SIGINT, lambda signum, frame: self.shutdown())
        signal.signal(signal.SIGTERM, lambda signum, frame: self.shutdown())
        logger.info("For graceful shutdown press Ctrl+C or send SIGTERM.")
        super().listen()
        logger.info("Bot is listening for new messages.")

    def shutdown(self) -> None:
        self.save_session()
        for _, conversation in self.conversations.items():
            conversation.memory.save()
        logger.info("Shutting down the bot.")
        sys.exit(0)  

    def save_session(self, coookie_file=FB_COOKIES) -> None:
        session_cookies = self.getSession()
        with open(coookie_file, "w") as file:
            json.dump(session_cookies, file)
        logger.info("Saved session cookies.")

    def load_session(self, cookie_file=FB_COOKIES) -> dict | None:
        logger.info(f"Loading session cookies from file: {cookie_file}")
        if os.path.exists(cookie_file):
            with open(cookie_file, "r") as file:
                session_cookies = json.load(file)
            logger.info("Loaded session cookies.")
            return session_cookies
        else:
            logger.info("Session cookies not found.")
            return None
        
    def load_characters(self):
        characters_path = os.path.join(ROOT_DIR, 'characters')  # Cesta ke složce s postavami
        character_files = [f for f in os.listdir(characters_path) if f.endswith('.json')]  # Filtr pro JSON soubory

        for character_file in character_files:
            full_path = os.path.join(characters_path, character_file)
            try:
                character = self.load_character(full_path)  # Použije tvou funkci na načtení postavy
                self.available_characters[character.name] = character
                logger.info(f"Loaded character: {character.name}")
                logger.debug(character.__dict__)
            except Exception as e:
                logger.error(f"Failed to load character from {character_file}: {e}")
        self.available_characters['NO_ONE'] = Character(**NO_ONE)

        logger.info(f"Total characters loaded: {len(self.available_characters)}")

    @staticmethod
    def load_character(config_file: str) -> Character:
        config_file = os.path.join(ROOT_DIR, 'characters', config_file)
        character_dict = json_load(config_file)

        mandatory_keys = ['name', 'character_setting']
        if not all(key in character_dict for key in mandatory_keys):
            logger.error(f"Invalid or missing configuration file {config_file}.")
            logger.error(f"Please make sure that the file contains the following keys: {mandatory_keys}.")

        return Character(
            name=character_dict['name'],
            character_setting=character_dict['character_setting'],
            temperature=character_dict.get('temperature'),
            max_tokens=character_dict.get('max_tokens'),
            logit_bias=character_dict.get('logit_bias'),
            presence_penalty=character_dict.get('presence_penalty')
        )
    
    def fetch_bot_name(self, thread: Thread) -> str:
        print(f"{Fore.YELLOW}Fetching bot name...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Thread: {thread}{Style.RESET_ALL}")
        if thread.type == ThreadType.USER:
            bot_user = thread.own_nickname
        elif thread.type == ThreadType.GROUP:
            bot_user = self.fetchUserInfo(self.uid)[self.uid]
        return bot_user.nickname or bot_user.name
    
    def fetch_participants(self, thread: Thread) -> dict[str, dict[str, str|bool]]:
        logging.info("Fetching participants...")
        print(f"{Fore.YELLOW}Thread: {thread}{Style.RESET_ALL}")
        
        participants = {}
        if thread.type == ThreadType.USER:
            participants[thread.uid] = {
                "name": thread.name or "",
                "nickname": thread.nickname or "",
                "is_friend": thread.is_friend,
            }
            participants[self.uid] = {
                "name": "bot",
                "nickname": thread.own_nickname or "",
                "is_friend": True,
            }

        elif thread.type == ThreadType.GROUP:
            user_ids = thread.participants
            for user_id in user_ids:
                user_info = self.fetchUserInfo(user_id)[user_id]
                participants[user_id] = {
                    "name": user_info.name or "",
                    "nickname": thread.nicknames.get(user_id, ""),
                    "is_friend": user_info.is_friend,
                }
        else:
            logging.error(f"Unknown thread type: {thread.type}")

        logging.info(f"Participants: {participants}")
        return participants
