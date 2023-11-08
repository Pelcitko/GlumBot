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
    pending_action = None  # Ukládáme příkaz čekající na potvrzení

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


    @staticmethod
    def clean_message(text):
        """Odstraní tagy uživatelů ve tvaru @UživatelskéJméno z textu zprávy."""
        # Zkontroluj, jestli text není prázdný nebo není textový typ
        if not text or not isinstance(text, str):
            return text

        # Odstranění tagů a trim whitespace
        cleaned_text = re.sub(r'@\S+', '', text)
        return cleaned_text

    @staticmethod
    def recognize_command(text):
        commands = {
            'help': r"(help|pomoc|\?|man|manual|návod|🆘)",
            'about': r"(about|o tobě|představ se|info|informace|ℹ️)",
            'list_characters': r"(list characters|ukaz postavy|ukázat osobnosti|vypsat charaktery|👥)",
            'autoresponse': r"(autoresponse|auto-odpovědi|automatické odpovědi|zapnout auto|vypnout auto|💭|🗣️|🙊)",
            'forget': r"(forget|zapomeň|smaž historii|vymazat paměť|🧹|🗑️)",
            'status': r"(status|stav|jak funguješ|kontrola|🚦)",
            'switch_character': r"(switch character|změnit charakter|přepnout osobnost|změna postavy|🎭)",
            'mute': r"(mute|ztišit|ticho|neodpovídej|🔇)",
            'unmute': r"(unmute|aktivuj|mluv|odpovídej|🔊)"
        }
        # Normalize the input text
        normalized_text = text.lower()
        for command, pattern in commands.items():
            if re.search(pattern, normalized_text):
                return command
        return None  # If no command is recognized
    
    @staticmethod
    def recognize_command(text):
        # ... statická metoda rozpoznávající příkaz
        pass

    @staticmethod
    def is_positive_confirmation(text):
        positive_confirmations = ['ano', 'yes', 'jo', 'ok', '✔', 'správně', 'jasně', 'samozřejmě', 'to jo']
        negative_confirmations = ['ne', 'no', 'nechci', '❌', 'nemyslím', 'ani náhodou', 'to ne']

        # Převedení textu na malá písmena a odstranění bílých znaků pro jednodušší porovnání
        text = text.strip().lower()

        # Počítání výskytů
        positive_count = sum(text.count(word) for word in positive_confirmations)
        negative_count = sum(text.count(word) for word in negative_confirmations)

        # Zjištění, jestli text obsahuje více kladných než záporných výrazů
        confirmation_score = positive_count - negative_count

        # Pokud je zpráva příliš dlouhá vzhledem k nalezeným výskytům, nebudeme rozhodovat
        if len(text) > (positive_count + negative_count) * 13:
            return None  # Znamená, že nemůžeme rozhodnout a možná se zeptáme znovu

        return confirmation_score > 0  # True pokud je score kladné, False pokud záporné nebo nulové

    @staticmethod
    def is_positive_confirmation(text):
        # ... statická metoda pro detekci kladné odpovědi
        pass