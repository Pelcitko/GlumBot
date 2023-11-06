import logging
import openai
from colorama import Fore, Style
import tiktoken
from config import OPENAI_API_KEY, DEAFAULT_MODEL

# Initialize logging
logging.basicConfig(format=f'{Fore.LIGHTBLACK_EX}%(message)s{Style.RESET_ALL}', level=logging.INFO)

openai.api_key = OPENAI_API_KEY


class AI:
    def __init__(self, user:str, model: str = DEAFAULT_MODEL, temperature=None, max_tokens=None, logit_bias=None, presence_penalty=None):
        """
        Initialize an instance of AI with given settings.

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
        """
        Fetch a response from the OpenAI API.
        """
        logging.info(f'Sending: {messages}')

        try:
            # Vytvoření slovníku z atributů objektu a filtrování None hodnot
            params = {key: value for key, value in vars(self).items() if value is not None}

            # Přidej specifické parametry, které jsou vždy potřeba
            params.update({
                "model": self.model,
                "messages": messages
            })

            # Zavolej OpenAI API s dynamicky sestavenými parametry
            response = openai.ChatCompletion.create(**params)
        except Exception as e:
            logging.error(f'OpenAI API Error: {e}')
            return "🤕 An error occurred when calling my brain."

        logging.info(f'Received: {response}')
        return response['choices'][0]['message']['content'].strip()


    # def get_response(self, messages: list[dict[str, str]]):
    #     """
    #     Fetch a response from the OpenAI API.
    #     """
    #     logging.info(f'Sending: {messages}')

    #     try:
    #         response = openai.ChatCompletion.create(
    #             model=self.model,
    #             messages=messages,
    #             temperature=self.temperature,
    #             max_tokens=self.max_tokens,
    #             logit_bias=self.logit_bias,
    #             presence_penalty=self.presence_penalty
    #         )
    #     except Exception as e:
    #         logging.error(f'OpenAI API Error: {e}')
    #         return "An error occurred."

    #     logging.info(f'Received: {response}')
    #     return response['choices'][0]['message']['content'].strip()
            

    def prune_messages(self, messages: list[dict[str, str]], prune_ratio: float) -> list[dict[str, str]]:
        """
        Ořeže seznam zpráv na základě zadaného prune_ratio nebo odstraní zprávy tak, aby celkový počet tokenů nepřekročil max_tokens.

        :param messages: Seznam zpráv ke zpracování.
        :param prune_ratio: Poměr zpráv ke smazání (0-1) nebo -1 pro odstranění jedné zprávy. Pokud je hodnota 0, bude seznam ořezáván tak, aby celkový počet tokenů nepřekročil max_tokens.
        :return: Ořezaný seznam zpráv.
        """
        if prune_ratio:
            prune_length = int(len(messages) * prune_ratio)
            return messages[prune_length:]
        elif prune_ratio == -1:
            return messages.pop(0)
        else:
            while self.num_tokens_from_messages(messages) > self.max_tokens:
                messages.pop(0)
            return messages

    def num_tokens_from_messages(self, messages: list[dict[str, str]], model: str = DEAFAULT_MODEL) -> int:
        """
        Calculate the total number of tokens in the messages based on the model specification.

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