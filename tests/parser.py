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

    def __init__(self, precision=0):
        self.precision = precision

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

        if xbrl.find('xbrl') is None and xbrl.find(name=re.compile("(xbrl*:)")) is None:
            raise XBRLParserException('The xbrl file is empty!')

        return xbrl

    @classmethod
    def parseGAAP(self, xbrl, doc_date):
        '''
        Parse GAAP in xbrl-land and return a GAAP object.
        '''
        gaap_obj = GAAP()

        assets = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(assets)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.assets = self.data_processing(assets, xbrl)

        current_assets = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(currentassets)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.current_assets = self.data_processing(current_assets, xbrl)

        non_current_assets = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(assetsnoncurrent)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        if non_current_assets == 0 or not non_current_assets:
            gaap_obj.non_current_assets = gaap_obj.current_assets - gaap_obj.assets
        else:
            gaap_obj.non_current_assets = self.data_processing(non_current_assets, xbrl)

        liabilities_and_equity = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(liabilitiesand)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.liabilities_and_equity = self.data_processing(liabilities_and_equity, xbrl)

        liabilities = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(liabilities)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.liabilities = self.data_processing(liabilities, xbrl)

        current_liabilities = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(currentliabilities)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.current_liabilities = self.data_processing(current_liabilities, xbrl)

        noncurrent_liabilities = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(noncurrentliabilities)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.noncurrent_liabilities = self.data_processing(noncurrent_liabilities, xbrl)

        commitments_and_contingencies = xbrl.findAll(name=re.compile("(us-gaap:commitmentsandcontingencies)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.commitments_and_contingencies = self.data_processing(commitments_and_contingencies, xbrl)

        redeemable_noncontrolling_interest = xbrl.findAll(name=re.compile("(us-gaap:redeemablenoncontrollinginterestequity)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.redeemable_noncontrolling_interest = self.data_processing(redeemable_noncontrolling_interest, xbrl)

        temporary_equity = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(temporaryequity)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.temporary_equity = self.data_processing(temporary_equity, xbrl)

        equity = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(equity)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.equity = self.data_processing(equity, xbrl)

        equity_attributable_interest = xbrl.findAll(name=re.compile("(us-gaap:minorityinterest)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        equity_attributable_interest += xbrl.findAll(name=re.compile("(us-gaap:partnerscapitalattributabletononcontrollinginterest)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.equity_attributable_interest = self.data_processing(equity_attributable_interest, xbrl)

        equity_attributable_parent = xbrl.findAll(name=re.compile("(us-gaap:liabilitiesandpartnerscapital)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        stockholders_equity = xbrl.findAll(name=re.compile("(us-gaap:stockholdersequity)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.equity_attributable_parent = self.data_processing(equity_attributable_parent, xbrl)
        gaap_obj.stockholders_equity = self.data_processing(stockholders_equity, xbrl)

        ### Incomes ###
        revenues = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(revenue)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.revenues = self.data_processing(revenues, xbrl)

        cost_of_revenue = xbrl.findAll(name=re.compile("(us-gaap:costofrevenue)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        cost_of_revenue += xbrl.findAll(name=re.compile("(us-gaap:costffservices)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        cost_of_revenue += xbrl.findAll(name=re.compile("(us-gaap:costofgoodssold)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        cost_of_revenue += xbrl.findAll(name=re.compile("(us-gaap:costofgoodsandservicessold)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})

        gross_profit = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(grossprofit)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.gross_profit = self.data_processing(gross_profit, xbrl)

        operating_expenses = xbrl.findAll(name=re.compile("(us-gaap:operating)[^s]*(expenses)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.operating_expenses = self.data_processing(operating_expenses, xbrl)

        costs_and_expenses = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(costsandexpenses)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.costs_and_expenses = self.data_processing(costs_and_expenses, xbrl)

        other_operating_income = xbrl.findAll(name=re.compile("(us-gaap:otheroperatingincome)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.other_operating_income = self.data_processing(other_operating_income, xbrl)

        operating_income_loss = xbrl.findAll(name=re.compile("(us-gaap:otheroperatingincome)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.operating_income_loss = self.data_processing(operating_income_loss, xbrl)

        nonoperating_income_loss = xbrl.findAll(name=re.compile("(us-gaap:nonoperatingincomeloss)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.nonoperating_income_loss = self.data_processing(nonoperating_income_loss, xbrl)

        interest_and_debt_expense = xbrl.findAll(name=re.compile("(us-gaap:interestanddebtexpense)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.interest_and_debt_expense = self.data_processing(interest_and_debt_expense, xbrl)

        income_before_equity_investments = xbrl.findAll(name=re.compile("(us-gaap:incomelossfromcontinuingoperationsbeforeincometaxesminorityinterest)",re.IGNORECASE|re.MULTILINE), attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.income_before_equity_investments = self.data_processing(income_before_equity_investments, xbrl)

        income_from_equity_investments = xbrl.findAll(name=re.compile("(us-gaap:incomelossfromequitymethodinvestments)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.income_from_equity_investments = self.data_processing(income_from_equity_investments, xbrl)

        income_tax_expense_benefit = xbrl.findAll(name=re.compile("(us-gaap:incometaxexpensebenefit)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.income_tax_expense_benefit = self.data_processing(income_tax_expense_benefit, xbrl)

        income_continuing_operations_tax = xbrl.findAll(name=re.compile("(us-gaap:IncomeLossBeforeExtraordinaryItemsAndCumulativeEffectOfChangeInAccountingPrinciple)",re.IGNORECASE|re.MULTILINE), attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.income_continuing_operations_tax = self.data_processing(income_continuing_operations_tax, xbrl)

        income_discontinued_operations = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(discontinuedoperation)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.income_discontinued_operations = self.data_processing(income_discontinued_operations, xbrl)

        extraordary_items_gain_loss = xbrl.findAll(name=re.compile("(us-gaap:extraordinaryitemnetoftax)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.extraordary_items_gain_loss = self.data_processing(extraordary_items_gain_loss, xbrl)

        income_loss = xbrl.findAll(name=re.compile("(us-gaap:)[^s]*(incomeloss)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.income_loss = self.data_processing(income_loss, xbrl)
        income_loss += xbrl.findAll(name=re.compile("(us-gaap:profitloss)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.income_loss = self.data_processing(income_loss, xbrl)
        
        net_income_shareholders = xbrl.findAll(name=re.compile("(us-gaap:netincomeavailabletocommonstockholdersbasic)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_income_shareholders = self.data_processing(net_income_shareholders, xbrl)

        preferred_stock_dividends = xbrl.findAll(name=re.compile("(us-gaap:preferredstockdividendsandotheradjustments)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.preferred_stock_dividends = self.data_processing(preferred_stock_dividends, xbrl)

        net_income_loss_noncontrolling = xbrl.findAll(name=re.compile("(us-gaap:netincomelossattributabletononcontrollinginterest)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_income_loss_noncontrolling = self.data_processing(net_income_loss_noncontrolling, xbrl)
        
        net_income_parent = xbrl.findAll(name=re.compile("(us-gaap:netincomeloss)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_income_parent = self.data_processing(net_income_parent, xbrl)

        other_comprehensive_income = xbrl.findAll(name=re.compile("(us-gaap:othercomprehensiveincomelossnetoftax)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.other_comprehensive_income = self.data_processing(other_comprehensive_income, xbrl)

        comprehensive_income = xbrl.findAll(name=re.compile("(us-gaap:comprehensiveincome)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.comprehensive_income = self.data_processing(comprehensive_income, xbrl)

        comprehensive_income_parent = xbrl.findAll(name=re.compile("(us-gaap:comprehensiveincomenetoftax)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.comprehensive_income_parent = self.data_processing(comprehensive_income_parent, xbrl)

        comprehensive_income_interest = xbrl.findAll(name=re.compile("(us-gaap:comprehensiveincomenetoftaxattributabletononcontrollinginterest)",re.IGNORECASE|re.MULTILINE), attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.comprehensive_income_interest = self.data_processing(comprehensive_income_interest, xbrl)

        ### Cash flow statement ###
        net_cash_flows_operating = xbrl.findAll(name=re.compile("(us-gaap:netcashprovidedbyusedinoperatingactivities)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_flows_operating = self.data_processing(net_cash_flows_operating, xbrl)

        net_cash_flows_investing = xbrl.findAll(name=re.compile("(us-gaap:netcashprovidedbyusedininvestingactivities)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_flows_investing = self.data_processing(net_cash_flows_investing, xbrl)

        net_cash_flows_financing = xbrl.findAll(name=re.compile("(us-gaap:netcashprovidedbyusedinfinancingactivities)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_flows_financing = self.data_processing(net_cash_flows_financing, xbrl)

        net_cash_flows_operating_continuing = xbrl.findAll(name=re.compile("(us-gaap:netcashprovidedbyusedinoperatingactivitiescontinuingoperations)",re.IGNORECASE|re.MULTILINE), attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_operating_continuing = self.data_processing(net_cash_flows_operating_continuing, xbrl)
        
        net_cash_flows_investing_continuing = xbrl.findAll(name=re.compile("(us-gaap:netcashprovidedbyusedininvestingactivitiescontinuingoperations)",re.IGNORECASE|re.MULTILINE), attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_flows_investing_continuing = self.data_processing(net_cash_flows_investing_continuing, xbrl)
                        
        net_cash_flows_financing_continuing = xbrl.findAll(name=re.compile("(us-gaap:netcashprovidedbyusedinfinancingactivitiescontinuingoperations)",re.IGNORECASE|re.MULTILINE), attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_flows_financing_continuing = self.data_processing(net_cash_flows_financing_continuing, xbrl)

        net_cash_flows_operating_discontinued = xbrl.findAll(name=re.compile("(us-gaap:cashprovidedbyusedinoperatingactivitiesdiscontinuedoperations)",re.IGNORECASE|re.MULTILINE), attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_flows_operating_discontinued = self.data_processing(net_cash_flows_operating_discontinued, xbrl)

        net_cash_flows_investing_discontinued = xbrl.findAll(name=re.compile("(us-gaap:CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations)",re.IGNORECASE|re.MULTILINE), attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_flows_investing_discontinued = self.data_processing(net_cash_flows_investing_discontinued, xbrl)

        net_cash_flows_discontinued = xbrl.findAll(name=re.compile("(us-gaap:netcashprovidedbyusedindiscontinuedoperations)",re.IGNORECASE|re.MULTILINE),
        attrs={"contextref" : re.compile("("+doc_date+")")})
        gaap_obj.net_cash_flows_discontinued = self.data_processing(net_cash_flows_discontinued, xbrl)

        return gaap_obj

    @classmethod
    def parseUnique(self, xbrl):
        '''
        Parse company unique entities in xbrl-land and return an Unique object.
        '''
        unique_obj = Unique()

        unique_data = xbrl.findAll(re.compile('^(?!us-gaap|xbrl*):\s*'))
        print unique_data[0]

        return unique_obj
    
    @staticmethod
    def trim_decimals(s, precision):
        return int(str(s.encode('ascii','ignore'))[:precision])

    @staticmethod
    def is_number(s):
        try:
            s = float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def total_elements(elements, precision=0):

        elements_total = 0
        for element in elements:
            if XBRLParser().is_number(element.text):
                elements_total += float(XBRLParser().trim_decimals(element.text, int(precision)))
        return elements_total

    @classmethod
    def data_processing(self, elements, xbrl):
        if len(elements) > 0 and XBRLParser().is_number(elements[0].text):
            if filter(lambda x: x[0]=='decimals', elements[0].attrs)[0][1] is not None:
                attr_precision = filter(lambda x: x[0]=='decimals', elements[0].attrs)[0][1]
                if xbrl.precision is not 0 and xbrl.precison is not attr_precision:
                    xbrl.precision = attr_precision
            if elements:
                return self.total_elements(elements, xbrl.precision)
            else:
                return 0
        else:
            return 0


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
                tag_name = re.findall(r'(?i)<*>', token)[0]
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
                 assets=0.0,
                 current_assets=0.0,
                 non_current_assets=0.0,
                 liabilities_and_equity=0.0,
                 liabilities=0.0,
                 current_liabilities=0.0,
                 noncurrent_liabilities=0.0,
                 commitments_and_contingencies=0.0,
                 redeemable_noncontrolling_interest=0.0,
                 temporary_equity=0.0,
                 equity=0.0,
                 equity_attributable_interest=0.0,
                 equity_attributable_parent=0.0,
                 stockholders_equity=0.0,
                 revenue=0.0,
                 cost_of_revenue=0.0,
                 gross_profit=0.0,
                 costs_and_expenses=0.0,
                 other_operating_income=0.0,
                 operating_income_loss=0.0,
                 nonoperating_income_loss=0.0,
                 interest_and_debt_expense=0.0,
                 income_before_equity_investments=0.0,
                 income_from_equity_investments=0.0,
                 income_tax_expense_benefit=0.0,
                 extraordary_items_gain_loss=0.0,
                 income_loss=0.0,
                 net_income_shareholders=0.0,
                 preferred_stock_dividends=0.0,
                 net_income_loss_noncontrolling=0.0,
                 net_income_parent=0.0,
                 other_comprehensive_income=0.0,
                 comprehensive_income=0.0,
                 comprehensive_income_parent=0.0,
                 comprehensive_income_interest=0.0,
                 net_cash_flows_operating=0.0,
                 net_cash_flows_investing=0.0,
                 net_cash_flows_financing=0.0,
                 net_cash_flows_operating_continuing=0.0,
                 net_cash_flows_investing_continuing=0.0,
                 net_cash_flows_financing_continuing=0.0,
                 net_cash_flows_operating_discontinued=0.0,
                 net_cash_flows_investing_discontinued=0.0,
                 net_cash_flows_discontinued=0.0):
        self.assets = assets
        self.current_assets = current_assets
        self.non_current_assets = non_current_assets
        self.liabilities_and_equity = liabilities_and_equity
        self.liabilities = liabilities
        self.current_liabilities = current_liabilities
        self.noncurrentLiabilities = noncurrent_liabilities
        self.commitments_and_contingencies = commitments_and_contingencies
        self.redeemable_noncontrolling_interest = redeemable_noncontrolling_interest
        self.temporary_equity = temporary_equity
        self.equity = equity
        self.equity_attributable_interest = equity_attributable_interest
        self.equity_attributable_parent = equity_attributable_parent
        self.stockholders_equity = stockholders_equity
        self.revenue = revenue
        self.cost_of_revenue = cost_of_revenue
        self.gross_profit = gross_profit
        self.costs_and_expenses = costs_and_expenses 
        self.other_operating_income = other_operating_income
        self.nonoperating_income_loss = nonoperating_income_loss
        self.interest_and_debt_expense = interest_and_debt_expense 
        self.income_before_equity_investments = income_before_equity_investments
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
        self.net_cash_flows_operating_continuing = net_cash_flows_operating_continuing
        self.net_cash_flows_investing_continuing = net_cash_flows_investing_continuing
        self.net_cash_flows_financing_continuing = net_cash_flows_financing_continuing
        self.net_cash_flows_operating_discontinued = net_cash_flows_operating_discontinued
        self.net_cash_flows_investing_discontinued = net_cash_flows_investing_discontinued
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
    stockholders_equity = fields.Number()
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
    net_income_parent= fields.Number()
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
