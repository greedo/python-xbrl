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

        assets = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(assets)",re.IGNORECASE|re.MULTILINE))
        if assets:
            gaap_obj.assets = self.total_elements(assets)

        current_assets = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(currentassets)",re.IGNORECASE|re.MULTILINE))
        if current_assets:
            gaap_obj.current_assets = self.total_elements(current_assets)

        non_current_assets = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(assetsnoncurrent)",re.IGNORECASE|re.MULTILINE))
        if non_current_assets == 0 or not non_current_assets:
            gaap_obj.non_current_assets = gaap_obj.current_assets - gaap_obj.assets
        else:
            gaap_obj.non_current_assets = self.total_elements(non_current_assets)

        liabilities = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(liabilities)",re.IGNORECASE|re.MULTILINE))
        if liabilities:
            gaap_obj.liabilities = self.total_elements(liabilities)

        current_liabilities = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(currentliabilities)",re.IGNORECASE|re.MULTILINE))
        if current_liabilities:
            gaap_obj.current_liabilities = self.total_elements(current_liabilities)

        noncurrent_liabilities = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(noncurrentliabilities)",re.IGNORECASE|re.MULTILINE))
        if noncurrent_liabilities:
            gaap_obj.noncurrent_liabilities = self.total_elements(noncurrent_liabilities)

        commitments_and_contingencies = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(commitmentsandcontingencies)",re.IGNORECASE|re.MULTILINE))
        if commitments_and_contingencies:
            gaap_obj.commitments_and_contingencies = self.total_elements(commitments_and_contingencies)

        temporary_equity = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(temporaryequity)",re.IGNORECASE|re.MULTILINE))
        if temporary_equity:
            gaap_obj.temporary_equity = self.total_elements(temporary_equity)

        equity = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(equity)",re.IGNORECASE|re.MULTILINE))
        if equity:
            gaap_obj.equity = self.total_elements(equity)

        revenues = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(revenue)",re.IGNORECASE|re.MULTILINE))
        if revenues:
            gaap_obj.revenue = self.total_elements(revenues)

        gross_profit = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(grossprofit)",re.IGNORECASE|re.MULTILINE))
        if gross_profit:
            gaap_obj.gross_profit = self.total_elements(gross_profit)

        costs_and_expenses = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(costsandexpenses)",re.IGNORECASE|re.MULTILINE))
        if costs_and_expenses:
            gaap_obj.costs_and_expenses = self.total_elements(costs_and_expenses)

        other_operating_income = xbrl.findAll(name=re.compile("(us-gaap:otheroperatingincome)",re.IGNORECASE|re.MULTILINE))
        if other_operating_income:
            gaap_obj.other_operating_income = other_operating_income

        operating_income_loss = xbrl.findAll(name=re.compile("(us-gaap:otheroperatingincome)",re.IGNORECASE|re.MULTILINE))
        if operating_income_loss:
            gaap_obj.operating_income_loss = operating_income_loss

        nonoperating_income_loss = xbrl.findAll(name=re.compile("(us-gaap:nonoperatingincomeloss)",re.IGNORECASE|re.MULTILINE))
        if nonoperating_income_loss:
            gaap_obj.nonoperating_income_loss = nonoperating_income_loss

        interest_and_debt_expense = xbrl.findAll(name=re.compile("(us-gaap:interestanddebtexpense)",re.IGNORECASE|re.MULTILINE))
        if interest_and_debt_expense:
            gaap_obj.interest_and_debt_expense = interest_and_debt_expense

        net_income_shareholders = xbrl.findAll(name=re.compile("(us-gaap:netincomeavailabletocommonstockholdersbasic)",re.IGNORECASE|re.MULTILINE))
        if net_income_shareholders:
            gaap_obj.net_income_shareholders = net_income_shareholders

        comprehensive_income = xbrl.findAll(name=re.compile("(us-gaap:comprehensiveincome)",re.IGNORECASE|re.MULTILINE))
        if comprehensive_income:
            gaap_obj.comprehensive_income = self.total_elements(comprehensive_income)

        comprehensive_income_parent = xbrl.findAll(name=re.compile("(us-gaap:comprehensiveincomenetoftax)",re.IGNORECASE|re.MULTILINE))
        if comprehensive_income_parent:
            gaap_obj.comprehensive_income_parent = self.total_elements(comprehensive_income_parent)

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

    @classmethod
    def parseUnique(self, xbrl):
        '''
        Parse company unique entities in xbrl-land and return an Unique object.
        '''
        unique_obj = Unique()

        unique_data = xbrl.findAll(re.compile('^(?!us-gaap|xbrll):\s*'))
        print unique_data[0]

        return unique_obj

    @staticmethod
    def is_number(s):
        try:
            s = float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def total_elements(elements):

        elements_total = 0
        for element in elements:
            if XBRLParser().is_number(element.text):
                elements_total += float(element.text)
        return elements_total


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
                 assets=None,
                 current_assets=None,
                 non_current_assets=None,
                 liabilities=None,
                 current_liabilities=None,
                 noncurrent_liabilities=None,
                 commitments_and_contingencies=None,
                 temporary_equity=None,
                 equity=None,
                 revenue=None,
                 gross_profit=None,
                 costs_and_expenses=None,
                 other_operating_income=None,
                 comprehensive_income=None,
                 comprehensive_income_parent=None):
        self.assets = assets
        self.current_assets = current_assets
        self.non_current_assets = non_current_assets
        self.liabilities = liabilities
        self.current_liabilities = current_liabilities
        self.noncurrentLiabilities = noncurrent_liabilities
        self.commitments_and_contingencies = commitments_and_contingencies
        self.temporary_equity = temporary_equity
        self.equity = equity
        self.revenue = revenue
        self.gross_profit = gross_profit
        self.costs_and_expenses = costs_and_expenses 
        self.other_operating_income = other_operating_income
        self.comprehensive_income = comprehensive_income
        self.comprehensive_income_parent = comprehensive_income_parent


class GAAPSerializer(Serializer):
    assets = fields.Number()
    current_assets = fields.Number()
    non_current_assets = fields.Number()
    liabilities = fields.Number()
    current_liabilities = fields.Number()
    noncurrent_liabilities = fields.Number()
    commitments_and_contingencies = fields.Number()
    temporary_equity = fields.Number()
    equity = fields.Number()
    revenue = fields.Number()
    gross_profit = fields.Number()
    costs_and_expenses = fields.Number()
    other_operating_income = fields.Number()
    comprehensive_income = fields.Number()
    comprehensive_income_parent = fields.Number()


class Unique(object):
    def __init__(self):
        return None
