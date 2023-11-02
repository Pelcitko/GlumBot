# messenger_client.py
from colorama import Fore, Style
import logging
from fbchat import Client, ThreadType, Thread
from fbchat.models import Message
from openai import OpenAIError 
from character import Character

logging.basicConfig(level=logging.INFO, format=f"{Fore.BLUE}%(message)s{Style.RESET_ALL}")


class MessengerClient(Client):

    def __init__(self, email, password, max_tries=2, session_cookies=None):
        super().__init__(email, password, max_tries=max_tries, session_cookies=session_cookies)
        # self.character: Character = NO_ONE  # Přiřazení defaultní postavy
        self.threads: dict[str, Thread] = {}  # Seznam konverzačních vláken
        self.threads_participants: dict[str, dict] = {}  # Seznamy účastníků ve vlákenech
        self.threads_auto_response: dict[str, bool] = {}  # Nastavení kdy bot odpovídá automaticky

    def set_conversation(self, thread_id: str, auto_response: bool = False) -> Thread:
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

    def onMessage(self, mid=None, author_id=None, message=None, message_object=None, thread_id=None, thread_type=None, ts=None, metadata=None, msg={}):
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

        # Uložení vlastních zpráv do historie
        if author_id == self.uid:
            self.character.add_message("assistant", self.character, message_object.text)
            return

        participant_full_name = self.get_participant_name(author_id)
        self.character.add_message("user", participant_full_name, message_object.text)

        if thread_id == self.thread.uid:
            self.markAsRead(thread_id)

            # Zpracování zprávy a získání odpovědi, pokud je označen
            if message_object.mentions:
                ai_response = self.handle_send()
                if ai_response:
                    self.send_message(ai_response, thread_id, thread_type)


    def handle_send(self):
        mess = [{"role": "system", "content": self.character.character_setting}] + self.character.messages

        try:
            response = self.character.ai.get_response(mess)
            return response
        except OpenAIError as e:
            print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}\n')

            if "max tokens" in str(e):
                self.character.messages = self.character.ai.prune_messages(self.character.messages, 0.5)
                print(f"{Fore.YELLOW}Právě jsem zapomněl půku své identity.{Style.RESET_ALL}")

            return self.handle_send()  # rekurzivní volání s ořezanými zprávami
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
