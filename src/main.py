import signal
from bot_manager import ClientManager
from config import FB_EMAIL, FB_PASSWORD

def main():
    print("Starting the bot.")
    print("Press Ctrl+C to exit.")
    
    bot_manager = ClientManager(FB_EMAIL, FB_PASSWORD)
    # handlery pro signály ukončení
    signal.signal(signal.SIGINT, lambda signum, frame: bot_manager.shutdown())
    signal.signal(signal.SIGTERM, lambda signum, frame: bot_manager.shutdown())

    bot_manager.initialize()
    bot_manager.run()

if __name__ == "__main__":
    main()