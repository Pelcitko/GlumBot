import csv
import json
import os
from colorama import Fore, Style, init

from ai import AI

class Character:
    def __init__(
        self, 
        name: str, 
        character_setting: str, 
        temperature: float, 
        max_tokens: int, 
        logit_bias: dict[str, float], 
        presence_penalty: float
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
        self.ai = AI(
            user=name,
            temperature=temperature,
            max_tokens=max_tokens,
            logit_bias=logit_bias,
            presence_penalty=presence_penalty
        )
        self.memory = f"memory_of_{name}.msg"
        self.last_saved_message_index = 0
        self.messages = self.load_conversation()

    def save_conversation(self) -> None:
        """Uloží nové zprávy z konverzace do souboru."""
        new_messages = self.messages[self.last_saved_message_index:]  # Získání nových zpráv
        if new_messages:  # Pokud existují nové zprávy
            with open(self.memory, "a", encoding='utf-8') as file:  # Otevření souboru v módu 'append'
                for message in new_messages:
                    file.write(json.dumps(message) + '\n')  # Uložení každé nové zprávy jako řádek
            self.last_saved_message_index += len(new_messages)  # Aktualizace indexu poslední uložené zprávy

    def load_conversation(self) -> list[dict[str, str]]:
        """Načte konverzaci ze souboru nebo vrátí výchozí systémovou zprávu, pokud soubor neexistuje."""
        if os.path.exists(self.memory):
            with open(self.memory, "r", encoding='utf-8') as file:  # Otevření souboru v módu 'read'
                self.messages = [json.loads(line) for line in file]  # Čtení každého řádku a jeho převedení zpět na slovník
            self.last_saved_message_index = len(self.messages)  # Aktualizace indexu poslední uložené zprávy
        else:
            self.messages = [{"role": "system", "content": self.character_setting}]
            self.last_saved_message_index = 1  # První zpráva byla právě vytvořena
        return self.messages

    def add_message(self, role: str, content: str) -> None:
        """Přidá zprávu do seznamu zpráv postavy."""
        new_message = {"role": role, "content": f"{self.name}: {content}"}
        self.messages.append(new_message)