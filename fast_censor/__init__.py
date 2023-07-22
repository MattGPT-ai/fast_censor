from . import profanity_check_trie
from . import wordlist_file_handler
from .profanity_check_trie import FastCensor
from .wordlist_file_handler import WordListHandler


__all__ = [
    "__title__", "__summary__", "__uri__", "__version__",
    "__author__", "__email__", "__license__", "__copyright__",
]

__title__ = "ProfanityTrie"
__summary__ = "quickly filter profanity from text"
__uri__ = ""

__version__ = "0.3.0"
__build__ = ""

__author__ = "Matt Buchovecky (mbuchove)"
__email__ = "mbuchove@gmail.com"

__license__ = ""
__copyright__ = "Copyright 2022"
