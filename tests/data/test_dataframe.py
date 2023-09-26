import unittest
from maeve import Session

class TestData(unittest.TestCase):

    def setUp(self):
        self.me = Session(conf="../tests/conf/basic_org_conf.hjson", log_level="DEBUG")

    def test_load_csv(self):
        df = self.me.cook("TestNoPipeline")


if __name__ == '__main__':
    unittest.main()