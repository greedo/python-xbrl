#! /usr/bin/env python
# encoding: utf-8

import re
from marshmallow import Schema, fields
import datetime
import collections
import six
import logging

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

if 'OrderedDict' in dir(collections):
    odict = collections
else:
    import ordereddict as odict


def soup_maker(fh):
    """ Takes a file handler returns BeautifulSoup"""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(fh, "lxml")
        for tag in soup.find_all():
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
        """
        parse is the main entry point for an XBRLParser. It takes a file
        handle.
        """

        xbrl_obj = XBRL()

        # if no file handle was given create our own
        if not hasattr(file_handle, 'read'):
            file_handler = open(file_handle)
        else:
            file_handler = file_handle

        # Store the headers
        xbrl_file = XBRLPreprocessedFile(file_handler)

        xbrl = soup_maker(xbrl_file.fh)
        file_handler.close()
        xbrl_base = xbrl.find(name=re.compile("xbrl*:*"))

        if xbrl.find('xbrl') is None and xbrl_base is None:
            raise XBRLParserException('The xbrl file is empty!')

        # lookahead to see if we need a custom leading element
        lookahead = xbrl.find(name=re.compile("context",
                              re.IGNORECASE | re.MULTILINE)).name
        if ":" in lookahead:
            self.xbrl_base = lookahead.split(":")[0] + ":"
        else:
            self.xbrl_base = ""

        return xbrl

    @classmethod
    def parseGAAP(self,
                  xbrl,
                  doc_date="",
                  context="current",
                  ignore_errors=0):
        """
        Parse GAAP from our XBRL soup and return a GAAP object.
        """
        gaap_obj = GAAP()

        if ignore_errors == 2:
            logging.basicConfig(filename='/tmp/xbrl.log',
                level=logging.ERROR,
                format='%(asctime)s %(levelname)s %(name)s %(message)s')
            logger = logging.getLogger(__name__)
        else:
            logger = None

        # the default is today
        if doc_date == "":
            doc_date = str(datetime.date.today())
        doc_date = re.sub(r"[^0-9]+", "", doc_date)

        # current is the previous quarter
        if context == "current":
            context = 90

        if context == "year":
            context = 360

        context = int(context)

        if context % 90 == 0:
            context_extended = list(range(context, context + 9))
            expected_start_date = \
                datetime.datetime.strptime(doc_date, "%Y%m%d") \
                - datetime.timedelta(days=context)
        elif context == "instant":
            expected_start_date = None
        else:
            raise XBRLParserException('invalid context')

        # we need expected end date unless instant
        if context != "instant":
            expected_end_date = \
                datetime.datetime.strptime(doc_date, "%Y%m%d")

        doc_root = ""

        # we might need to attach the document root
        if len(self.xbrl_base) > 1:
            doc_root = self.xbrl_base

        # collect all contexts up that are relevant to us
        # TODO - Maybe move this to Preprocessing Ingestion
        context_ids = []
        context_tags = xbrl.find_all(name=re.compile(doc_root + "context",
                                     re.IGNORECASE | re.MULTILINE))

        try:
            for context_tag in context_tags:
                # we don't want any segments
                if context_tag.find(doc_root + "entity") is None:
                    continue
                if context_tag.find(doc_root + "entity").find(
                doc_root + "segment") is None:
                    context_id = context_tag.attrs['id']

                    found_start_date = None
                    found_end_date = None

                    if context_tag.find(doc_root + "instant"):
                        instant = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "instant")
                                                        .text)[:8], "%Y%m%d")
                        if instant == expected_end_date:
                            context_ids.append(context_id)
                            continue

                    if context_tag.find(doc_root + "period").find(
                    doc_root + "startdate"):
                        found_start_date = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "period")
                                                       .find(doc_root +
                                                             "startdate")
                                                        .text)[:8], "%Y%m%d")
                    if context_tag.find(doc_root + "period").find(doc_root +
                    "enddate"):
                        found_end_date = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "period")
                                                       .find(doc_root +
                                                             "enddate")
                                                       .text)[:8], "%Y%m%d")
                    if found_end_date and found_start_date:
                        for ce in context_extended:
                            if found_end_date - found_start_date == \
                            datetime.timedelta(days=ce):
                                if found_end_date == expected_end_date:
                                    context_ids.append(context_id)
        except IndexError:
            raise XBRLParserException('problem getting contexts')

        assets = xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(assets)",
                               re.IGNORECASE | re.MULTILINE))
        gaap_obj.assets = self.data_processing(assets, xbrl,
            ignore_errors, logger, context_ids)

        current_assets = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(currentassets)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.current_assets = self.data_processing(current_assets,
            xbrl, ignore_errors, logger, context_ids)

        non_current_assets = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(assetsnoncurrent)",
                          re.IGNORECASE | re.MULTILINE))
        if non_current_assets == 0 or not non_current_assets:
            gaap_obj.non_current_assets = gaap_obj.current_assets \
                - gaap_obj.assets
        else:
            gaap_obj.non_current_assets = \
                self.data_processing(non_current_assets, xbrl,
                    ignore_errors, logger, context_ids)

        liabilities_and_equity = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(liabilitiesand)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.liabilities_and_equity = \
            self.data_processing(liabilities_and_equity, xbrl,
                ignore_errors, logger, context_ids)

        liabilities = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(liabilities)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.liabilities = \
            self.data_processing(liabilities, xbrl, ignore_errors,
                logger, context_ids)

        current_liabilities = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]\
                          *(currentliabilities)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.current_liabilities = \
            self.data_processing(current_liabilities, xbrl,
                ignore_errors, logger, context_ids)

        noncurrent_liabilities = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]\
                          *(noncurrentliabilities)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.noncurrent_liabilities = \
            self.data_processing(noncurrent_liabilities, xbrl,
                ignore_errors, logger, context_ids)

        commitments_and_contingencies = \
            xbrl.find_all(name=re.compile("(us-gaap:commitments\
                          andcontingencies)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.commitments_and_contingencies = \
            self.data_processing(commitments_and_contingencies, xbrl,
                ignore_errors, logger, context_ids)

        redeemable_noncontrolling_interest = \
            xbrl.find_all(name=re.compile("(us-gaap:redeemablenoncontrolling\
                          interestequity)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.redeemable_noncontrolling_interest = \
            self.data_processing(redeemable_noncontrolling_interest,
                xbrl, ignore_errors, logger, context_ids)

        temporary_equity = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(temporaryequity)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.temporary_equity = \
            self.data_processing(temporary_equity, xbrl, ignore_errors,
                logger, context_ids)

        equity = xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(equity)",
                               re.IGNORECASE | re.MULTILINE))
        gaap_obj.equity = self.data_processing(equity, xbrl, ignore_errors,
            logger, context_ids)

        equity_attributable_interest = \
            xbrl.find_all(name=re.compile("(us-gaap:minorityinterest)",
                          re.IGNORECASE | re.MULTILINE))
        equity_attributable_interest += \
            xbrl.find_all(name=re.compile("(us-gaap:partnerscapitalattributable\
                          tononcontrollinginterest)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.equity_attributable_interest = \
            self.data_processing(equity_attributable_interest, xbrl,
                ignore_errors, logger, context_ids)

        equity_attributable_parent = \
            xbrl.find_all(name=re.compile("(us-gaap:liabilitiesandpartners\
                          capital)",
                          re.IGNORECASE | re.MULTILINE))
        stockholders_equity = \
            xbrl.find_all(name=re.compile("(us-gaap:stockholdersequity)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.equity_attributable_parent = \
            self.data_processing(equity_attributable_parent, xbrl,
                ignore_errors, logger, context_ids)
        gaap_obj.stockholders_equity = \
            self.data_processing(stockholders_equity, xbrl, ignore_errors,
                logger, context_ids)

        # Incomes #
        revenues = xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(revenue)",
                                 re.IGNORECASE | re.MULTILINE))
        gaap_obj.revenues = self.data_processing(revenues, xbrl,
            ignore_errors, logger, context_ids)

        cost_of_revenue = \
            xbrl.find_all(name=re.compile("(us-gaap:costofrevenue)",
                          re.IGNORECASE | re.MULTILINE))
        cost_of_revenue += \
            xbrl.find_all(name=re.compile("(us-gaap:costffservices)",
                          re.IGNORECASE | re.MULTILINE))
        cost_of_revenue += \
            xbrl.find_all(name=re.compile("(us-gaap:costofgoodssold)",
                          re.IGNORECASE | re.MULTILINE))
        cost_of_revenue += \
            xbrl.find_all(name=re.compile("(us-gaap:costofgoodsand\
                          servicessold)",
                          re.IGNORECASE | re.MULTILINE))

        gross_profit = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(grossprofit)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.gross_profit = \
            self.data_processing(gross_profit, xbrl, ignore_errors,
                                 logger, context_ids)

        operating_expenses = \
            xbrl.find_all(name=re.compile("(us-gaap:operating)[^s]*(expenses)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.operating_expenses = \
            self.data_processing(operating_expenses, xbrl, ignore_errors,
                                 logger, context_ids)

        costs_and_expenses = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(costsandexpenses)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.costs_and_expenses = \
            self.data_processing(costs_and_expenses, xbrl, ignore_errors,
                                 logger, context_ids)

        other_operating_income = \
            xbrl.find_all(name=re.compile("(us-gaap:otheroperatingincome)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.other_operating_income = \
            self.data_processing(other_operating_income, xbrl, ignore_errors,
                                 logger, context_ids)

        operating_income_loss = \
            xbrl.find_all(name=re.compile("(us-gaap:otheroperatingincome)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.operating_income_loss = \
            self.data_processing(operating_income_loss, xbrl, ignore_errors,
                                 logger, context_ids)

        nonoperating_income_loss = \
            xbrl.find_all(name=re.compile("(us-gaap:nonoperatingincomeloss)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.nonoperating_income_loss = \
            self.data_processing(nonoperating_income_loss, xbrl,
                                 ignore_errors, logger, context_ids)

        interest_and_debt_expense = \
            xbrl.find_all(name=re.compile("(us-gaap:interestanddebtexpense)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.interest_and_debt_expense = \
            self.data_processing(interest_and_debt_expense, xbrl,
                                 ignore_errors, logger, context_ids)

        income_before_equity_investments = \
            xbrl.find_all(name=re.compile("(us-gaap:incomelossfromcontinuing"
                                          "operationsbeforeincometaxes"
                                          "minorityinterest)",
                          re.IGNORECASE  | re.MULTILINE))
        gaap_obj.income_before_equity_investments = \
            self.data_processing(income_before_equity_investments, xbrl,
                                 ignore_errors, logger, context_ids)

        income_from_equity_investments = \
            xbrl.find_all(name=re.compile("(us-gaap:incomelossfromequity"
                          "methodinvestments)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_from_equity_investments = \
            self.data_processing(income_from_equity_investments, xbrl,
                                 ignore_errors, logger, context_ids)

        income_tax_expense_benefit = \
            xbrl.find_all(name=re.compile("(us-gaap:incometaxexpensebenefit)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_tax_expense_benefit = \
            self.data_processing(income_tax_expense_benefit, xbrl,
                                 ignore_errors, logger, context_ids)

        income_continuing_operations_tax = \
            xbrl.find_all(name=re.compile("(us-gaap:IncomeLossBeforeExtraordinaryItems\
                          AndCumulativeEffectOfChangeInAccountingPrinciple)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_continuing_operations_tax = \
            self.data_processing(income_continuing_operations_tax, xbrl,
                                 ignore_errors, logger, context_ids)

        income_discontinued_operations = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(discontinued"
                          "operation)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_discontinued_operations = \
            self.data_processing(income_discontinued_operations, xbrl,
                                 ignore_errors, logger, context_ids)

        extraordary_items_gain_loss = \
            xbrl.find_all(name=re.compile("(us-gaap:extraordinaryitem"
                          "netoftax)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.extraordary_items_gain_loss = \
            self.data_processing(extraordary_items_gain_loss, xbrl,
                                 ignore_errors, logger, context_ids)

        income_loss = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(incomeloss)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_loss = \
            self.data_processing(income_loss, xbrl, ignore_errors,
                logger, context_ids)
        income_loss += xbrl.find_all(name=re.compile("(us-gaap:profitloss)",
                                     re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_loss = \
            self.data_processing(income_loss, xbrl, ignore_errors,
                                 logger, context_ids)

        net_income_shareholders = \
            xbrl.find_all(name=re.compile("(us-gaap:netincomeavailabletocommon\
                          stockholdersbasic)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_income_shareholders = \
            self.data_processing(net_income_shareholders, xbrl, ignore_errors,
                                 logger, context_ids)

        preferred_stock_dividends = \
            xbrl.find_all(name=re.compile("(us-gaap:preferredstockdividendsand\
                          otheradjustments)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.preferred_stock_dividends = \
            self.data_processing(preferred_stock_dividends, xbrl,
                ignore_errors, logger, context_ids)

        net_income_loss_noncontrolling = \
            xbrl.find_all(name=re.compile("(us-gaap:netincomelossattributableto\
                          noncontrollinginterest)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_income_loss_noncontrolling = \
            self.data_processing(net_income_loss_noncontrolling, xbrl,
                                 ignore_errors, logger, context_ids)

        net_income_loss = \
            xbrl.find_all(name=re.compile("^us-gaap:netincomeloss$",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_income_loss = \
            self.data_processing(net_income_loss, xbrl, ignore_errors,
                                 logger, context_ids)

        other_comprehensive_income = \
            xbrl.find_all(name=re.compile("(us-gaap:othercomprehensiveincomeloss\
                          netoftax)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.other_comprehensive_income = \
            self.data_processing(other_comprehensive_income, xbrl,
                ignore_errors, logger, context_ids)

        comprehensive_income = \
            xbrl.find_all(name=re.compile("(us-gaap:comprehensiveincome)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.comprehensive_income = \
            self.data_processing(comprehensive_income, xbrl, ignore_errors,
                                 logger, context_ids)

        comprehensive_income_parent = \
            xbrl.find_all(name=re.compile("(us-gaap:comprehensiveincomenetof"
                          "tax)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.comprehensive_income_parent = \
            self.data_processing(comprehensive_income_parent, xbrl,
                                 ignore_errors, logger, context_ids)

        comprehensive_income_interest = \
            xbrl.find_all(name=re.compile("(us-gaap:comprehensiveincomenetoftax\
                          attributabletononcontrollinginterest)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.comprehensive_income_interest = \
            self.data_processing(comprehensive_income_interest, xbrl,
                                 ignore_errors, logger, context_ids)

        # Cash flow statements #
        net_cash_flows_operating = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          operatingactivities)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_operating = \
            self.data_processing(net_cash_flows_operating, xbrl, ignore_errors,
                                 logger, context_ids)

        net_cash_flows_investing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          investingactivities)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_investing = \
            self.data_processing(net_cash_flows_investing, xbrl, ignore_errors,
                                logger, context_ids)

        net_cash_flows_financing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          financingactivities)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_financing = \
            self.data_processing(net_cash_flows_financing, xbrl, ignore_errors,
                                logger, context_ids)

        net_cash_flows_operating_continuing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          operatingactivitiescontinuingoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_operating_continuing = \
            self.data_processing(net_cash_flows_operating_continuing, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_investing_continuing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          investingactivitiescontinuingoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_investing_continuing = \
            self.data_processing(net_cash_flows_investing_continuing, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_financing_continuing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          financingactivitiescontinuingoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_financing_continuing = \
            self.data_processing(net_cash_flows_financing_continuing, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_operating_discontinued = \
            xbrl.find_all(name=re.compile("(us-gaap:cashprovidedbyusedin\
                          operatingactivitiesdiscontinuedoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_operating_discontinued = \
            self.data_processing(net_cash_flows_operating_discontinued, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_investing_discontinued = \
            xbrl.find_all(name=re.compile("(us-gaap:cashprovidedbyusedin\
                          investingactivitiesdiscontinuedoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_investing_discontinued = \
            self.data_processing(net_cash_flows_investing_discontinued, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_discontinued = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          discontinuedoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_discontinued = \
            self.data_processing(net_cash_flows_discontinued, xbrl,
                                 ignore_errors, logger, context_ids)

        common_shares_outstanding = \
            xbrl.find_all(name=re.compile("(us-gaap:commonstockshares\
                          outstanding)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.common_shares_outstanding = \
            self.data_processing(common_shares_outstanding, xbrl,
                                 ignore_errors, logger, context_ids)

        common_shares_issued = \
            xbrl.find_all(name=re.compile("(us-gaap:commonstockshares\
                          issued)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.common_shares_issued = \
            self.data_processing(common_shares_issued, xbrl,
                                 ignore_errors, logger, context_ids)

        common_shares_authorized = \
            xbrl.find_all(name=re.compile("(us-gaap:commonstockshares\
                          authorized)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.common_shares_authorized = \
            self.data_processing(common_shares_authorized, xbrl,
                                 ignore_errors, logger, context_ids)

        return gaap_obj

    @classmethod
    def parseDEI(self,
                 xbrl,
                 ignore_errors=0):
        """
        Parse DEI from our XBRL soup and return a DEI object.
        """
        dei_obj = DEI()

        if ignore_errors == 2:
            logging.basicConfig(filename='/tmp/xbrl.log',
                level=logging.ERROR,
                format='%(asctime)s %(levelname)s %(name)s %(message)s')
            logger = logging.getLogger(__name__)
        else:
            logger = None

        trading_symbol = xbrl.find_all(name=re.compile("(dei:tradingsymbol)",
            re.IGNORECASE | re.MULTILINE))
        dei_obj.trading_symbol = \
            self.data_processing(trading_symbol, xbrl,
                                 ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        company_name = xbrl.find_all(name=re.compile("(dei:entityregistrantname)",
            re.IGNORECASE | re.MULTILINE))
        dei_obj.company_name = \
            self.data_processing(company_name, xbrl,
                                 ignore_errors, logger,
                                 options={'type': 'String',
                                          'no_context': True})

        shares_outstanding = xbrl.find_all(name=re.compile("(dei:entitycommonstocksharesoutstanding)",
            re.IGNORECASE | re.MULTILINE))
        dei_obj.shares_outstanding = \
            self.data_processing(shares_outstanding, xbrl,
                                 ignore_errors, logger,
                                 options={'type': 'Number',
                                          'no_context': True})

        public_float = xbrl.find_all(name=re.compile("(dei:entitypublicfloat)",
            re.IGNORECASE | re.MULTILINE))
        dei_obj.public_float = \
            self.data_processing(public_float, xbrl,
                                 ignore_errors, logger,
                                 options={'type': 'Number',
                                          'no_context': True})

        return dei_obj

    @classmethod
    def parseCustom(self,
                    xbrl,
                    ignore_errors=0):
        """
        Parse company custom entities from XBRL and return an Custom object.
        """
        custom_obj = Custom()

        custom_data = xbrl.find_all(re.compile('^((?!(us-gaap|dei|xbrll|xbrldi)).)*:\s*',
            re.IGNORECASE | re.MULTILINE))

        elements = {}
        for data in custom_data:
            if XBRLParser().is_number(data.text):
                setattr(custom_obj, data.name.split(':')[1], data.text)

        return custom_obj

    @staticmethod
    def trim_decimals(s, precision=-3):
        """
        Convert from scientific notation using precision
        """
        encoded = s.encode('ascii', 'ignore')
        str_val = ""
        if six.PY3:
            str_val = str(encoded, encoding='ascii', errors='ignore')[:precision]
        else:
            # If precision is 0, this must be handled seperately
            if precision == 0:
                str_val = str(encoded)
            else:
                str_val = str(encoded)[:precision]
        if len(str_val) > 0:
            return float(str_val)
        else:
            return 0

    @staticmethod
    def is_number(s):
        """
        Test if value is numeric
        """
        try:
            s = float(s)
            return True
        except ValueError:
            return False

    @classmethod
    def data_processing(self,
                        elements,
                        xbrl,
                        ignore_errors,
                        logger,
                        context_ids=[],
                        **kwargs):
        """
        Process a XBRL tag object and extract the correct value as
        stated by the context.
        """
        options = kwargs.get('options', {'type': 'Number',
                                         'no_context': False})

        if options['type'] == 'String':
            if len(elements) > 0:
                    return elements[0].text

        if options['no_context'] == True:
            if len(elements) > 0 and XBRLParser().is_number(elements[0].text):
                    return elements[0].text

        try:

            # Extract the correct values by context
            correct_elements = []
            for element in elements:
                std = element.attrs['contextref']
                if std in context_ids:
                    correct_elements.append(element)
            elements = correct_elements

            if len(elements) > 0 and XBRLParser().is_number(elements[0].text):
                decimals = elements[0].attrs['decimals']
                if decimals is not None:
                    attr_precision = decimals
                    if xbrl.precision != 0 \
                    and xbrl.precison != attr_precision:
                        xbrl.precision = attr_precision
                if elements:
                    return XBRLParser().trim_decimals(elements[0].text,
                        int(xbrl.precision))
                else:
                    return 0
            else:
                return 0
        except Exception as e:
            if ignore_errors == 0:
                raise XBRLParserException('value extraction error')
            elif ignore_errors == 1:
                return 0
            elif ignore_errors == 2:
                logger.error(str(e) + " error at " +
                    ''.join(elements[0].text))


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
                tag_name = re.findall(r'(?i)<*>', token)[0]
                if tag_name.upper() not in closing_tags:
                    last_open_tag = tag_name
            new_fh.write(token)
        new_fh.seek(0)
        self.fh = new_fh


class XBRL(object):
    def __str__(self):
        return ""


# Base GAAP object
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
                 net_income_loss=0.0,
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
                 net_cash_flows_discontinued=0.0,
                 common_shares_outstanding=0.0,
                 common_shares_issued=0.0,
                 common_shares_authorized=0.0):
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
        self.stockholders_equity = stockholders_equity
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
        self.net_income_loss = net_income_loss
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
        self.common_shares_outstanding = common_shares_outstanding
        self.common_shares_issued = common_shares_issued
        self.common_shares_authorized = common_shares_authorized


class GAAPSerializer(Schema):
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
    net_income_parent = fields.Number()
    net_income_loss = fields.Number()
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
    common_shares_outstanding = fields.Number()
    common_shares_issued = fields.Number()
    common_shares_authorized = fields.Number()


# Base DEI object
class DEI(object):
    def __init__(self,
                 trading_symbol='',
                 company_name='',
                 shares_outstanding=0.0,
                 public_float=0.0):
        self.trading_symbol = trading_symbol
        self.company_name = company_name
        self.shares_outstanding = shares_outstanding
        self.public_float = public_float


class DEISerializer(Schema):
    trading_symbol = fields.String()
    company_name = fields.String()
    shares_outstanding = fields.Number()
    public_float = fields.Number()


# Base Custom object
class Custom(object):

    def __init__(self):
        return None

    def __call__(self):
        return self.__dict__.items()
