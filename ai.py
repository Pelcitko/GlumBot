import openai
import logging
from colorama import Fore, Style
import tiktoken
from secret import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
DEAFAULT_MODEL = "gpt-3.5-turbo"

class AI:
    def __init__(self, user:str, model: str = DEAFAULT_MODEL, temperature=None, max_tokens=None, logit_bias=None, presence_penalty=None):
        """
        Inicializuje instanci AI s danými nastaveními.

        :param model: Název modelu, který bude použit pro generování textu. Defaultní je "gpt-3.5-turbo".
        :param temperature: Hodnota (0-1) řídící náhodnost generovaného textu. Nižší hodnoty vedou k více deterministickému textu. Defaultní je 1.
        :param max_tokens: Maximální počet tokenů, které může kontextové okno obsahovat. Defaultně je maximální počet tokenů, které může model vygenerovat.
        :param logit_bias: Slovník pro úpravu logitů konkrétních tokenů, kde klíče jsou stringy token IDs a hodnoty jsou float bias hodnoty. 
                           Např {"50256": -20}. Tokeny lze vypátrat pomocí https://platform.openai.com/tokenizer
        :param presence_penalty: Hodnota (0-2) udávající trest za nepřítomnost tokenů ve výstupu. Defaultní je 0.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logit_bias = logit_bias
        self.presence_penalty = presence_penalty
        self.user = user

    def get_response(self, messages: list[dict[str, str]]):
        # logging.debug(f'Sending: {messages}')
        print(f'{Fore.LIGHTBLACK_EX}Sending: {messages}{Style.RESET_ALL}\n')

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                logit_bias=self.logit_bias,
                presence_penalty=self.presence_penalty
            )
            # logging.debug(f'Received: {response}')
            print(f'{Fore.LIGHTBLACK_EX}Received: {response}{Style.RESET_ALL}\n')

            message = response['choices'][0]['message']['content'].strip()
            return message
        except Exception as e:
            logging.error(f'Error: {e}')
            

    def prune_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Ořeže seznam zpráv tak, aby celkový počet tokenů nepřekročil max_tokens.

        :param messages: Seznam zpráv ke zpracování.
        :return: Ořezaný seznam zpráv.
        """
        while self.num_tokens_from_messages(messages) > self.max_tokens:
            messages.pop(0)
        return messages

    def num_tokens_from_messages(self, messages: list[dict[str, str]], model: str = DEAFAULT_MODEL) -> int:
        """
        Vypočte celkový počet tokenů ve zprávách na základě specifikace modelu.

        :param messages: Seznam zpráv ke zpracování.
        :param model: Název modelu použitého pro výpočet počtu tokenů. Defaultní je "gpt-3.5-turbo".
        :return: Celkový počet tokenů ve zprávách.
        """
        encoding = tiktoken.encoding_for_model(model)
        tokens_count = 0
        for message in messages:
            content = message['content']
            tokens_count += len(encoding.encode(content))
        return tokens_count