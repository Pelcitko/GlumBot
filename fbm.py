from fbchat import Client, ThreadType
from fbchat.models import Message

from secrets import FB_EMAIL, FB_PASSWORD

class MessengerClient(Client):
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
