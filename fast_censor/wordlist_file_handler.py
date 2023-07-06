"""this class handles reading / writing and encoding / decoding files for word lists"""

from base64 import b64encode, b64decode
from os import path
from sys import stderr
from typing import List, Generator


class WordListHandler:
    """class that handles reading / decoding and writing / encoding word list files"""

    def __init__(self, debug: bool = False):

        self.debug = debug

    def write_file_lines(self, lines: List[str], file_path: str, encode: bool = False) -> None:
        """writes list of strings as lines to file path"""
        with open(file_path, 'w') as outfile:
            for line in lines:
                if encode:
                    line = self.encode_string(line)
                outfile.write(line)
                outfile.write('\n')

    @staticmethod
    def decode_string(encoded_string: str) -> str:
        """takes string (not bytes) and decodes from base64. returns string"""
        try:
            return b64decode(encoded_string.encode()).decode()
        except UnicodeDecodeError:
            print('Decoding failed! You may be trying to decode a file that is not encoded!'
                  'Try setting `wordlist_encoded = False` in FastCensor or WordListHandler!',
                  file=stderr)
            raise

    @staticmethod
    def encode_string(string: str) -> str:
        """takes regular string and encodes using base64, returns string"""
        return b64encode(string.encode()).decode()

    def read_wordlist_file(self, filename: str, decode: bool = False) -> Generator[str, None, None]:
        """Return words from a wordlist file."""
        with open(filename) as wordlist_file:
            for line in wordlist_file:
                if line != "":
                    if decode:
                        line = self.decode_string(line)
                    yield line

    @staticmethod
    def get_complete_path_of_file(filename: str) -> str:
        """Join the path of the current directory with the input filename."""
        root = path.abspath(path.dirname(__file__))
        return path.join(root, filename)

    @classmethod
    def get_default_wordlist_path(cls) -> str:
        """returns absolute path to wordlist file included in package"""
        return cls.get_complete_path_of_file("word_lists/profanity_wordlist_encoded.txt")
