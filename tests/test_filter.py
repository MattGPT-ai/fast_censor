"""tests the primary functionality of the fast censor"""

import unittest

from fast_censor.profanity_check_trie import ProfanityTrie
from fast_censor.word_lists.locate import word_list_dir


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.profanity_filter = ProfanityTrie(wordlist=f"{word_list_dir}/clean_wordlist_decrypted.txt",
                                              wordlist_encrypted=False)

    def test_filter_word(self):
        res = self.profanity_filter.check_text("there fvdge fudgey  ri1i1i1liick  f_u_d_g_e cow swirl saa@ax crap")
        self.assertEqual(res, [(6, 11), (12, 17), (20, 32)])


if __name__ == "__main__":
    unittest.main()
