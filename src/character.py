# character.py
import logging
from ai import AI
from log_formatter import CustomFormatter


class Character:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    def __init__(
        self, 
        name: str, 
        character_setting: str, 
        temperature: float = 0.5, 
        max_tokens: int = 512, 
        logit_bias: dict[str, float] = None, 
        presence_penalty: float = None
    ):
        """
        Inicializuje postavu se zadanými nastaveními.

        :param name: Jméno postavy.
        :param character_setting: Nastavení charakteru pro systémovou zprávu.
        :param temperature: Parametr řízení náhodnosti odpovědí, hodnoty blíže 0 vedou k determinističtějším odpovědím.
        :param max_tokens: Maximální počet tokenů, které mohou být generovány při odpovídání.
        :param logit_bias: Mapa tokenů a jejich biasů, které ovlivňují pravděpodobnost výběru tokenů.
        :param presence_penalty: Pokuta za přítomnost nových tokenů, hodnoty blíže 2 vedou k větší pravděpodobnosti nových témat.
        """
        self.name = name
        self.character_setting = character_setting
        self.ai: AI = AI(
            user=name,
            temperature=temperature,
            max_tokens=max_tokens,
            logit_bias=logit_bias,
            presence_penalty=presence_penalty
        )
        # self.memory = os.path.join("characters_memory", f"{name}.json")
        # self.messages = self.load_conversation()

    def __str__(self) -> str:
        """Vrátí jméno postavy."""
        return self.name

    # def save_conversation(self) -> None:
    #     """Uloží současnou konverzaci do souboru."""
    #     with open(self.memory, "w", encoding="utf-8") as file:
    #         json.dump(self.messages, file, indent=2)

    # def load_conversation(self) -> list[dict[str, str]]:
    #     """Načte konverzaci ze souboru nebo vrátí výchozí systémovou zprávu, pokud soubor neexistuje."""
    #     if os.path.exists(self.memory):
    #         with open(self.memory, "r", encoding="utf-8") as file:
    #             print(f"{Fore.YELLOW}Postava si právě vzpoměla o čem jste se bavili minule.{Style.RESET_ALL}")
    #             return json.load(file)
    #     print(f"{Fore.YELLOW}Konverzace nenalezena, postova přichází do nové konverzace.{Style.RESET_ALL}")
    #     return []

    # def add_message(self, role: str, participant: str, content: str) -> None:
    #     """Přidá zprávu do seznamu zpráv postavy."""
    #     new_message = {"role": role, "content": f"{participant}: {content}"}
    #     print(f"{Fore.GREEN}🧠: {new_message}{Style.RESET_ALL}")
    #     self.messages.append(new_message)