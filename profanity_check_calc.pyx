cimport cython
from typing import Dict, List
#cdef dict d = <dict>defaultdict(int)


cdef struct TrieNode:
    char val
    dict children
    str end_node_string


cdef class TrieNodeClass:
    def __init__(self, val: str):
        self.val: str = val
        self.children: Dict[str, List[TrieNode]] = dict()
        self.end_node_string: str = ''

    def __repr__(self):
        child_strings = []
        for key, value in self.children.items():
            child_strings.append(f"{key}->{''.join(child.val for child in value)}")
        return f"Node({self.val}) -> ({' '.join(child_strings)})"



cs = cython.struct(x=int, y=float)

cdef float test(cs z):
    cdef char c = 'h'
    return z.y

cpdef int dub(int x):
    cdef int a = 5
    c1 = cs(x, 1.0)
    return 2 * c1.x

cpdef char dict_test(dict d):
    return d['x']

# cdef char node_test(TrieNode tn):
#     return tn.val
