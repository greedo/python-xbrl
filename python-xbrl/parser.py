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

        assets = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(assets)",
            re.IGNORECASE | re.MULTILINE))
        if assets:
            gaap_obj.assets = self.total_elements(assets)

        current_assets = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(currentassets)",
            re.IGNORECASE | re.MULTILINE))
        if current_assets:
            gaap_obj.current_assets = self.total_elements(current_assets)

        non_current_assets = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(assetsnoncurrent)",
            re.IGNORECASE | re.MULTILINE))
        if non_current_assets == 0 or not non_current_assets:
            gaap_obj.non_current_assets = gaap_obj.current_assets - \
                gaap_obj.assets
        else:
            gaap_obj.non_current_assets = \
                self.total_elements(non_current_assets)

        liabilities_and_equity = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(liabilitiesand)",
            re.IGNORECASE | re.MULTILINE))
        if liabilities_and_equity:
            gaap_obj.liabilities_and_equity = \
                self.total_elements(liabilities_and_equity)

        liabilities = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(liabilities)",
            re.IGNORECASE | re.MULTILINE))
        if liabilities:
            gaap_obj.liabilities = self.total_elements(liabilities)

        current_liabilities = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(currentliabilities)",
            re.IGNORECASE | re.MULTILINE))
        if current_liabilities:
            gaap_obj.current_liabilities = \
                self.total_elements(current_liabilities)

        noncurrent_liabilities = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(noncurrentliabilities)",
            re.IGNORECASE | re.MULTILINE))
        if noncurrent_liabilities:
            gaap_obj.noncurrent_liabilities = \
                self.total_elements(noncurrent_liabilities)

        commitments_and_contingencies = xbrl.findAll(
            name=re.compile("(us-gaap:commitmentsandcontingencies)",
            re.IGNORECASE | re.MULTILINE))
        if commitments_and_contingencies:
            gaap_obj.commitments_and_contingencies = \
                self.total_elements(commitments_and_contingencies)

        redeemable_noncontrolling_interest = xbrl.findAll(
            name=re.compile("(us-gaap:redeemablenoncontrollinginterestequity)",
            re.IGNORECASE | re.MULTILINE))
        if redeemable_noncontrolling_interest:
            gaap_obj.redeemable_noncontrolling_interest = \
                self.total_elements(redeemable_noncontrolling_interest)

        temporary_equity = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(temporaryequity)",
            re.IGNORECASE | re.MULTILINE))
        if temporary_equity:
            gaap_obj.temporary_equity = self.total_elements(temporary_equity) \
                + gaap_obj.redeemable_noncontrolling_interest

        equity = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(equity)",
            re.IGNORECASE | re.MULTILINE))
        if equity:
            gaap_obj.equity = self.total_elements(equity)

        equity_attributable_interest = xbrl.findAll(
            name=re.compile("(us-gaap:minorityinterest)",
            re.IGNORECASE | re.MULTILINE))

        equity_attributable_interest += xbrl.findAll(
            name=re.compile("(us-gaap:partnerscapitalattributabletonon\
            controllinginterest)", re.IGNORECASE | re.MULTILINE))
        if equity_attributable_interest:
            gaap_obj.equity_attributable_interest = \
                self.total_elements(equity_attributable_interest)

        equity_attributable_parent = xbrl.findAll(
            name=re.compile("(us-gaap:liabilitiesandpartnerscapital)",
            re.IGNORECASE | re.MULTILINE))

        equity_attributable_parent += xbrl.findAll(
            name=re.compile("(us-gaap:stockholdersequity)",
            re.IGNORECASE | re.MULTILINE))
        if equity_attributable_parent:
            gaap_obj.equity_attributable_parent = \
                self.total_elements(equity_attributable_parent)

        # Incomes
        revenues = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(revenue)",
            re.IGNORECASE | re.MULTILINE))
        if revenues:
            gaap_obj.revenue = self.total_elements(revenues)

        cost_of_revenue = xbrl.findAll(
            name=re.compile("(us-gaap:costofrevenue)",
            re.IGNORECASE | re.MULTILINE))

        cost_of_revenue += xbrl.findAll(
            name=re.compile("(us-gaap:costffservices)",
            re.IGNORECASE | re.MULTILINE))

        cost_of_revenue += xbrl.findAll(
            name=re.compile("(us-gaap:costofgoodssold)",
            re.IGNORECASE | re.MULTILINE))

        cost_of_revenue += xbrl.findAll(
            name=re.compile("(us-gaap:costofgoodsandservicessold)",
            re.IGNORECASE | re.MULTILINE))

        gross_profit = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(grossprofit)",
            re.IGNORECASE | re.MULTILINE))
        if gross_profit:
            gaap_obj.gross_profit = self.total_elements(gross_profit)

        operating_expenses = xbrl.findAll(
            name=re.compile("(us-gaap:operating)[^s]*(expenses)",
            re.IGNORECASE | re.MULTILINE))
        if operating_expenses:
            gaap_obj.operating_expenses = \
                self.total_elements(operating_expenses)

        costs_and_expenses = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(costsandexpenses)",
            re.IGNORECASE | re.MULTILINE))
        if costs_and_expenses:
            gaap_obj.costs_and_expenses = \
                self.total_elements(costs_and_expenses)

        other_operating_income = xbrl.findAll(
            name=re.compile("(us-gaap:otheroperatingincome)",
            re.IGNORECASE | re.MULTILINE))
        if other_operating_income:
            gaap_obj.other_operating_income = \
                self.total_elements(other_operating_income)

        operating_income_loss = xbrl.findAll(
            name=re.compile("(us-gaap:otheroperatingincome)",
            re.IGNORECASE | re.MULTILINE))
        if operating_income_loss:
            gaap_obj.operating_income_loss = \
                self.total_elements(operating_income_loss)

        nonoperating_income_loss = xbrl.findAll(
            name=re.compile("(us-gaap:nonoperatingincomeloss)",
            re.IGNORECASE | re.MULTILINE))
        if nonoperating_income_loss:
            gaap_obj.nonoperating_income_loss = \
                self.total_elements(nonoperating_income_loss)

        interest_and_debt_expense = xbrl.findAll(
            name=re.compile("(us-gaap:interestanddebtexpense)",
            re.IGNORECASE | re.MULTILINE))
        if interest_and_debt_expense:
            gaap_obj.interest_and_debt_expense = \
                self.total_elements(interest_and_debt_expense)

        income_before_equity_investments = xbrl.findAll(
            name=re.compile("(us-gaap:incomelossfromcontinuing\
            operationsbeforeincometaxesminorityinterest)",
            re.IGNORECASE | re.MULTILINE))
        if income_before_equity_investments:
            gaap_obj.income_before_equity_investments = \
                self.total_elements(income_before_equity_investments)

        income_from_equity_investments = xbrl.findAll(
            name=re.compile("(us-gaap:incomelossfromequitymethodinvestments)",
            re.IGNORECASE | re.MULTILINE))
        if income_from_equity_investments:
            gaap_obj.income_from_equity_investments = \
                self.total_elements(income_from_equity_investments)

        income_tax_expense_benefit = xbrl.findAll(
            name=re.compile("(us-gaap:incometaxexpensebenefit)",
            re.IGNORECASE | re.MULTILINE))
        if income_tax_expense_benefit:
            gaap_obj.income_tax_expense_benefit = \
                self.total_elements(income_tax_expense_benefit)

        income_continuing_operations_tax = xbrl.findAll(
            name=re.compile("(us-gaap:IncomeLossBeforeExtraordinary\
            ItemsAndCumulativeEffectOfChangeInAccountingPrinciple)",
            re.IGNORECASE | re.MULTILINE))
        if income_continuing_operations_tax:
            gaap_obj.income_continuing_operations_tax = \
                self.total_elements(income_continuing_operations_tax)

        income_discontinued_operations = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(discontinuedoperation)",
            re.IGNORECASE | re.MULTILINE))
        if income_discontinued_operations:
            gaap_obj.income_discontinued_operations = \
                self.total_elements(income_discontinued_operations)

        extraordary_items_gain_loss = xbrl.findAll(
            name=re.compile("(us-gaap:extraordinaryitemnetoftax)",
            re.IGNORECASE | re.MULTILINE))
        if extraordary_items_gain_loss:
            gaap_obj.extraordary_items_gain_loss = \
                self.total_elements(extraordary_items_gain_loss)

        income_loss = xbrl.findAll(
            name=re.compile("(us-gaap:)[^s]*(incomeloss)",
            re.IGNORECASE | re.MULTILINE))
        if income_loss:
            gaap_obj.income_loss = self.total_elements(income_loss)
        income_loss += xbrl.findAll(
            name=re.compile("(us-gaap:profitloss)",
            re.IGNORECASE | re.MULTILINE))
        if income_loss:
            gaap_obj.income_loss = self.total_elements(income_loss)

        net_income_shareholders = xbrl.findAll(
            name=re.compile("(us-gaap:netincomeavailabletocommonstockholders\
            basic)", re.IGNORECASE | re.MULTILINE))
        if net_income_shareholders:
            gaap_obj.net_income_shareholders = \
                self.total_elements(net_income_shareholders)

        preferred_stock_dividends = xbrl.findAll(
            name=re.compile("(us-gaap:preferredstockdividendsandother\
            adjustments)", re.IGNORECASE | re.MULTILINE))
        if preferred_stock_dividends:
            gaap_obj.preferred_stock_dividends = \
                self.total_elements(preferred_stock_dividends)

        net_income_loss_noncontrolling = xbrl.findAll(
            name=re.compile("(us-gaap:netincomelossattributabletononcontrolling\
            interest)", re.IGNORECASE | re.MULTILINE))
        if net_income_loss_noncontrolling:
            gaap_obj.net_income_loss_noncontrolling = \
                self.total_elements(net_income_loss_noncontrolling)

        net_income_parent = xbrl.findAll(
            name=re.compile("(us-gaap:netincomeloss)",
            re.IGNORECASE | re.MULTILINE))
        if net_income_parent:
            gaap_obj.net_income_parent = self.total_elements(net_income_parent)

        other_comprehensive_income = xbrl.findAll(
            name=re.compile("(us-gaap:othercomprehensiveincomelossnetoftax)",
            re.IGNORECASE | re.MULTILINE))
        if other_comprehensive_income:
            gaap_obj.other_comprehensive_income = \
                self.total_elements(other_comprehensive_income)

        comprehensive_income = xbrl.findAll(
            name=re.compile("(us-gaap:comprehensiveincome)",
            re.IGNORECASE | re.MULTILINE))
        if comprehensive_income:
            gaap_obj.comprehensive_income = \
                self.total_elements(comprehensive_income)

        comprehensive_income_parent = xbrl.findAll(
            name=re.compile("(us-gaap:comprehensiveincomenetoftax)",
            re.IGNORECASE | re.MULTILINE))
        if comprehensive_income_parent:
            gaap_obj.comprehensive_income_parent = \
                self.total_elements(comprehensive_income_parent)

        comprehensive_income_interest = xbrl.findAll(
            name=re.compile("(us-gaap:comprehensiveincomenetoftaxattributable\
            tononcontrollinginterest)",
        re.IGNORECASE | re.MULTILINE))
        if comprehensive_income_interest:
            gaap_obj.comprehensive_income_interest = \
                self.total_elements(comprehensive_income_interest)

        # Cash flow statements
        net_cash_flows_operating = xbrl.findAll(
            name=re.compile("(us-gaap:netcashprovidedbyusedinoperating\
            activities)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_operating:
            gaap_obj.net_cash_flows_operating = \
                self.total_elements(net_cash_flows_operating)

        net_cash_flows_investing = xbrl.findAll(
            name=re.compile("(us-gaap:netcashprovidedbyusedininvesting\
            activities)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_investing:
            gaap_obj.net_cash_flows_investing = \
                self.total_elements(net_cash_flows_investing)

        net_cash_flows_financing = xbrl.findAll(
            name=re.compile("(us-gaap:netcashprovidedbyusedinfinancing\
            activities)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_financing:
            gaap_obj.net_cash_flows_financing = \
                self.total_elements(net_cash_flows_financing)

        net_cash_flows_operating_continuing = xbrl.findAll(
            name=re.compile("(us-gaap:netcashprovidedbyusedinoperating\
            activitiescontinuingoperations)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_operating_continuing:
            gaap_obj.net_cash_flows_operating_continuing = \
                self.total_elements(net_cash_flows_operating_continuing)

        net_cash_flows_investing_continuing = xbrl.findAll(
            name=re.compile("(us-gaap:netcashprovidedbyusedininvestingactivities\
            continuingoperations)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_investing_continuing:
            gaap_obj.net_cash_flows_investing_continuing = \
                self.total_elements(net_cash_flows_investing_continuing)

        net_cash_flows_financing_continuing = xbrl.findAll(
            name=re.compile("(us-gaap:netcashprovidedbyusedinfinancingactivities\
            continuingoperations)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_financing_continuing:
            gaap_obj.net_cash_flows_financing_continuing = \
                self.total_elements(net_cash_flows_financing_continuing)

        net_cash_flows_operating_discontinued = xbrl.findAll(
            name=re.compile("(us-gaap:cashprovidedbyusedinoperatingactivities\
            discontinuedoperations)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_operating_discontinued:
            gaap_obj.net_cash_flows_operating_discontinued = \
                self.total_elements(net_cash_flows_operating_discontinued)

        net_cash_flows_investing_discontinued = xbrl.findAll(
            name=re.compile("(us-gaap:cashprovidedbyusedininvestingactivities\
            discontinuedoperations)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_investing_discontinued:
            gaap_obj.net_cash_flows_investing_discontinued = \
                self.total_elements(net_cash_flows_investing_discontinued)

        net_cash_flows_discontinued = xbrl.findAll(
            name=re.compile("(us-gaap:netcashprovidedbyusedindiscontinued\
            operations)", re.IGNORECASE | re.MULTILINE))
        if net_cash_flows_discontinued:
            gaap_obj.net_cash_flows_discontinued = \
                self.total_elements(net_cash_flows_discontinued)

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


# Preprocessing to fix broken XML
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
                 liabilities_and_equity=None,
                 liabilities=None,
                 current_liabilities=None,
                 noncurrent_liabilities=None,
                 commitments_and_contingencies=None,
                 redeemable_noncontrolling_interest=None,
                 temporary_equity=None,
                 equity=None,
                 equity_attributable_interest=None,
                 equity_attributable_parent=None,
                 revenue=None,
                 cost_of_revenue=None,
                 gross_profit=None,
                 costs_and_expenses=None,
                 other_operating_income=None,
                 operating_income_loss=None,
                 nonoperating_income_loss=None,
                 interest_and_debt_expense=None,
                 income_before_equity_investments=None,
                 income_from_equity_investments=None,
                 income_tax_expense_benefit=None,
                 extraordary_items_gain_loss=None,
                 income_loss=None,
                 net_income_shareholders=None,
                 preferred_stock_dividends=None,
                 net_income_loss_noncontrolling=None,
                 net_income_parent=None,
                 other_comprehensive_income=None,
                 comprehensive_income=None,
                 comprehensive_income_parent=None,
                 comprehensive_income_interest=None,
                 net_cash_flows_operating=None,
                 net_cash_flows_investing=None,
                 net_cash_flows_financing=None,
                 net_cash_flows_operating_continuing=None,
                 net_cash_flows_investing_continuing=None,
                 net_cash_flows_financing_continuing=None,
                 net_cash_flows_operating_discontinued=None,
                 net_cash_flows_investing_discontinued=None,
                 net_cash_flows_discontinued=None):
        self.assets = assets
        self.current_assets = current_assets
        self.non_current_assets = non_current_assets
        self.liabilities_and_equity = liabilities_and_equity
        self.liabilities = liabilities
        self.current_liabilities = current_liabilities
        self.noncurrentLiabilities = noncurrent_liabilities
        self.commitments_and_contingencies = commitments_and_contingencies
        self.redeemable_noncontrolling_interest = \
            redeemable_noncontrolling_interest
        self.temporary_equity = temporary_equity
        self.equity = equity
        self.equity_attributable_interest = equity_attributable_interest
        self.equity_attributable_parent = equity_attributable_parent
        self.revenue = revenue
        self.cost_of_revenue = cost_of_revenue
        self.gross_profit = gross_profit
        self.costs_and_expenses = costs_and_expenses
        self.other_operating_income = other_operating_income
        self.nonoperating_income_loss = nonoperating_income_loss
        self.interest_and_debt_expense = interest_and_debt_expense
        self.income_before_equity_investments = \
            income_before_equity_investments
        self.income_from_equity_investments = income_from_equity_investments
        self.income_tax_expense_benefit = income_tax_expense_benefit
        self.net_income_shareholders = net_income_shareholders
        self.extraordary_items_gain_loss = extraordary_items_gain_loss
        self.income_loss = income_loss
        self.net_income_shareholders = net_income_shareholders
        self.preferred_stock_dividends = preferred_stock_dividends
        self.net_income_loss_noncontrolling = net_income_loss_noncontrolling
        self.net_income_parent = net_income_parent
        self.other_comprehensive_income = other_comprehensive_income
        self.comprehensive_income = comprehensive_income
        self.comprehensive_income_parent = comprehensive_income_parent
        self.comprehensive_income_interest = comprehensive_income_interest
        self.net_cash_flows_operating = net_cash_flows_operating
        self.net_cash_flows_investing = net_cash_flows_investing
        self.net_cash_flows_financing = net_cash_flows_financing
        self.net_cash_flows_operating_continuing = \
            net_cash_flows_operating_continuing
        self.net_cash_flows_investing_continuing = \
            net_cash_flows_investing_continuing
        self.net_cash_flows_financing_continuing = \
            net_cash_flows_financing_continuing
        self.net_cash_flows_operating_discontinued = \
            net_cash_flows_operating_discontinued
        self.net_cash_flows_investing_discontinued = \
            net_cash_flows_investing_discontinued
        self.net_cash_flows_discontinued = net_cash_flows_discontinued


class GAAPSerializer(Serializer):
    assets = fields.Number()
    current_assets = fields.Number()
    non_current_assets = fields.Number()
    liabilities_and_equity = fields.Number()
    liabilities = fields.Number()
    current_liabilities = fields.Number()
    noncurrent_liabilities = fields.Number()
    commitments_and_contingencies = fields.Number()
    redeemable_noncontrolling_interest = fields.Number()
    temporary_equity = fields.Number()
    equity = fields.Number()
    equity_attributable_interest = fields.Number()
    equity_attributable_parent = fields.Number()
    revenue = fields.Number()
    cost_of_revenue = fields.Number()
    gross_profit = fields.Number()
    operating_expenses = fields.Number()
    costs_and_expenses = fields.Number()
    other_operating_income = fields.Number()
    operating_income_loss = fields.Number()
    nonoperating_income_loss = fields.Number()
    interest_and_debt_expense = fields.Number()
    income_before_equity_investments = fields.Number()
    income_from_equity_investments = fields.Number()
    income_tax_expense_benefit = fields.Number()
    extraordary_items_gain_loss = fields.Number()
    income_loss = fields.Number()
    net_income_shareholders = fields.Number()
    preferred_stock_dividends = fields.Number()
    net_income_loss_noncontrolling = fields.Number()
    net_income_parent = fields.Number()
    other_comprehensive_income = fields.Number()
    comprehensive_income = fields.Number()
    comprehensive_income_parent = fields.Number()
    comprehensive_income_interest = fields.Number()
    net_cash_flows_operating = fields.Number()
    net_cash_flows_investing = fields.Number()
    net_cash_flows_financing = fields.Number()
    net_cash_flows_operating_continuing = fields.Number()
    net_cash_flows_investing_continuing = fields.Number()
    net_cash_flows_financing_continuing = fields.Number()
    net_cash_flows_operating_discontinued = fields.Number()
    net_cash_flows_investing_discontinued = fields.Number()
    net_cash_flows_discontinued = fields.Number()


class Unique(object):
    def __init__(self):
        return None
