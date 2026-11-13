def is_palindrome(text):
    """True if text reads the same backwards, ignoring case and punctuation."""
    cleaned = [ch.lower() for ch in text if ch.isalnum()]
    return cleaned == cleaned[::-1]
