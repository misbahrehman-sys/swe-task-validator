import unittest

from src.lists import chunk


class ChunkTests(unittest.TestCase):
    def test_even_split(self):
        self.assertEqual(chunk([1, 2, 3, 4], 2), [[1, 2], [3, 4]])

    def test_last_group_is_kept(self):
        self.assertEqual(chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])

    def test_size_larger_than_list(self):
        self.assertEqual(chunk([1, 2], 5), [[1, 2]])


if __name__ == "__main__":
    unittest.main()
