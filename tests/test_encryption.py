import pytest

from fast_censor.wordlist_file_handler import WordListHandler


@pytest.fixture
def word_list_handler() -> WordListHandler:
    return WordListHandler(keyfile_path='keyfile')


@pytest.mark.parametrize("string", ['hello', 'hi there', 'hi\nthere'])
def test_encrypt_decrypt(string: str, word_list_handler):
    assert word_list_handler.decrypt_string(word_list_handler.encrypt_string(string))
