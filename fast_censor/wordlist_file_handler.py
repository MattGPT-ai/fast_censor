"""this class handles reading / writing and encrypting / decrypting files for word lists"""

import base64
from os import path
from typing import List, Generator


class WordListHandler:
    """class that handles reading / decrypting files and writing new files"""

    def __init__(self, debug: bool = False):

        self.debug = debug

    @staticmethod
    def read_file_lines(file_path: str) -> List[str]:
        """reads file at path and returns lines as a list of strings"""
        with open(file_path, 'r') as infile:
            return infile.readlines()

    @staticmethod
    def write_file_lines(lines: List[str], file_path: str) -> None:
        """writes list of strings as lines to file path"""
        with open(file_path, 'w') as outfile:
            for line in lines:
                outfile.write(line)
                outfile.write('\n')

    @staticmethod
    def decrypt_string(encrypted_string: str) -> str:
        """takes string (not bytes) and decrypts using your cypher. returns string"""
        return base64.b64decode(encrypted_string.encode()).decode()

    @staticmethod
    def encrypt_string(string: str) -> str:
        """takes regular string and encrypts using your cypher, returns string"""
        return base64.b64encode(string.encode()).decode()

    def read_and_decrypt_file(self, encrypted_file_path: str) -> List[str]:
        """read an encrypted file and return decrypted lines"""
        lines = WordListHandler.read_file_lines(encrypted_file_path)
        return [self.decrypt_string(line) for line in lines]

    def encrypt_and_write_lines(self, lines: List[str], outfile_path) -> None:
        """encrypt strings in lines and write to outfile path"""
        encrypted_lines = [self.encrypt_string(line) for line in lines]
        self.write_file_lines(encrypted_lines, outfile_path)

    def read_wordlist_file(self, filename: str, decrypt: bool = False) -> Generator[str, None, None]:
        """Return words from a wordlist file."""
        with open(filename, encoding="utf-8") as wordlist_file:
            for line in wordlist_file:
                if line != "":
                    if decrypt:
                        line = self.decrypt_string(line)
                    yield line

    @staticmethod
    def get_complete_path_of_file(filename: str) -> str:
        """Join the path of the current directory with the input filename."""
        root = path.abspath(path.dirname(__file__))
        return path.join(root, filename)

    @classmethod
    def get_default_wordlist_path(cls) -> str:
        """returns absolute path to wordlist file included in package"""
        return cls.get_complete_path_of_file("word_lists/profanity_wordlist_encrypted.txt")
