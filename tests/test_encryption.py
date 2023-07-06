from unittest import TestCase
import unittest.main

from fast_censor.wordlist_file_handler import WordListHandler


class TestWordListHandler(TestCase):
    """Tests functionality of the wordlist file handler"""

    def setUp(self):
        """Initializes a default word list handler"""
        self.word_list_handler = WordListHandler(debug=True)

    def test_encode_decode(self):
        """Ensure that if you encode and decode a string, you get back the original string"""
        for string in ['hello', 'hi there', 'hi\nthere']:
            self.assertEqual(string, self.word_list_handler.decode_string(self.word_list_handler.encode_string(string)))


if __name__ == '__main__':
    unittest.main()
