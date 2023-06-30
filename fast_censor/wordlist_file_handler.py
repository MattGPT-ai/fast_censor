"""this class handles reading / writing and encrypting / decrypting files for word lists"""

from os import path
import sys
from typing import List

from cryptography.fernet import Fernet


class WordListHandler:
    """class that handles reading / decrypting files and writing new files"""

    def __init__(self, keyfile_path: str = "keyfile"):

        self.keyfile_path = keyfile_path
        if path.isfile(self.keyfile_path):
            with open(self.keyfile_path, 'rb') as keyfile:
                self.key = keyfile.read()
        else:
            print(f"warning, keyfile path {self.keyfile_path} is not present", file=sys.stderr)
            self.key = Fernet.generate_key()  # this is your "password"
            with open(self.keyfile_path, 'wb') as keyfile:
                keyfile.write(self.key)

        self.cipher_suite = Fernet(self.key)

    @staticmethod
    def read_file_lines(file_path: str) -> List[str]:
        """reads file at path and returns lines as a list of strings"""
        with open(file_path, 'r') as infile:
            return infile.readlines()

    @staticmethod
    def write_file_lines(lines: List[str], file_path: str) -> None:
        """writes list of strings as lines to file path"""
        with open(file_path, 'w') as outfile:
            outfile.writelines(lines)

    def decrypt_string(self, encrypted_string: str) -> str:
        """takes string (not bytes) and decrypts using your cypher. returns string"""
        return self.cipher_suite.decrypt(encrypted_string.encode()).decode()

    def encrypt_string(self, string: str) -> str:
        """takes regular string and encrypts using your cypher, returns string"""
        return self.cipher_suite.encrypt(string.encode()).decode()

    def read_and_decrypt_file(self, encrypted_file_path: str) -> List[str]:
        """read an encrypted file and return decrypted lines"""
        lines = WordListHandler.read_file_lines(encrypted_file_path)
        return [self.decrypt_string(line) for line in lines]

    def encrypt_and_write_lines(self, lines: List[str], outfile_path) -> None:
        """encrypt strings in lines and write to outfile path"""
        encrypted_lines = [self.encrypt_string(line) for line in lines]
        with open(outfile_path) as outfile:
            outfile.writelines(encrypted_lines)


def get_complete_path_of_file(filename):
    """Join the path of the current directory with the input filename."""
    root = path.abspath(path.dirname(__file__))
    return path.join(root, filename)


if __name__ == "__main__":  # decrypt
    decrypted_path = "profanity_wordlist.txt"
    encrypted_path = "profanity_wordlist_encrypted.txt"

    handler = WordListHandler()
