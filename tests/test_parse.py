
import os
from unittest import TestCase
import sys
sys.path.insert(0, os.path.abspath('..'))

from parse import XBRLParser
#from xbrlparse.xbrlparse import OfxFile, OfxPreprocessedFile, OfxParserException, soup_maker


class TestParse(TestCase):

        def testEmptyFile(self):
                self.assertRaises(OfxParserException, OfxParser.parse, fh)

        #def test_parse(self):
        # make sure the shuffled sequence does not lose any elements


if __name__ == '__main__':
    unittest.main()



