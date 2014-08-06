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
        Parse GAAP in xbrl-land and return a GAAP object.
        '''
        gaap_obj = GAAP()

        accumulated_other = xbrl.find(re.compile('^us-gaap:accumulatedothercomprehensiveincomelossnetoftax\s*'))
        if accumulated_other:
            gaap_obj.accumulated_other = accumulated_other.text

        stockholders_equity = xbrl.find(re.compile('^us-gaap:stockholdersequity\s*'))
        if stockholders_equity:
            gaap_obj.stockholders_equity = stockholders_equity.text

        cash_and_cash = xbrl.find(re.compile('^us-gaap:cashandcashequivalentsatcarryingvalue\s*'))
        if cash_and_cash:
            gaap_obj.cash_and_cash = cash_and_cash.text

        shares_outstanding = xbrl.find(re.compile('^us-gaap:sharesoutstanding\s*'))
        if shares_outstanding:
            gaap_obj.shares_outstanding = shares_outstanding.text

        valuation_allowance = xbrl.find(re.compile('^us-gaap:valuationallowancesandreservesbalance\s*'))
        if valuation_allowance:
            gaap_obj.valuation_allowance = valuation_allowance.text

        share_based_comp = xbrl.find(re.compile('^us-gaap:sharebasedcompensationarrangementbysharebased\
        paymentawardequityinstrumentsotherthanoptionsnonvestednumber\s*'))
        if share_based_comp:
            gaap_obj.share_based_comp = share_based_comp.text

        share_based_comp_exercise = xbrl.find(re.compile('^us-gaap:sharebasedcompensationarrangementby\
        sharebasedpaymentawardoptionsexercisablenumber\s*'))
        if share_based_comp_exercise:
            gaap_obj.share_based_comp_exercise = share_based_comp_exercise.text

        share_based_comp_exercise_price = xbrl.find(re.compile('^us-gaap:sharebasedcompensationarrangement\
        bysharebasedpaymentwwardoptionsoutstandingweightedaverageexerciseprice\s*'))
        if share_based_comp_exercise_price:
            gaap_obj.share_based_comp_exercise_price = share_based_comp_exercise_price.text

        share_based_comp_outstanding = xbrl.find(re.compile('^us-gaap:sharebasedcompensationarrangementby\
        sharebasedpaymentawardoptionsoutstandingnumber\s*'))
        if share_based_comp_outstanding:
            gaap_obj.share_based_comp_outstanding = share_based_comp_outstanding.text

        return gaap_obj

    @classmethod
    def parseUnique(self, xbrl):
        '''
        Parse company unique entities in xbrl-land and return an Unique object.
        '''
        unique_obj = Unique()

        unique_data = xbrl.findAll(re.compile('^(?!us-gaap|xbrll):\s*'))
        print unique_data[0]

        return unique_obj


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
                 shares_outstanding=None,
                 valuation_allowance=None,
                 share_based_comp=None,
                 share_based_comp_exercise=None,
                 share_based_comp_exercise_price=None,
                 share_based_comp_outstanding=None):
        self.accumulated_other = accumulated_other
        self.cash_and_cash = cash_and_cash
        self.stockholders_equity = stockholders_equity
        self.shares_outstanding = shares_outstanding
        self.valuation_allowance = valuation_allowance
        self.share_based_comp = share_based_comp
        self.share_based_comp_exercise = share_based_comp_exercise
        self.share_based_comp_exercise_price = share_based_comp_exercise_price
        self.share_based_comp_outstanding = share_based_comp_outstanding


class GAAPSerializer(Serializer):
    accumulated_other = fields.Number()
    stockholders_equity = fields.Number()
    cash_and_cash = fields.Number()
    stockholders_equity = fields.Number()
    shares_outstanding = fields.Number()
    valuation_allowance = fields.Number()
    share_based_comp = fields.Number()
    share_based_comp_exercise = fields.Number()
    share_based_comp_exercise_price = fields.Number()
    share_based_comp_outstanding = fields.Number()


class Unique(object):
    def __init__(self):
        return None
