# fbm.py
from colorama import Fore, Style
from fbchat import Client, ThreadType, Thread
from fbchat.models import Message

from config import FB_EMAIL, FB_PASSWORD


class MessengerClient(Client):
    def fetch_participants(self, thread_id) -> dict[str, dict[str, str]]:
        """
        Získá seznam účastníků chatu ve zvoleném vláknu.

        :param thread_id: ID vlákna.
        :return: Slovník účastníků chatu.
        """
        thread = self.fetchThreadInfo(thread_id)[thread_id]
        print(f"{Fore.LIGHTBLUE_EX}Thread info: {thread}{Style.RESET_ALL}")
        user_ids = thread.participants
        participants = {}
        for user_id in user_ids:
            user_info = self.fetchUserInfo(user_id)[user_id]
            participants[user_id] = {
                "name": user_info.name,
                "nickname": thread.nicknames.get(user_id, ""),
                "is_friend": user_info.is_friend,
            }
        print(f"{Fore.LIGHTBLUE_EX}Participants: {participants}{Style.RESET_ALL}")
        return participants


    def send_message(self, message, thread_id, thread_type=ThreadType.USER):
        """
        Odešle zprávu do zadaného vlákna.
        
        :param message: Text zprávy k odeslání.
        :param thread_id: ID vlákna, do kterého se má zpráva odeslat.
        :param thread_type: Typ vlákna (uživatel, skupina, stránka). Defaultní je uživatel.
        """
        if not self.isLoggedIn():
            self.login(FB_EMAIL, FB_PASSWORD)
        self.send(
            Message(text=message),
            thread_id=thread_id,
            thread_type=thread_type
        )
