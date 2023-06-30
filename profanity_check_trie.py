import os
from collections import defaultdict
from typing import Dict, List, Set, Tuple


def read_wordlist(filename: str):
    """Return words from a wordlist file."""
    with open(filename, encoding="utf-8") as wordlist_file:
        for row in iter(wordlist_file):
            row = row.strip()
            if row != "":
                yield row


def get_complete_path_of_file(filename):
    """Join the path of the current directory with the input filename."""
    root = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(root, filename)


class TrieNode:
    def __init__(self, val: str):
        """each node value should be a char"""
        self.val: str = val
        self.children: Dict[str, List[TrieNode]] = defaultdict(list)
        self.end_node_string: str = ''

    def __repr__(self):
        child_strings = []
        for key, value in self.children.items():
            child_strings.append(f"{key}->{''.join(child.val for child in value)}")
        return f"Node({self.val}) -> ({' '.join(child_strings)})"


class ProfanityTrie:

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

    delimiters = set(" \t\n_.,")  # characters that signal the end of a word, default

    def is_delimiter(self, char: str) -> bool:
        """"""
        return char in self.delimiters

    def set_delimiters(self, delimiters):
        if delimiters is None:
            self.delimiters = ProfanityTrie.delimiters
        else:
            self.delimiters = {delim for delim in delimiters}

    def __init__(self, words=None, wordlist="profanity_wordlist.txt", mapping: dict = None, debug: bool=False,
                 delimiters: Union[Set, str] = None):
        """requires: words or wordlist
        words - set of words to be filtered
        wordlist - path to wordlist file
        mapping - maps string value to set of valid substitutions
        delimiters - characters that separate words, typically whitespace"""

        self.debug = debug
        self.mapping: dict = ProfanityTrie.CHARS_MAPPING if mapping is None else mapping
        self.words: list = words
        if self.words is None:
            if wordlist:
                self.words = list(read_wordlist(os.path.expanduser(wordlist)))
            else:
                raise ValueError("must provide either wordlist or words")
        self.set_delimiters(delimiters)
        if self.debug:
            print(f"processing {len(self.words)} words")

        # the primary data structure is a Trie
        self.head_node: TrieNode = TrieNode('')
        self.build_trie()

    def build_trie(self):

        # the primary data structure is a Trie
        self.head_node = TrieNode('')

        # populate trie with list of words, incorporating mapping
        for word in self.words:
            if not word:
                continue
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
                    print('already endz', pointer.end_node_string)
                pointer.end_node_string = word

        if self.debug:
            # breadth-first search
            nodes = [self.head_node]
            while nodes:
                new_nodes = set()
                for node in nodes:
                    print(node)
                    for child in node.children.values():
                        new_nodes.update(child)
                nodes = new_nodes

    def check_text(self, string: str, allow_repetitions: bool = True) -> List[Tuple[int, int]]:
        """checks the given string for instances of profane words matching the word list
        returns list of index spans of matches"""

        pointers: Set[Tuple] = set()  # tuple of pointer to node and match length
        string = string.lower()  # case-insensitive matching
        profanity_matches = []
        new_text = list(string)  # censored text

        # iterate over each character in string and check for matches
        word_start = True
        for i, c in enumerate(string):
            if self.is_delimiter(c):
                word_start = True
                pointers = set()
                #pointers = set(pointer for pointer in pointers if pointer.val == c)
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
                            new_text[i-length:i+1] = \
                                '*' * (length+1)
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
        if self.debug:
            print('censored:\t', ''.join(new_text))

        return profanity_matches

    def text_has_match(self, text: str):
        match_iterator = MatchIterator(self, text)
        try:
            next(match_iterator)
        except StopIteration:
            return False
        return True

    def get_matches(self, text: str):
        return list({match for match in MatchIterator(self, text)})


class MatchIterator():  # collections.Iterator
    def __init__(self, trie: ProfanityTrie, string: str, allow_repetitions: bool = True):
        self.trie: ProfanityTrie = trie
        self.string: str = string
        self.allow_repetitions: bool = allow_repetitions
        self.pointers: Set[Tuple] = set()  # tuple of pointer to node and match length
        self.word_start: bool = True
        self.i: int = 0

    def __next__(self):
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

    pf = ProfanityTrie(words=['test', 'sax', 'vup'], debug=False)
    #pf = ProfanityTrie(debug=True)
    pf = ProfanityTrie(debug=True, delimiters={' ', '\t'}, wordlist="clean_wordlist_decrypted.txt")
    print(pf.check_text("there fuvuudge fvu*dge ri1i1i1liick lady cow f_u_d_g_e saa@ax vap crap" * 50))
