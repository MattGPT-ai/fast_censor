"""This module includes the FastCensor class, which is implemented with a Trie data structure
It also contains the TrieNode class that builds the profanity Trie, and a match iterator class
the FastCensor class uses the Trie data structure to more efficiently detect and filter out profanity from a text"""

import logging
from collections import defaultdict
from math import ceil
from os.path import expanduser
from typing import Dict, List, Set, Tuple, Union, Optional, Generator, Collection, Callable

from fast_censor.wordlist_file_handler import WordListHandler


class TrieNode:
    """A node in the trie data structure.
    Contains a char value, pointers to its children by char, and a flag.

    Args:
        val: the char value of the node - pre-substitution

    Attributes:
        children: dict that maps a char to a list of connected child nodes
        end_node_string: if this is a non-empty string, the node represents a match
    """

    def __init__(self, val: str):
        """Constructor class for TrieNode

        Args:
            val: char value of the node
        """
        self.val: str = val  # character value
        self.children: Dict[str, List[TrieNode]] = defaultdict(list)
        self.end_node_string: str = ''  # None may be more appropriate

    def __repr__(self) -> str:
        """Returns a string of node's value and its child chars"""
        child_strings = []
        for key, value in self.children.items():
            child_strings.append(f"{key}->{''.join(child.val for child in value)}")
        return f"Node({self.val}) -> ({' '.join(child_strings)})"


