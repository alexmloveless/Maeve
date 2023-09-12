import unittest

class TestData(unittest.TestCase):

    def setUp(self):
        self.csvfile = "./data/spotify-2023-utf-8.csv"

    def test_load_csv(self):
        dfpd = None


if __name__ == '__main__':
    unittest.main()