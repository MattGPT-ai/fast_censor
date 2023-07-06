"""Profanity check Trie
this class uses the Trie data structure to more efficiently detect and filter out profanity from a text"""

from os.path import expanduser
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Union, Optional, Generator, Collection

from fast_censor.wordlist_file_handler import WordListHandler


class TrieNode:
    """a node in the trie data structure
    contains a char value, pointers to its children by char, and a flag """

    def __init__(self, val: str):
        """each node value should be a char"""
        self.val: str = val  # character value
        self.children: Dict[str, List[TrieNode]] = defaultdict(list)
        self.end_node_string: str = ''  # None may be more appropriate

    def __repr__(self):
        """prints out a node value and its child chars"""
        child_strings = []
        for key, value in self.children.items():
            child_strings.append(f"{key}->{''.join(child.val for child in value)}")
        return f"Node({self.val}) -> ({' '.join(child_strings)})"


class FastCensor:
    """this is the main class that is used for finding matches of words that are to be filtered"""

    # character substitutions that will still register, e.g. leet (1337) speak
    CHARS_MAPPING = {
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

    default_delimiters = set(" \t\n_.,")  # characters that signal the end of a word, default

    def is_delimiter(self, char: str) -> bool:
        """tells you if a character is a delimiter which separates words"""
        return char in self.delimiters

    def set_delimiters(self, delimiters: Union[Set[str], str, List[str]]):
        """set delimiters that determine the boundaries of words for finding matches"""
        if delimiters is None:
            self.delimiters = FastCensor.default_delimiters
        else:
            self.delimiters = {delim for delim in delimiters}

    def __init__(
        self,
        words: Optional[Collection[str]] = None,  # overrides wordlist
        wordlist: Optional[str] = WordListHandler.get_default_wordlist_path(),
        wordlist_encoded: bool = True,  # toggle this to decode word file
        mapping: Optional[Dict[str, Collection[str]]] = None,
        delimiters: Union[Set, str] = None,
        strip: Optional[str] = None,  # None strips default whitespace, empty string doesn't strip, else strip chars in value
        keep_word_set: bool = True,
        censor_char: str = "*",
        debug: bool = False,
    ):
        """requires: words or wordlist
        words - set of words to be filtered
        wordlist - path to wordlist file
        mapping - maps char (str) value to set of valid substitutions
        delimiters - characters that separate words, whitespace by default
        """

        self.strip = strip
        self.debug = debug
        self.delimiters = None
        self.set_delimiters(delimiters)
        self.censor_char = censor_char

        self.mapping: Dict = FastCensor.CHARS_MAPPING if mapping is None else mapping
        self.word_file_handler = WordListHandler()

        # save word set for quick writing
        self.words: Set[str] = set()
        if words is None:
            if wordlist:
                words = set(self.word_file_handler.read_wordlist_file(expanduser(wordlist),
                                                                      decode=wordlist_encoded))
            else:
                raise ValueError("must provide either wordlist or words!")
        if self.debug:
            print(f"processing {len(self.words)} words")

        self.keep_word_set = keep_word_set
        self.words = None

        self.head_node: Optional[TrieNode] = None
        self.build_trie(words)

    def add_word(self, word: str) -> Optional[TrieNode]:
        """adds word to trie structure and set of words"""

        word = word.strip(self.strip)

        if not word:
            return

        if self.words is not None:
            self.words.add(word)

        # add word to trie
        pointer = self.head_node
        for c in word.lower():
            # find next
            c_children = pointer.children.get(c)
            if c_children is None:
                nxt = TrieNode(c)
                if self.debug:
                    print('created node', nxt)
                chars = self.mapping.get(c)
                if chars is None:
                    chars = tuple(c)
                for char in chars:
                    pointer.children[char].append(nxt)
                    if self.debug:
                        print(f"set {pointer.val} node child {char} to {nxt.val}")
            else:  # character already
                for child in c_children:
                    if child.val == c:
                        nxt = child
                        break
                else:  # character does not yet lead to
                    c_children.append(TrieNode(c))
                    nxt = c_children[-1]
            pointer = nxt  # advance
        if pointer is not self.head_node:
            if self.debug and pointer.end_node_string:
                print('already ends', pointer.end_node_string)
            pointer.end_node_string = word
            return pointer

    def build_trie(self, words: Union[Set[str], List[str]]):
        """build the trie structure and populate it with words"""

        if self.keep_word_set:
            self.words = set()

        # the primary data structure is a Trie
        self.head_node = TrieNode('')

        # populate trie with list of words, incorporating mapping
        while len(words) > 0:
            word = words.pop()
            self.add_word(word)

        if self.debug:
            self.bfs()

    def bfs(self):
        """breadth-first-search and print nodes for debugging"""
        nodes = [self.head_node]
        while nodes:
            new_nodes = set()
            for node in nodes:
                print(node)
                for child in node.children.values():
                    new_nodes.update(child)
            nodes = new_nodes

    def get_words(self) -> Generator[str, None, None]:
        """Performs a depth-first-search of trie and yields words"""
        node_stack = [self.head_node]
        while len(node_stack) > 0:
            node = node_stack.pop()
            for child in node.children.values():
                node_stack.extend(child)
            if node.end_node_string:
                yield node.end_node_string

    def has_word(self, word: str) -> bool:
        """Returns True if word is in trie, else False"""
        return word in self.words

    def check_text(self, string: str, allow_repetitions: bool = True) -> List[Tuple[int, int]]:
        """Checks the given string for instances of profane words matching the word list
        returns list of index spans of matches"""

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
            if self.debug:
                print('pointers:', pointers)
            for pointer, length in pointers:
                if c in pointer.children:
                    for new_pointer in pointer.children[c]:
                        if new_pointer.end_node_string:
                            profanity_matches.append((i - length, i + 1))
                            if self.debug:
                                print(new_pointer.end_node_string, 'found')
                        else:
                            if self.debug:
                                print('appending pointer', new_pointer.val)
                        new_pointers.add((new_pointer, length+1))  # advance
                # allow additional repeated characters after all repetitions have been traversed
                if allow_repetitions and (c == pointer.val or
                                          (pointer.val in self.mapping and c in
                                           self.mapping[pointer.val])):
                    new_pointers.add((pointer, length+1))  # don't advance
                # else pointer is not continued

            pointers = new_pointers  # advance all

        return profanity_matches

    def censor_text(self, text: str) -> str:
        """returns string with all profanity matches replaced with `censor_char`"""
        text_list = list(text)
        matches = self.check_text(text)
        for i, j in matches:
            text_list[i:j+1] = self.censor_char * (j - i)
        return ''.join(text_list)

    def text_has_match(self, text: str):
        """returns True if text contains any profanity instances"""
        match_iterator = ProfanityMatchIterator(self, text)
        try:
            next(match_iterator)
        except StopIteration:
            return False
        return True

    def get_matches(self, text: str):
        return list({match for match in ProfanityMatchIterator(self, text)})

    def write_words_file(self, outfile_path: str, encode: bool = True):
        """write the wordlist file to specified path
        if encode is set to True (default), each line in the file will be encoded"""
        sorted_words = sorted(self.words)
        self.word_file_handler.write_file_lines(sorted_words, outfile_path, encode)


class ProfanityMatchIterator:
    """used for yielding matches"""

    def __init__(self, trie: FastCensor, string: str, allow_repetitions: bool = True):
        self.trie: FastCensor = trie
        self.string: str = string
        self.allow_repetitions: bool = allow_repetitions
        self.pointers: Set[Tuple] = set()  # tuple of pointer to node and match length
        self.word_start: bool = True
        self.i: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        word_start = True
        while self.i < len(self.string):
            c = self.string[self.i]
            if self.trie.is_delimiter(c):
                word_start = True
                pointers = set()
            elif word_start and c in self.trie.head_node.children:
                pointers.update((child, 1) for child in self.trie.head_node.children[c])
                word_start = False
                continue
            new_pointers = set()
            if self.trie.debug:
                print('pointers:', pointers)
            for pointer, length in pointers:
                if c in pointer.children:
                    for new_pointer in pointer.children[c]:
                        if new_pointer.end_node_string:
                            yield
                        new_pointers.add((new_pointer, length+1))  # advance
                # allow additional repeated characters after all repetitions have been traversed
                if self.allow_repetitions and (c == pointer.val or
                                          (pointer.val in self.trie.mapping and c in
                                           self.trie.mapping[pointer.val])):
                    new_pointers.add((pointer, length+1))  # don't advance
                # else pointer is not continued

            pointers = new_pointers  # advance all


if __name__ == '__main__':

    # pf = ProfanityTrie(words=['test', 'sax', 'vup'], debug=True)
    pf = FastCensor(wordlist="word_lists/clean_wordlist_decoded.txt", wordlist_encoded=False,
                    delimiters={' ', '\t'})
    print(pf.check_text("there fuvuudge fvu*dge ri1i1i1liick lady cow f_u_d_g_e saa@ax vap crap" * 50))
    pf.add_word('newword')
    print(pf.check_text("there fvdge fudgey  ri1i1i1liick  f_u_d_g_e cow swirl saa@ax crap newword"))
    pf.write_words_file("word_lists/clean_wordlist_encoded.txt", encode=True)
    print(list(pf.words))

    pf = FastCensor(wordlist="word_lists/profanity_wordlist_encoded.txt", wordlist_encoded=True)
    #pf.text_has_match()
    #pf.get_matches()
    #h = WordListHandler()
