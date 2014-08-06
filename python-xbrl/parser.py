import collections
import re
from marshmallow import Serializer, fields, pprint
import pprint

if 'OrderedDict' in dir(collections):
    odict = collections
else:
    import ordereddict as odict

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def soup_maker(fh):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(fh, "xml")
        for tag in soup.findAll():
            tag.name = tag.name.lower()
    except ImportError:
        from BeautifulSoup import BeautifulStoneSoup
        soup = BeautifulStoneSoup(fh)
    return soup


class XBRLFile(object):
    def __init__(self, fh):
        """
        fh should be a seekable file-like byte stream object
        """
        self.headers = odict.OrderedDict()
        self.fh = fh

class XBRLParserException(Exception):
    pass

class XBRLParser(object):
    @classmethod
    def parse(self, file_handle):
        '''
        parse is the main entry point for an XBRLParser. It takes a file
        handle.

        '''

        xbrl_obj = XBRL()

        # Store the headers
        xbrl_file = XBRLPreprocessedFile(file_handle)
        xbrl = soup_maker(xbrl_file.fh)
        if xbrl.find('xbrl') is None:
            raise XBRLParserException('The xbrl file is empty!')

        return xbrl

    @classmethod
    def parseGAAP(self, xbrl):
        '''
        Parse a GAAP in xbrl-land and return a GAAP object.
        '''
        gaap_obj = GAAP()

        accumulated_other = xbrl.find(re.compile('^us-gaap:accumulatedothercomprehensiveincomelossnetoftax\s*'))
        if accumulated_other:
            gaap_obj.accumulated_other = accumulated_other.text

        stockholders_equity = xbrl.find(re.compile('^us-gaap:stockholdersequity\s*'))
        if stockholders_equity:
            gaap_obj.stockholders_equity = stockholders_equity.text

        cash_and_cash = xbrl.find(re.compile('^cashandcashequivalentsatcarryingvalue\s*'))
        if cash_and_cash:
            gaap_obj.cash_and_cash = cash_and_cash.text

        shares_outstanding = xbrl.find(re.compile('^us-gaap:sharesoutstanding\s*'))
        if shares_outstanding:
            gaap_obj.shares_outstanding = shares_outstanding.text

        return gaap_obj


#Preprocessing to fix broken XML
# TODO - Run tests to see if other XML processing errors can occur
class XBRLPreprocessedFile(XBRLFile):
    def __init__(self, fh):
        super(XBRLPreprocessedFile, self).__init__(fh)

        if self.fh is None:
            return

        xbrl_string = self.fh.read()

        # find all closing tags as hints
        closing_tags = [t.upper() for t in re.findall(r'(?i)</([a-z0-9_\.]+)>',
                        xbrl_string)]

        # close all tags that don't have closing tags and
        # leave all other data intact
        last_open_tag = None
        tokens = re.split(r'(?i)(</?[a-z0-9_\.]+>)', xbrl_string)
        new_fh = StringIO()
        for idx, token in enumerate(tokens):
            is_closing_tag = token.startswith('</')
            is_processing_tag = token.startswith('<?')
            is_cdata = token.startswith('<!')
            is_tag = token.startswith('<') and not is_cdata
            is_open_tag = is_tag and not is_closing_tag \
                and not is_processing_tag
            if is_tag:
                if last_open_tag is not None:
                    new_fh.write("</%s>" % last_open_tag)
                    last_open_tag = None
            if is_open_tag:
                tag_name = re.findall(r'(?i)<([a-z0-9_\.]+)>', token)[0]
                if tag_name.upper() not in closing_tags:
                    last_open_tag = tag_name
            new_fh.write(token)
        new_fh.seek(0)
        self.fh = new_fh

class XBRL(object):
    def __str__(self):
        return ""

class GAAP(object):
    def __init__(self,
                 accumulated_other=None,
                 stockholders_equity=None,
                 cash_and_cash=None,
                 shares_outstanding=None):
        self.accumulated_other = accumulated_other
        self.stockholders_equity = stockholders_equity
        self.cash_and_cash = cash_and_cash 
        self.shares_outstanding = shares_outstanding

class GAAPSerializer(Serializer):
    accumulated_other = fields.Number()
    stockholders_equity = fields.Number()
    cash_and_cash = fields.Number()
    shares_outstanding = fields.Number()
