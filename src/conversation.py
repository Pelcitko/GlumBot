import logging
import re
from colorama import Fore, Style, init
from fbchat.models import Thread, ThreadType
from character import Character
from openai import OpenAIError
from log_formatter import CustomFormatter

from memory_manager import MemoryManager

init(autoreset=True) 
logging.basicConfig(level=logging.INFO, format=f"{Fore.LIGHTBLUE_EX}%(message)s{Style.RESET_ALL}")

class Conversation:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    def __init__(self, thread: Thread, participants: dict, auto_response: bool = False):
        print("Starting initialization conversation...")
        self.thread: Thread = thread
        self.thread_id: str = thread.uid
        self.participants: dict[str, dict] = participants
        self.character: Character = None 
        self.memory: MemoryManager = MemoryManager(f"{self.thread_id}.json") 
        self.auto_response = auto_response

    def __str__(self):
        """Vrátí název vlákna případně seznam přezdívek účastníků."""
        if self.thread.name:
            return self.thread.name
        else:
            return ', '.join(self.participants[participant_id]["nickname"] for participant_id in self.participants)

    def set_character(self, character: Character):
        """Nastaví postavu."""
        self.character = character

    def add_message(self, role: str, text: str, uid: str = None):
        """Přidá zprávu do konverzace."""
        self.logger.debug(f"Message before trim: {text}")
        # Ořezání různých možností začátku zprávy pomocí regulárního výrazu
        patterns = [":", " ", re.escape(self.character.name)]
        pattern = r'^(' + '|'.join(patterns) + ')+'
        text = re.sub(pattern, '', text)
        self.logger.debug(f"Message after trim: {text}")

        if uid is None:
            name = self.character.name
        else:
            name = self.get_participant_full_name(uid)

        self.memory.add_message(role, name, text)

    def handle_send(self):
        """Zpracuje zprávy a získá odpověď od AI."""
        mess = [{"role": "system", "content": self.character.character_setting}] + self.memory.history

        try:
            response = self.character.ai.get_response(mess)
            return response
        except OpenAIError as e:
            print(f'Error: {e}\n')

            if "max tokens" in str(e):
                self.memory.manage_history(0.5)
                print("Právě jsem zapomněl půku své identity.")

            return self.handle_send()  # rekurzivní volání s ořezanými zprávami
        except Exception as e:
            print(f'Error: {e}\n')
            return None

    def get_participant_name(self, participant_id) -> str|None:
        """Získá jméno účastníka zadaného podle ID."""
        return self.participants[participant_id]['name']

    def get_participant_nickname(self, participant_id) -> str|None:
        """Získá přezdívku účastníka zadaného podle ID."""
        return self.participants[participant_id]['nickname']
    
    def get_participant_full_name(self, participant_id: str) -> str|None:
        """Získá plné označení účastníka zadaného podle ID."""
        if self.participants is None:
            logging.error("[get_participant_full_name] No participants found.")
            return ""
        participant: dict = self.participants.get(participant_id)
        if participant is None:
            logging.error(f"Unknown participant: {participant_id}")
            return ""
        return f"{participant['nickname']} ({participant['name']})"

    # def fetch_participants(self, thread: Thread) -> dict[str, dict[str, str|bool]]:
    #     logging.info("Fetching participants...")
    #     if thread is None:
    #         thread = self.thread
    #     # logging.info(f"Thread: {self.thread}")
    #     participants = {}
    #     if thread.type == ThreadType.USER:
    #         participants[thread.uid] = {
    #             "name": thread.name or "",
    #             "nickname": thread.nickname or "",
    #             "is_friend": thread.is_friend,
    #         }

    #     elif thread.type == ThreadType.GROUP:
    #         user_ids = thread.participants
    #         for user_id in user_ids:
    #             user_info = self.thread.fetchUserInfo(user_id)[user_id]
    #             participants[user_id] = {
    #                 "name": user_info.name or "",
    #                 "nickname": thread.nicknames.get(user_id, ""),
    #                 "is_friend": user_info.is_friend,
    #             }
    #     else:
    #         logging.error(f"Unknown thread type: {thread.type}")

    #     logging.info(f"Participants: {participants}")
    #     return participants