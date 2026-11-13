def chunk(items, size):
    """Split items into groups of at most `size`, keeping every item."""
    return [items[i:i + size] for i in range(0, len(items), size)]
