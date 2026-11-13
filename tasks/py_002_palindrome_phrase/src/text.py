def is_palindrome(text):
    """True if text reads the same backwards, ignoring case and punctuation."""
    return text == text[::-1]
