import json
import logging
import os
from colorama import Fore, Style, init
import openai
from character import Character
from fbm import MessengerClient
from fbchat import ThreadType
from config import FB_EMAIL, FB_PASSWORD, ROOT_DIR

# Konstanty
PROMPT_CHARACTER = f"Zadejte postavu"
PROMPT_SEND = ", nebo 'send' pro odeslání konverzace: "

init()  # Inicializace colorama


def load_character(config_file='Glum.json'):
    config_file = os.path.join(ROOT_DIR, 'characters', config_file)
    default_config = {
        'name': 'No One',
        'character_setting': 'Jsi charakter ze Hry o trůny, jsi Nikdo. Nikdo je ztělesněním emocionálního odloučení, je nemilosrdný a chladnokrevný. Vyhýbáš se osobním zájmenům a čehokoliv, co by odhalilo osobní identitu. Nikdo mluví stručně a neosobně.'
    }

    config = None
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)

    if not config or not config.get('name') or not config.get('character_setting'):
        print(f"{Fore.YELLOW}Invalid or missing configuration file {config_file}. Defaulting to character 'No One'.{Style.RESET_ALL}")
        config = default_config

    return Character(
        name=config['name'],
        character_setting=config['character_setting'],
        temperature=config.get('temperature'),
        max_tokens=config.get('max_tokens'),
        logit_bias=config.get('logit_bias'),
        presence_penalty=config.get('presence_penalty')
    )
    
def get_participants():
    participants = input("Zadejte postavy, oddělené čárkou: ").split(",")
    return [char.strip() for char in participants]

def get_user_input(participants):
    user_input = input(f"{PROMPT_CHARACTER} ({', '.join(participants)}){PROMPT_SEND}")
    if user_input.lower() in ['quit', 'send', 'save']:
        return user_input.lower(), None
    if user_input not in participants:
        print(f"{Fore.RED}Neznámá postava. Zkuste to znovu.{Style.RESET_ALL}")
        return None, None  # Vrátí None, aby hlavní smyčka pokračovala
    
    user_input_text = input(f"{Fore.MAGENTA}{user_input}: {Style.RESET_ALL}")
    return user_input, user_input_text

def handle_send(glum):
    mess = [{"role": "system", "content": glum.character_setting}] + glum.messages

    try:
        response = glum.ai.get_response(mess)
        return response
    except openai.error.OpenAIError as e:
        print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}\n')

        if "max tokens" in str(e):
            glum.messages = glum.ai.prune_messages(glum.messages, 0.5)
            print(f"{Fore.YELLOW}Právě jsem zapněl půku své identity.{Style.RESET_ALL}")

        return handle_send(glum)  # rekurzivní volání s ořezanými zprávami
    except Exception as e:
        print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}\n')
        return None

def main():
    glum = load_character()
    with open("session.json") as f:
        cookies = json.load(f)
    fb_client = MessengerClient(FB_EMAIL, FB_PASSWORD, max_tries=1, session_cookies=cookies, logging_level=logging.INFO)
    thread_id = "2853571361363788"
    
    print(Fore.CYAN + "Vítejte v chatbotu. Zadejte 'quit' pro ukončení." + Style.RESET_ALL)
    print(f"{Fore.LIGHTBLUE_EX}Participant: {fb_client.fetch_participants(thread_id)}{Style.RESET_ALL}")
    participants = get_participants()

    while True:
        print()  # Prázdný řádek pro lepší orientaci
        participant_name, participant_input = get_user_input(participants)
        
        if participant_name == 'quit':
            print(f"{Fore.YELLOW}{glum} jde spát a memoruje. 💤{Style.RESET_ALL}")
            glum.save_conversation()
            cookies = fb_client.getSession()
            with open("session.json", "w") as f:
                json.dump(cookies, f)
            break

        if participant_name == 'send':
            response = handle_send(glum)
            if response:
                print(f'{Fore.GREEN}{response}{Style.RESET_ALL}\n')
                fb_client.send_message(response, thread_id, thread_type=ThreadType.GROUP)
                glum.add_message("system", glum, response)
            continue

        if participant_name == 'save':
            print(f"{Fore.YELLOW}Neboj, {glum} to nezapomene.{Style.RESET_ALL}")
            glum.save_conversation()  # Uložení konverzace na vyžádání
            continue

        if participant_name and participant_input:
            glum.add_message("user", participant_name, participant_input) 

if __name__ == "__main__":
    main()
