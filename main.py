import json
import os
import logging
import glum
from colorama import Fore, Style, init

# Konstanty
PROMPT_CHARACTER = f"Zadejte postavu"
PROMPT_SEND = ", nebo 'send' pro odeslání konverzace: "

# Inicializace
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
init()  # Inicializace colorama

# Konstanty
CONVERSATION_FILE = "conversation.json"

def save_conversation(messages):
    with open(CONVERSATION_FILE, "w") as file:
        json.dump(messages, file, indent=2)

def load_conversation():
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, "r") as file:
            return json.load(file)
    return [{"role": "system", "content": "Jsi Glum, postava z knihy Pán prstenů. Používej jeho repliky, aby tvé odpovědi byly co nejvíce v jeho stylu. Používej hodně slova 'my', 'Glum', 'můj a 'milášek'."}]  # Výchozí zpráva

def get_characters():
    characters = input("Zadejte postavy, oddělené čárkou: ").split(",")
    return [char.strip() for char in characters]

def get_user_input(characters):
    character = input(f"{PROMPT_CHARACTER} ({', '.join(characters)}){PROMPT_SEND}")
    if character.lower() in ['quit', 'send']:
        return character.lower(), ""
    if character not in characters:
        print(f"{Fore.RED}Neznámá postava. Zkuste to znovu.{Style.RESET_ALL}")
        return None, None  # Vrátí None, aby hlavní smyčka pokračovala
    user_input = input(f"{Fore.MAGENTA}{character}: {Style.RESET_ALL}")
    return character, user_input

def main():
    print(Fore.CYAN + "Vítejte v chatbotu. Zadejte 'quit' pro ukončení." + Style.RESET_ALL)
    characters = get_characters()
    messages = load_conversation()

    while True:
        print()  # Prázdný řádek pro lepší orientaci
        character, user_input = get_user_input(characters)
        if character == 'quit':
            break
        if character == 'send':
            response = glum.get_response(messages)
            print(f'{Fore.GREEN}{response}{Style.RESET_ALL}\n')
            save_conversation(messages)  # Uloží konverzaci po každém odeslání
            continue
        if character and user_input:  # Pokud není None
            messages.append({"role": "user", "content": f"{character}: {user_input}"})

if __name__ == "__main__":
    main()
