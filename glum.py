import openai
import logging
from colorama import Fore, Style, init
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_response(messages):
    # logging.debug(f'Sending: {messages}')
    print(f'{Fore.LIGHTBLACK_EX}Sending: {messages}{Style.RESET_ALL}\n')
    
    try:
        # Volání OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=128
        )
        
        # logging.debug(f'Received: {response}')
        print(f'{Fore.LIGHTBLACK_EX}Received: {response}{Style.RESET_ALL}\n')

        message = response['choices'][0]['message']['content'].strip()
        return message
    except Exception as e:
        logging.error(f'Error: {e}')
        return str(e)
