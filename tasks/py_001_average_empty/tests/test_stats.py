import unittest

from src.stats import average


class AverageTests(unittest.TestCase):
    def test_regular_list(self):
        self.assertEqual(average([2, 4, 6]), 4)

    def test_single_value(self):
        self.assertEqual(average([5]), 5)

    def test_empty_list_returns_zero(self):
        self.assertEqual(average([]), 0.0)


if __name__ == "__main__":
    unittest.main()
