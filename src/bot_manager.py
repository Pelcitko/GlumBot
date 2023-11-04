from openai import OpenAIError
from character import Character  # Import Character třídy
from colorama import Fore, Style
from fbchat import Client, ThreadType, Thread
from fbchat.models import Message
from config import FB_COOKIES, NO_ONE, ROOT_DIR
import json
import logging
import os
from conversation import Conversation

from tools import json_load

logging.basicConfig(level=logging.INFO, format=f"{Fore.BLUE}%(message)s{Style.RESET_ALL}")


class ClientManager(Client):
    def __init__(self, email, password):
        super().__init__(email, password, max_tries=2, session_cookies=self.load_session())
        self.available_characters: dict[str, Character] = {}  # postavy: {name: Character}
        self.conversations: dict[str, Conversation] = {}      # threads: {thread_id: Conversation}

    def set_conversation(self, thread_id: str, auto_response: bool = False) -> Thread:
        """
        Sets up a conversation with a thread by fetching its information and participants.
        If the thread is not already in the bot's threads, it will be added.
        If auto_response is True, the bot will automatically respond to messages in the thread.
        
        Args:
        - thread_id (str): The ID of the thread to set up a conversation with.
        - auto_response (bool): Whether or not to automatically respond to messages in the thread.
        
        Returns:
        - Thread: The thread object representing the conversation.
        """
        if thread_id not in self.threads:
            thread = self.fetchThreadInfo(thread_id)[thread_id]
            self.threads[thread_id] = thread
            logging.info(f"Added thread: {thread}")

            self.threads_participants[thread_id] = self.fetch_participants(thread)
            self.threads_auto_response[thread_id] = auto_response
        return self.threads[thread_id]

    def fetch_participants(self, thread: Thread) -> dict[str, dict[str, str|bool]]:
        """
        Fetches the list of participants in a given thread.
        
        :param thread: Thread object.
        :return: Dictionary of participants in the chat.
        """
        participants = {}
        if thread.type == ThreadType.USER:
            participants = {
                "name": thread.name,
                "nickname": thread.nickname,
                "is_friend": thread.is_friend,
            }

        elif thread.type == ThreadType.GROUP:
            user_ids = thread.participants
            for user_id in user_ids:
                user_info = self.fetchUserInfo(user_id)[user_id]
                participants[user_id] = {
                    "name": user_info.name,
                    "nickname": thread.nicknames.get(user_id, ""),
                    "is_friend": user_info.is_friend,
                }

        logging.info(f"Participants: {participants}")
        return participants

    def get_participant_name(self, participant_id):
        """
        Získá plné označení účastníka zadaného podle ID.

        :param participant_id: ID účastníka.
        :return: 'Přesdívka (Jméno Přijmení)'
        """
        return f"{self.participants[participant_id]['nickname']} ({self.participants[participant_id]['name']})"

    def onMessage(self, mid=None, author_id=None, message=None, message_object: Message=None, thread_id=None, thread_type=None, ts=None, metadata=None, msg={}):
        """
        Metoda je zavolána, když přijde nová zpráva.

        :param mid: ID zprávy.
        :param author_id: ID autora zprávy.
        :param message: Text zprávy.
        :param message_object: Objekt zprávy.
        :param thread_id: ID vlákna.
        :param thread_type: Typ vlákna.
        :param ts: Časové razítko.
        :param metadata: Metadata.
        :param msg: Slovník zprávy.
        """
        self.markAsDelivered(thread_id, message_object.uid)

        if thread_id not in self.conversations:
            conversation = Conversation(thread_id=thread_id)
            self.conversations[thread_id] = conversation
        else:
            conversation = self.conversations[thread_id]
        
        # Uložení vlastních zpráv do historie
        if author_id == self.uid:
            conversation.add_message("assistant", message_object.text)
            return
        
        conversation.add_message("user", message_object.text, author_id)
        
        # Zjištění charakteru pro dané vlákno na základě přezdívky
        nickname = conversation.get_participant_nickname(author_id)  # předpokládá, že existuje tato metoda
        character = self.available_characters.get(nickname, self.available_characters['NO_ONE'])
        conversation.set_character(character)

        self.markAsRead(thread_id)
        
        if conversation.auto_response or message_object.mentions:
            ai_response = self.handle_send(conversation)
            if ai_response:
                self.send_message(ai_response, thread_id, thread_type)


    def handle_send(self, conversation: Conversation) -> str:
        char: Character = conversation.character
        mess = [{"role": "system", "content": char.character_setting}] + char.messages

        try:
            response = char.ai.get_response(mess)
            return response
        except OpenAIError as e:
            print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}\n')

            if "max tokens" in str(e):
                char.messages = char.ai.prune_messages(char.messages, 0.5)
                print(f"{Fore.YELLOW}Právě jsem zapomněl půku své identity.{Style.RESET_ALL}")

            return self.handle_send(conversation)  # rekurzivní volání s ořezanými zprávami
        except Exception as e:
            print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}\n')
            return None

    def send_message(self, message, thread_id, thread_type=ThreadType.USER):
        """
        Odešle zprávu do zadaného vlákna.
        
        :param message: Text zprávy k odeslání.
        :param thread_id: ID vlákna, do kterého se má zpráva odeslat.
        :param thread_type: Typ vlákna (uživatel, skupina, stránka). Defaultní je uživatel.
        """
        self.send(
            Message(text=message),
            thread_id=thread_id,
            thread_type=thread_type
        )

        
    def initialize(self) -> None:
        self.load_characters()
        logging.info(f"Loaded {len(self.available_characters)} characters.")

    def run(self) -> None:
        super().listen()
        logging.info("Bot is now running.")

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
            print(session_cookies)
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