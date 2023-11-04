from fbchat.models import Thread, ThreadType
from character import Character
from openai import OpenAIError

class Conversation:
    def __init__(self, thread: Thread, participants: dict, character: Character):
        self.thread: Thread = thread
        self.participants: dict = participants
        self.character: Character = character   # vytvořte novou instanci postavy nebo předejte existující instanci
        self.messages = []  # seznam zpráv ve vláknu
        self.auto_response = False

    def __str__(self):
        """Vrátí název vlákna."""
        return self.thread.name
    
    def set_character(self, character: Character):
        """Nastaví postavu."""
        self.character = character

    def add_message(self, role: str, text: str, participant: str = None):
        """Přidá zprávu do konverzace."""
        if participant is None:
            name = self.character
        else:
            name = self.get_participant_name(participant)

        self.messages.append({
            'role': role,
            'name': name,
            'content': text
        })

    def handle_send(self):
        """Zpracuje zprávy a získá odpověď od AI."""
        mess = [{"role": "system", "content": self.character.character_setting}] + self.messages

        try:
            response = self.character.ai.get_response(mess)
            return response
        except OpenAIError as e:
            print(f'Error: {e}\n')

            if "max tokens" in str(e):
                self.messages = self.character.ai.prune_messages(self.messages, 0.5)
                print("Právě jsem zapomněl půku své identity.")

            return self.handle_send()  # rekurzivní volání s ořezanými zprávami
        except Exception as e:
            print(f'Error: {e}\n')
            return None

    def get_participant_name(self, participant_id):
        """Získá plné označení účastníka zadaného podle ID."""
        if self.thread.type == ThreadType.USER:
            return f"{self.participants['name']} ({self.participants['nickname']})"
        elif self.thread.type == ThreadType.GROUP:
            return f"{self.participants[participant_id]['nickname']} ({self.participants[participant_id]['name']})"
        return "Unknown"

    def get_participant_nickname(self, participant_id):
        """Získá přezdívku účastníka zadaného podle ID."""
        if self.thread.type == ThreadType.USER:
            return self.participants['nickname']
        elif self.thread.type == ThreadType.GROUP:
            return self.participants[participant_id]['nickname']
        return "Unknown"