import json
import logging
import os
from colorama import Fore, Style, init
from character import Character

# Konstanty
PROMPT_CHARACTER = f"Zadejte postavu"
PROMPT_SEND = ", nebo 'send' pro odeslání konverzace: "

# Inicializace
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
init()  # Inicializace colorama


def load_character(config_file='character_config.json'):
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
        return Character(
            name=config.get('name', 'No One'),
            character_setting=config.get('character_setting', 'Jsi charakter ze Hry o trůny, jsi Nikdo. Nikdo je ztělesněním emocionálního odloučení, je nemilosrdný a chladnokrevný. Vyhýbáš se osobním zájmenům a čehokoliv, co by odhalilo osobní identitu. Nikdo mluví stručně a neosobně.'),
            temperature=config.get('temperature', 0.7),
            max_tokens=config.get('max_tokens', 128),
            logit_bias=config.get('logit_bias', {}),
            presence_penalty=config.get('presence_penalty', 0)
        )
    else:
        raise FileNotFoundError(f'Configuration file {config_file} not found.')
    
def get_participants():
    participants = input("Zadejte postavy, oddělené čárkou: ").split(",")
    return [char.strip() for char in participants]

def get_user_input(characters):
    participant = input(f"{PROMPT_CHARACTER} ({', '.join(characters)}){PROMPT_SEND}")
    if participant.lower() in ['quit', 'send']:
        return participant.lower(), ""
    if participant not in characters:
        print(f"{Fore.RED}Neznámá postava. Zkuste to znovu.{Style.RESET_ALL}")
        return None, None  # Vrátí None, aby hlavní smyčka pokračovala
    user_input = input(f"{Fore.MAGENTA}{participant}: {Style.RESET_ALL}")
    return participant, user_input

def main():
    print(Fore.CYAN + "Vítejte v chatbotu. Zadejte 'quit' pro ukončení." + Style.RESET_ALL)
    participants = get_participants()
    glum = load_character()

    while True:
        print()  # Prázdný řádek pro lepší orientaci
        participant_name, participant_input = get_user_input(participants)
        if participant_name == 'quit':
            break
        if participant_name == 'send':
            response = glum.ai.get_response(glum.messages)
            print(f'{Fore.GREEN}{response}{Style.RESET_ALL}\n')
            glum.save_conversation()  # Uloží konverzaci po každém odeslání
            continue
        if participant_name and participant_input:  # Pokud není None
            glum.add_message("user", participant_input)  # Použije existující objekt Glum

if __name__ == "__main__":
    main()
