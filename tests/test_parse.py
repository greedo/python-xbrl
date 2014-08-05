import os
from unittest import TestCase
import sys
sys.path.insert(0, os.path.abspath('..'))

from parser import soup_maker, XBRLParser

class TestParse(TestCase):

        def testEmptyFile(self):
                self.assertRaises(XBRLParserException, XBRLParser.parse, fh)

        #def test_parse(self):
        # make sure the shuffled sequence does not lose any elements


if __name__ == '__main__':
    unittest.main()

