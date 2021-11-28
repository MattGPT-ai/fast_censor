import os
from typing import Dict, List


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
        self.children: Dict[str, TrieNode] = {}
        self.end_node: bool = False

    def __repr__(self):
        return f"Node({self.val}) -> ({self.children.keys()})"


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
                nxt = pointer.children.get(c)
                if nxt is None:
                    nxt = TrieNode(c)
                    if self.debug:
                        print('created node', nxt)
                    chars = self.mapping.get(c)
                    if chars is None:
                        chars = tuple(c)
                    for char in chars:
                        pointer.children[char] = nxt
                        if self.debug:
                            print(f"set {pointer.val} node child {char} to {nxt.val}")
                pointer = nxt  # advance
            if pointer is not self.head_node:
                pointer.end_node = True

        if self.debug:
            # bfs
            nodes = [self.head_node]
            while nodes:
                new_nodes = set()
                for node in nodes:
                    print(node)
                    for child in node.children.values():
                        new_nodes.add(child)
                nodes = new_nodes

    def check_text(self, string: str) -> int:
        pointers: List[TrieNode] = []
        string = string.lower()
        profanity_counter = 0

        # iterate over each character in string
        for c in string:
            new_pointers = []
            if self.debug:
                print('pointers:', pointers)
            for pointer in pointers:
                if c in pointer.children:
                    new_pointer = pointer.children[c]
                    if new_pointer.end_node:
                        profanity_counter += 1
                        if self.debug:
                            print('word found terminating with', c)
                    else:
                        if self.debug:
                            print('appending pointer', new_pointer.val)
                        new_pointers.append(new_pointer)  # advance
                # allow additional repeated characters after all repetitions have been traversed
                elif c == pointer.val or \
                        (pointer.val in ProfanityTrie.CHARS_MAP_SETS and c in ProfanityTrie.CHARS_MAP_SETS[pointer.val]):
                    new_pointers.append(pointer)  # don't advance
                # else pointer is not continued

            pointers = new_pointers  # advance all

            if c in self.head_node.children:
                pointers.append(self.head_node.children[c])

        return profanity_counter


if __name__ == '__main__':
    pf = ProfanityTrie(words=['test', 'sax', 'vup'], debug=False)
    pf = ProfanityTrie()
    print(pf.check_text("there fuvuudge saa@ax vap" * 50))
