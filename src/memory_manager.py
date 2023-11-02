import json
import logging
import os
from typing import List, Dict
from colorama import Fore, Style

# Initialize logging
logging.basicConfig(format=f'{Fore.LIGHTBLACK_EX}%(message)s{Style.RESET_ALL}', level=logging.INFO)

class MemoryManager:
    def __init__(self, memory_file: str):
        """
        Initialize MemoryManager with a memory_file to store conversations.

        :param memory_file: File path to store conversations.
        """
        self.memory_file = memory_file
        self.history: List[Dict[str, str]] = self.load()  # Load existing conversations from the file.

    def save(self) -> None:
        """
        Save current conversation history to memory_file.
        """
        with open(self.memory_file, "w", encoding="utf-8") as file:
            json.dump(self.history, file, indent=2)
        logging.info(f"{Fore.YELLOW}Memory saved.{Style.RESET_ALL}")

    def load(self) -> List[Dict[str, str]]:
        """
        Load conversations from memory_file, or create an empty list if the file does not exist.
        """
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as file:
                logging.info(f"{Fore.YELLOW}Memory loaded.{Style.RESET_ALL}")
                return json.load(file)
        logging.info(f"{Fore.YELLOW}Memory not found, starting a new conversation.{Style.RESET_ALL}")
        return []

    def add_message(self, role: str, participant: str, content: str) -> None:
        """
        Add a new message to the history.
        """
        new_message = {"role": role, "content": f"{participant}: {content}"}
        self.history.append(new_message)
        logging.info(f"{Fore.GREEN}New message added to memory: {new_message}{Style.RESET_ALL}")

    def manage_history(self, messages: List[Dict[str, str]], prune_ratio: float) -> List[Dict[str, str]]:
        """
        Prune message history based on a given ratio or some condition.

        :param messages: List of current messages.
        :param prune_ratio: Ratio of messages to prune.
        :return: Pruned list of messages.
        """
        if prune_ratio:
            prune_length = int(len(messages) * prune_ratio)
            logging.info(f"{Fore.YELLOW}Pruning {prune_length} messages from memory.{Style.RESET_ALL}")
            return messages[prune_length:]
        else:
            logging.info(f"{Fore.YELLOW}Other pruning logic not implemented yet.{Style.RESET_ALL}")
            return messages
