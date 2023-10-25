import logging
import glum
from colorama import Fore, Style, init

logging.basicConfig(level=logging.INFO)
init()  # Inicializace colorama

def main():
    print(Fore.CYAN + "Vítejte v chatbotu. Zadejte 'quit' pro ukončení." + Style.RESET_ALL)
    characters = input("Zadejte postavy, oddělené čárkou: ").split(",")
    characters = [char.strip() for char in characters]
    messages = [{"role": "system", "content": "Jsi Glum, postava z knihy Pán prstenů. Používej jeho repliky, aby tvé odpovědi byly co nejvíce v jeho stylu. Používej hodně slova 'my', 'Glum', 'můj a 'milášek'."}]
    print()  # Prázdný řádek pro lepší orientaci

    while True:
        character = input(f"Zadejte postavu ({', '.join(characters)}), nebo 'send' pro odeslání konverzace: ")
        if character.lower() == 'quit':
            break
        if character.lower() == 'send':
            response = glum.get_response(messages)
            logging.info(f'Received: {response}')
            print(f'{Fore.GREEN}Glum: {response}{Style.RESET_ALL}\n')  # Prázdný řádek pro lepší orientaci
            continue  # Skočí zpět na začátek smyčky
        if character not in characters:
            print(f"{Fore.RED}Neznámá postava. Zkuste to znovu.{Style.RESET_ALL}")
            continue
        user_input = input(f"{Fore.MAGENTA}{character}: {Style.RESET_ALL}")
        messages.append({"role": "user", "content": f"{character}: {user_input}"})
        logging.info(f'Sending: {messages[-1]}')

if __name__ == "__main__":
    main()
