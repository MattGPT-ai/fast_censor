import os
from collections import defaultdict
from typing import Dict, List, Set


def read_wordlist(filename: str):
    """Return words from a wordlist file."""
    with open(filename, encoding="utf-8") as wordlist_file:
        for row in iter(wordlist_file):
            row = row.strip()
            if row != "":
                #print(row)
                yield row


class TrieNode:
    def __init__(self, val: str):
        self.val: str = val
        self.children: Dict[str, List[TrieNode]] = defaultdict(list)
        self.end_node: str = ''

    def __repr__(self):
        child_strings = []
        for key, value in self.children.items():
            child_strings.append(f"{key}->{''.join(child.val for child in value)}")
        return f"Node({self.val}) -> ({' '.join(child_strings)})"


class ProfanityTrie:

    CHARS_MAPPING = {
        "a": ("a", "@", "*", "4"),
        "i": ("i", "*", "l", "1"),
        "o": ("o", "*", "0", "@"),
        "u": ("u", "*", "v"),
        "v": ("v", "*", "u"),
        "l": ("l", "1"),
        "e": ("e", "*", "3"),
        "s": ("s", "$", "5"),
        "t": ("t", "7"),
    }
    CHARS_MAP_SETS = {key: set(value) for key, value in CHARS_MAPPING.items()}

    wordlist = "~/opt/anaconda3/envs/ziprecruiter/lib/python3.8/site-packages/better_profanity/profanity_wordlist.txt"

    separators = " \t_.,\n"

    @staticmethod
    def is_separator(char: str) -> bool:
        return char in ProfanityTrie.separators

    def __init__(self, words=None, mapping: dict = None, debug=False):
        self.debug = debug
        self.mapping = mapping
        self.mapping: dict = ProfanityTrie.CHARS_MAPPING if mapping is None else mapping
        self.words = words
        if self.words is None:
            self.words: list = list(read_wordlist(os.path.expanduser(ProfanityTrie.wordlist)))
        if self.debug:
            print(f"processing {len(self.words)} words")

        # the primary data structure is a Trie
        self.head_node: TrieNode = TrieNode('')

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
                pointer.end_node = word

        if self.debug:
            # bfs
            nodes = [self.head_node]
            while nodes:
                new_nodes = set()
                for node in nodes:
                    print(node)
                    for child in node.children.values():
                        new_nodes.update(child)
                nodes = new_nodes

    def check_text(self, string: str, allow_repititions: bool = True) -> int:
        pointers: Set[TrieNode] = set()
        string = string.lower()
        profanity_counter = 0

        # iterate over each character in string
        word_start = True
        for c in string:
            if ProfanityTrie.is_separator(c):
                word_start = True
                pointers = set()
            elif word_start and c in self.head_node.children:
                pointers.update(self.head_node.children[c])
                word_start = False
                continue
            new_pointers = set()
            if self.debug:
                print('pointers:', pointers)
            for pointer in pointers:
                if c in pointer.children:
                    for new_pointer in pointer.children[c]:
                        if new_pointer.end_node:
                            profanity_counter += 1
                            if self.debug:
                                print(new_pointer.end_node, 'found')
                        else:
                            if self.debug:
                                print('appending pointer', new_pointer.val)
                        new_pointers.add(new_pointer)  # advance
                # allow additional repeated characters after all repetitions have been traversed
                if allow_repititions:
                    if c == pointer.val or \
                            (pointer.val in ProfanityTrie.CHARS_MAP_SETS and c in ProfanityTrie.CHARS_MAP_SETS[pointer.val]):
                        new_pointers.add(pointer)  # don't advance
                # else pointer is not continued

            pointers = new_pointers  # advance all

        return profanity_counter


if __name__ == '__main__':

    pf = ProfanityTrie(words=['test', 'sax', 'vup'], debug=False)
    pf = ProfanityTrie(debug=True)
    print(pf.check_text("there fuvuudge fvu*dge ri1i1i1liick saa@ax vap" * 50))
