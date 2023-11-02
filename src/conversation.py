from fbchat.models import Thread, ThreadType
from character import Character
from openai import OpenAIError

class Conversation:
    def __init__(self, thread: Thread, participants: dict):
        self.thread = thread
        self.participants = participants
        self.character = Character()  # vytvořte novou instanci postavy nebo předejte existující instanci
        self.messages = []  # seznam zpráv ve vláknu

    def add_message(self, role: str, name: str, text: str):
        """Přidá zprávu do konverzace."""
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
