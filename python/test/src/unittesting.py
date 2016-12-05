import unittest
import os

class BasicTest(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(2 + 2, 4)


class Operators(unittest.TestCase):
    def test_operators(self):
        self.assertEqual(5, 5)
        self.assertNotEqual(5, 7)
        #
        self.assertGreaterEqual(5, 5)
        self.assertGreater(5, 3)
        self.assertLess(3, 5)
        self.assertLessEqual(5, 5)
        #
        self.assertTrue(True)
        self.assertFalse(False)
        #
        self.assertIs(None, None)
        self.assertIsNot(5, None)
        self.assertIsNone(None)
        self.assertIsNotNone(5)
        #
        self.assertIsInstance(5, int)
        self.assertNotIsInstance(5, str)
        #
        self.assertIn(5, (3, 5, 7))
        self.assertNotIn(5, (2, 4, 6))
        self.assertCountEqual((1, 2, 3, 3), (3, 2, 3, 1))
        #
        with self.assertRaises(ValueError):
            raise ValueError


if __name__ == "__main__":
        unittest.main()
