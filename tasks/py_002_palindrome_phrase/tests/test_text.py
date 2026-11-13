import unittest

from src.text import is_palindrome


class PalindromeTests(unittest.TestCase):
    def test_simple_word(self):
        self.assertTrue(is_palindrome("level"))

    def test_not_a_palindrome(self):
        self.assertFalse(is_palindrome("python"))

    def test_phrase_with_punctuation_and_case(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))


if __name__ == "__main__":
    unittest.main()
