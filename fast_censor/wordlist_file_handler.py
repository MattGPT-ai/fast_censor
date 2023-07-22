"""this module handles reading / writing and encoding / decoding files for word lists using the WordListHandler class"""

from base64 import b64encode, b64decode
from os import path
from sys import stderr
from typing import List, Generator


class WordListHandler:
    """Class that handles reading / decoding and writing / encoding word list files

    Attributes:
        debug: sets verbose output
    """

    def __init__(self, debug: bool = False):

        self.debug = debug

    def write_file_lines(self, lines: List[str], file_path: str, encode: bool = False) -> None:
        """Writes list of strings as lines to file path, separated by '\n'

        Args:
            encode: set to True to encode files so the profanity can not be directly read
            lines: list of string lines to be written to file
            file_path: output text file path
        """
        with open(file_path, 'w') as outfile:
            for line in lines:
                if encode:
                    line = self.encode_string(line)
                outfile.write(line)
                outfile.write('\n')

    @staticmethod
    def decode_string(encoded_string: str) -> str:
        """Takes string (not bytes) and decodes from base64.

        Returns:
             decoded string"""
        try:
            return b64decode(encoded_string.encode()).decode()
        except UnicodeDecodeError:
            print('Decoding failed! You may be trying to decode a file that is not encoded!'
                  'Try setting `wordlist_encoded = False` in FastCensor or WordListHandler!',
                  file=stderr)
            raise

    @staticmethod
    def encode_string(string: str) -> str:
        """Takes regular string and encodes using base64.
        Returns:
             encoded string"""
        return b64encode(string.encode()).decode()

    def read_wordlist_file(self, filename: str, decode: bool = False) -> Generator[str, None, None]:
        """Reads lines from wordlist file

        Args:
            filename: path to wordlist file
            decode: set to true if file is encoded

        Yields:
            words written in file
        """
        with open(filename) as wordlist_file:
            for line in wordlist_file:
                if line != "":
                    if decode:
                        line = self.decode_string(line)
                    yield line

    @staticmethod
    def get_path_of_package_file(filename: str) -> str:
        """Args:
            filename: just the filename of file included in package (see MANIFEST.in) - not including package directory
        Returns:
            path of package file matching filename"""
        word_list_dir = path.abspath(path.dirname(__file__))
        return path.join(word_list_dir, filename)

    @classmethod
    def get_default_wordlist_path(cls) -> str:
        """Get absolute path to wordlist file included in package
        Returns:
            path to wordlist file as string
        """
        return cls.get_path_of_package_file("word_lists/profanity_wordlist_encoded.txt")
