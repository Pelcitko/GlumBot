import signal
from bot_manager import ClientManager
from config import FB_EMAIL, FB_PASSWORD


def main():
    bot_manager = ClientManager(FB_EMAIL, FB_PASSWORD)
    bot_manager.initialize()
    bot_manager.run()

if __name__ == "__main__":
    main()