"""Tests the primary functionality of the fast censor"""

from unittest import TestCase
import unittest.main

from fast_censor.profanity_check_trie import FastCensor


class TestFilter(TestCase):
    def setUp(self):
        """Instantiate the FastCensor object with the decoded short clean wordlist for easier debugging"""
        self.profanity_filter = FastCensor(wordlist="../fast_censor/word_lists/clean_wordlist_decoded.txt",
                                           wordlist_encoded=False, censor_chars="*")

    def test_filter_word(self):
        """Check that the proper profanity matches are found within a string"""
        res = self.profanity_filter.check_text("there fvdge fudgey  ri1i1i1liick  f_u_d_g_e cow swirl saa@ax crap")
        self.assertEqual(res, [(6, 11), (12, 17), (20, 32)])

    def test_no_profanity(self):
        """Checks that a string with no profanity returns an empty list"""
        self.assertEqual(self.profanity_filter.check_text("The quick brown fox jumped over the lazy dog"), [])

    def test_long_text(self):
        """tests that the censored text of a long text is correct"""
        long_text = "oh fuudge  " * 100
        self.assertEqual(self.profanity_filter.censor_text(long_text), "oh ******  " * 100)


if __name__ == "__main__":
    unittest.main()