class FastCensor:
    """This is the main class that is used for filtering (censoring) and finding profanity matches in text
    requires: words or wordlist

    Args:
        words: set of words to be filtered - overrides wordlist
        wordlist: path to wordlist file, is set by default to encoded profanity list included in package
        wordlist_encoded: boolean that specifies if the provided wordlist is encoded so the file handler decodes lines
        substitutions: maps char (str) value to set of valid substitutions, like 1337code
        delimiters: characters that separate words, whitespace by default
        strip: None strips default whitespace, empty string doesn't strip, else strip chars in value when adding a word
        censor_chars: string that is to replace censored words. the sequence will repeat cyclically
        debug: boolean - set True to use verbose output
    """

    # character substitutions that will still register, e.g. leet (1337) speak
    CHAR_SUBSTITUTIONS = {
        "a": {"a", "@", "*", "4"},  # 'a' can be substituted with '@', '*', '4'
        "i": {"i", "*", "l", "1"},
        "o": {"o", "*", "0", "@"},
        "u": {"u", "*", "v"},
        "v": {"v", "*", "u"},
        "l": {"l", "1"},
        "e": {"e", "*", "3"},
        "s": {"s", "$", "5"},
        "t": {"t", "7"},
    }

    default_delimiters = set(" \t\n_.,;:")  # characters that signal the boundaries of a word, default

    def __init__(
        self,
        wordlist: Optional[str] = WordListHandler.get_default_wordlist_path(),
        wordlist_encoded: bool = True,  # toggle this to decode word file
        words: Union[List[str], Tuple[str], Set[str]] = None,  # overrides wordlist
        substitutions: Optional[Dict[str, Collection[str]]] = None,
        delimiters: Union[Set, str] = None,
        strip: Optional[str] = None,
        censor_chars: str = "*#&@",
        debug: bool = False,
    ):

        self.strip = strip
        self.delimiters = None
        self.set_delimiters(delimiters)
        self._censor_chars = censor_chars

        self.debug: bool = debug
        self.logger = logging.getLogger(__name__)
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

        self.substitution_map = None
        self.set_substitutions(FastCensor.CHAR_SUBSTITUTIONS if substitutions is None else substitutions)
        self.word_file_handler: WordListHandler = WordListHandler()

        # save word set for quick writing
        self.words: Set[str] = set()
        if words is None:
            if wordlist:
                words = set(self.word_file_handler.read_wordlist_file(expanduser(wordlist),
                                                                      decode=wordlist_encoded))
            else:
                raise ValueError("must provide either wordlist or words!")
        self.logger.debug(f"processing {len(self.words)} words")

        self.head_node: Optional[TrieNode] = None
        self.build_trie(words)

    def is_delimiter(self, char: str) -> bool:
        """
        Tells you if a character is a delimiter, which separates words when doing matching

        Args:
            char: character to check if it is a delimiter

        Returns:
            boolean stating whether provided char is a delimiter character
        """
        return char in self.delimiters

    def set_delimiters(self, delimiters: Union[Set[str], str, List[str]]) -> None:
        """
        Set delimiters that determine the boundaries of words for finding matches

        Args:
            delimiters: a collection of characters (str) that are to be considered delimiters
        """
        if delimiters is None:
            self.delimiters = FastCensor.default_delimiters
        else:
            self.delimiters = {delim for delim in delimiters}  # use set for quick access

    def get_delimiters(self) -> Set[str]:
        """Returns:
            set of delimiter chars
        """
        return self.delimiters

    def get_logger(self) -> logging.Logger:
        return self.logger

    def set_substitutions(self, substitutions: Dict[str, Collection[str]]) -> None:
        """preprocesses character substitutions and sets in FastCensor instance"""
        self.substitution_map = {}
        for char, subs in substitutions.items():
            subs = set(subs)
            if char not in subs:
                subs.add(char)
            if len(subs) <= 2:  # set only becomes more efficient with more than 2 characters
                subs = ''.join(subs)
            self.substitution_map[char] = subs
        self.substitution_map = substitutions

    def set_censor_chars(self, censor_chars: Union[str, List[str]]) -> None:
        self._censor_chars = censor_chars

    def add_word(self, word: str) -> Optional[TrieNode]:
        """Adds word to trie structure and set of words

        word: string to add to trie.

        Returns: added node if word is added, else None"""

        word = word.strip(self.strip)

        if not word:
            return

        # add word to trie
        pointer = self.head_node
        for c in word.lower():
            # find next
            c_children = pointer.children.get(c)
            if c_children is None:
                # create new node
                nxt = TrieNode(c)
                self.logger.debug(f'created node: ({nxt})')
                chars = self.substitution_map.get(c, c)
                for char in chars:
                    pointer.children[char].append(nxt)
                    self.logger.debug(f"set {pointer.val} node child {char} to {nxt.val}")
            else:  # character already a child of this node
                for child in c_children:
                    if child.val == c:
                        nxt = child
                        break
                else:  # character does not yet lead to
                    c_children.append(TrieNode(c))
                    nxt = c_children[-1]
            pointer = nxt  # advance
        if pointer is not self.head_node:
            if pointer.end_node_string:
                self.logger.debug(f'word "{pointer.end_node_string}" already ends on this node!')
            pointer.end_node_string = word
            return pointer

    def add_words(self, words: Collection[str]) -> None:
        """add list of words

        Args:
            words: Collection of words, such as list, tuple, set, etc. of strings
        """
        for word in words:
            self.add_word(word)

    def build_trie(self, words: Union[Set[str], List[str]]) -> TrieNode:
        """Builds the trie structure and populate it with words

        Args:
            words: Collection of string words to be added to trie

        Returns:
            the head node
        """

        # the primary data structure is a Trie
        self.head_node = TrieNode('')

        # populate trie with list of words, incorporating mapping
        while len(words) > 0:
            word = words.pop()
            self.add_word(word)

        if self.debug:
            self.bfs(self.logger.debug)

        return self.head_node

    def get_trie(self) -> TrieNode:
        """Returns:
            the head node"""
        return self.head_node

    def bfs(self, print_func: Callable = print):
        """breadth-first-search and print nodes for debugging.
        defaults to print, or you can provide it with e.g. self.logger.info"""
        nodes = [self.head_node]
        while nodes:
            new_nodes = set()
            for node in nodes:
                print_func(node)
                for child in node.children.values():
                    new_nodes.update(child)
            nodes = new_nodes

    def get_words(self) -> Generator[str, None, None]:
        """Performs a depth-first-search of trie and yields words"""
        visited_nodes = {self.head_node, }
        node_stack = [self.head_node, ]
        while len(node_stack) > 0:
            node = node_stack.pop()
            visited_nodes.add(node)
            for child_list in node.children.values():
                for child in child_list:
                    if child not in visited_nodes:
                        node_stack.append(child)
                        visited_nodes.add(child)
            if node.end_node_string:
                yield node.end_node_string

    def has_word(self, word: str) -> bool:
        """Returns True if word is in trie, else False.
        Only checks for the original value of the word, without substitutions or repetitions"""
        node = self.head_node
        for c in word:
            if c in node.children:
                node = node.children[c]
            else:
                return False
        return node.end_node_string == word

    def check_text(self, string: str, allow_repetitions: bool = True) -> List[Tuple[int, int]]:
        """Checks the given string for instances of profane words matching the word list
        Args:
            string: the string to check for profanity matches
            allow_repetitions: a single character or its substitutions can be repeated any number of times and still,
                                e.g. caaaaaaat would match cat

        Returns:
             list of index spans of matches, represented as tuples of start and end index"""

        pointers: Set[Tuple] = set()  # tuple of pointer to node and match length
        string = string.lower()  # case-insensitive matching
        profanity_matches = []

        # iterate over each character in string and check for matches
        word_start = True
        for i, c in enumerate(string):
            if self.is_delimiter(c):
                word_start = True
                pointers = set()
            elif word_start and c in self.head_node.children:
                pointers.update((child, 1) for child in self.head_node.children[c])
                word_start = False
                continue
            new_pointers = set()
            self.logger.debug('pointers:', pointers)
            for pointer, length in pointers:
                if c in pointer.children:
                    for new_pointer in pointer.children[c]:
                        if new_pointer.end_node_string:
                            profanity_matches.append((i - length, i + 1))
                            self.logger.debug(f'"{new_pointer.end_node_string}" found')
                        else:
                            if self.debug:
                                self.logger.debug('appending pointer', new_pointer.val)
                        new_pointers.add((new_pointer, length + 1))  # advance
                # allow additional repeated characters after all repetitions have been traversed
                if allow_repetitions and (c == pointer.val or
                                          (pointer.val in self.substitution_map and c in
                                           self.substitution_map[pointer.val])):
                    new_pointers.add((pointer, length + 1))  # don't advance
                # else pointer is not continued

            pointers = new_pointers  # advance all

        return profanity_matches

    def censor_text(self, text: str, allow_repetitions: bool = True) -> str:
        """returns string with all profanity matches replaced with `censor_char`"""
        text_list = list(text)
        matches = self.check_text(text, allow_repetitions)
        censor_string = self._censor_chars * ceil(sum(j - i for i, j in matches) / len(self._censor_chars))
        idx = 0  # starting point in censor string
        for i, j in matches:
            text_list[i:j] = censor_string[idx:idx + j - i]
            idx += j - i
        return ''.join(text_list)

    def write_words_file(self, outfile_path: str, encode: bool = True):
        """write the wordlist file to specified path
        if encode is set to True (default), each line in the file will be encoded"""
        sorted_words = sorted(self.get_words())
        self.word_file_handler.write_file_lines(sorted_words, outfile_path, encode)


if __name__ == '__main__':

    censor = FastCensor(wordlist="word_lists/clean_wordlist_decoded.txt", wordlist_encoded=False,
                        delimiters=" \t,")
    print(censor.check_text("there fuvuudge fvu*dge ri1i1i1liick lady cow f_u_d_g_e saa@ax vap crap" * 50))
    censor.add_word('newword')
    print(censor.check_text("there fvdge fudgey  ri1i1i1liick  f_u_d_g_e cow swirl saa@ax crap newword"))
    censor.write_words_file("word_lists/clean_wordlist_encoded.txt", encode=True)
    print(list(censor.get_words()))
    print(censor.censor_text("fuudge there is a b@t over there"))

    pf = FastCensor(wordlist="word_lists/profanity_wordlist_encoded.txt", wordlist_encoded=True)
