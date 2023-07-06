"""tests the primary functionality of the fast censor"""

from unittest import TestCase
import unittest.main

from fast_censor.profanity_check_trie import FastCensor
from fast_censor.word_lists.locate import word_list_dir


class TestFilter(TestCase):
    def setUp(self):
        self.profanity_filter = FastCensor(wordlist=f"{word_list_dir}/clean_wordlist_decoded.txt",
                                           wordlist_encoded=False)

    def test_filter_word(self):
        res = self.profanity_filter.check_text("there fvdge fudgey  ri1i1i1liick  f_u_d_g_e cow swirl saa@ax crap")
        self.assertEqual(res, [(6, 11), (12, 17), (20, 32)])


if __name__ == "__main__":
    unittest.main()
