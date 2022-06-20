#! /usr/bin/env python
# encoding: utf-8

from xbrl import XBRLParser
from xbrl import GAAP
from xbrl import GAAPSerializer
from xbrl import DEISerializer
from xbrl import XBRLParserException
import pytest
import sys
import os
import six

try:
    import __pypy__
except ImportError:
    __pypy__ = None

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

sys.path.insert(0, os.path.abspath('python-xbrl'))


def test_parse_empty_file():
    xbrl_parser = XBRLParser()
    file_to_parse = "tests/nothing.xml"
    with pytest.raises(XBRLParserException):
        xbrl_parser.parse(file_to_parse)


def test_open_file_handle():
    xbrl_parser = XBRLParser()
    file_to_parse = "tests/sam-20130629.xml"
    try:
        xbrl_parser.parse(file(file_to_parse))
    except NameError:
        pass


def test_parse_GAAP10Q_RRDonnelley():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/sam-20130629.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 98032.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 12107.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 5417.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == 19715.0
    assert result['liabilities_and_equity'] == 60263.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 0.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 65084.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 253536.0
    assert result['net_income_loss'] == 19715.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == 19715.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == 19715.0
    assert result['income_before_equity_investments'] == 31822.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 376766.0
    assert result['gross_profit'] == 97132.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 138996.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0


def test_parse_GAAP10K_RRDonnelley():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/sam-20131228.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 104377.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 0.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 9556.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == 29120.0
    assert result['liabilities_and_equity'] == 69900.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 0.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 0.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 302085.0
    assert result['net_income_loss'] == 18079.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == 0.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == 0.0
    assert result['income_before_equity_investments'] == 0.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 444075.0
    assert result['gross_profit'] == 104628.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 164278.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10K_Webfilings():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/goog-20131231.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 3755.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 0.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 38034.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == 0.0
    assert result['liabilities_and_equity'] == 110920.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 975.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 0.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 87309.0
    assert result['net_income_loss'] == 0.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == 0.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == 0.0
    assert result['income_before_equity_investments'] == 0.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 110920.0
    assert result['gross_profit'] == 0.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 72886.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10Q_Webfilings():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/goog-20140630.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 3683.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 913.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 11697.0
    assert result['non_current_assets'] == 43703.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == 3490.0
    assert result['liabilities_and_equity'] == 121608.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 0.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 0.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 95749.0
    assert result['net_income_loss'] == 3422.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == 3579.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == 3579.0
    assert result['income_before_equity_investments'] == 4403.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 121608.0
    assert result['gross_profit'] == 0.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 77905.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10Q_Rivet():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/c289-20140503.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 12535.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 14.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 708.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == -983.0
    assert result['liabilities_and_equity'] == 13261.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 0.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 3497.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 726.0
    assert result['net_income_loss'] == -983.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == -977.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == -977.0
    assert result['income_before_equity_investments'] == -969.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 13261.0
    assert result['gross_profit'] == 2687.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 10747.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10K_Rivet():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/rsh-20131231.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 234.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 42.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 583.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == -1914.0
    assert result['liabilities_and_equity'] == 15912.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 0.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 4445.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 2064.0
    assert result['net_income_loss'] == -1914.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == -1899.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == -1899.0
    assert result['income_before_equity_investments'] == -1872.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 15912.0
    assert result['gross_profit'] == 2784.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 13330.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10Q_QXInteractive():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/aaoi-20140630.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 5606.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 85.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 978.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == 1730.0
    assert result['liabilities_and_equity'] == 153524.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 0.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 9458.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 111781.0
    assert result['net_income_loss'] == 1919.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == 2058.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == 2058.0
    assert result['income_before_equity_investments'] == 0.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 153524.0
    assert result['gross_profit'] == 11188.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 106114.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10K_ThomsonReuters():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/aaoi-20131231.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 39057.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 0.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 177.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == -297.0
    assert result['liabilities_and_equity'] == 111057.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 0.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 6973.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 63077.0
    assert result['net_income_loss'] == -520.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == 0.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == 0.0
    assert result['income_before_equity_investments'] == 0.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 111057.0
    assert result['gross_profit'] == 6676.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 77936.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10Q_Fujitsu():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/aaww-20140630.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 233079.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == -23815.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 414512.0
    assert result['non_current_assets'] == 3568474.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == 26657.0
    assert result['liabilities_and_equity'] == 4100064.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 4870.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 0.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 1355551.0
    assert result['net_income_loss'] == 0.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == -515.0
    assert result['equity_attributable_interest'] == 0.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == -515.0
    assert result['income_before_equity_investments'] == 0.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 4100064.0
    assert result['gross_profit'] == 0.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 531590.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10K_Fujitsu():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/aaww-20131231.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 194292.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 0.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 3124306.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == 0.0
    assert result['liabilities_and_equity'] == 3718259.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 4870.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 0.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 1317773.0
    assert result['net_income_loss'] == 0.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == 0.0
    assert result['equity_attributable_interest'] == 4352.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == 0.0
    assert result['income_before_equity_investments'] == 0.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 3718259.0
    assert result['gross_profit'] == 0.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 593953.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_income_loss_noncontrolling'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_GAAP10Q_Ez_XBRL():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/ggho-20140930.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                     str(file_to_parse
                                         .split("-")[1].split(".")[0][:4] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][4:6] +
                                         file_to_parse.split("-")[1]
                                         .split(".")[0][6:8]),
                                     "current")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

    assert result['liabilities'] == 34273.0
    assert result['net_cash_flows_financing_continuing'] == 0.0
    assert result['revenue'] == 0.0
    assert result['income_tax_expense_benefit'] == 127.0
    assert result['income_from_equity_investments'] == 0.0
    assert result['preferred_stock_dividends'] == 0.0
    assert result['redeemable_noncontrolling_interest'] == 0.0
    assert result['extraordary_items_gain_loss'] == 0.0
    assert result['temporary_equity'] == 0.0
    assert result['costs_and_expenses'] == 0.0
    assert result['non_current_assets'] == 58615.0
    assert result['net_cash_flows_discontinued'] == 0.0
    assert result['income_loss'] == -7593.0
    assert result['liabilities_and_equity'] == 79451.0
    assert result['other_operating_income'] == 0.0
    assert result['operating_income_loss'] == 0.0
    assert result['net_income_parent'] == 0.0
    assert result['equity'] == 0.0
    assert result['net_cash_flows_operating_discontinued'] == 0.0
    assert result['cost_of_revenue'] == 0.0
    assert result['operating_expenses'] == 13026.0
    assert result['noncurrent_liabilities'] == 0.0
    assert result['current_liabilities'] == 0.0
    assert result['net_cash_flows_investing'] == 0.0
    assert result['stockholders_equity'] == 30543.0
    assert result['net_income_loss'] == -8642.0
    assert result['net_cash_flows_investing_continuing'] == 0.0
    assert result['nonoperating_income_loss'] == 0.0
    assert result['net_cash_flows_financing'] == 0.0
    assert result['net_income_shareholders'] == 0.0
    assert result['comprehensive_income'] == 0.0
    assert result['equity_attributable_interest'] == 309.0
    assert result['commitments_and_contingencies'] == 0.0
    assert result['comprehensive_income_parent'] == 0.0
    assert result['income_before_equity_investments'] == -8531.0
    assert result['comprehensive_income_interest'] == 0.0
    assert result['other_comprehensive_income'] == 0.0
    assert result['equity_attributable_parent'] == 0.0
    assert result['assets'] == 79451.0
    assert result['gross_profit'] == 5433.0
    assert result['net_cash_flows_operating_continuing'] == 0.0
    assert result['current_assets'] == 20836.0
    assert result['interest_and_debt_expense'] == 0.0
    assert result['net_cash_flows_operating'] == 0.0
    assert result['common_shares_outstanding'] == 0.0
    assert result['common_shares_issued'] == 0.0
    assert result['common_shares_authorized'] == 0.0


def test_parse_DEI10Q_RRDonnelley():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/sam-20130629.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    dei_obj = xbrl_parser.parseDEI(xbrl)

    serializer = DEISerializer()
    result = serializer.dump(dei_obj)

    assert result['trading_symbol'] == "SAM"
    assert result['company_name'] == "BOSTON BEER CO INC"
    assert result['shares_outstanding'] == 4007355.0
    assert result['public_float'] == 0.0


def test_parse_Custom10Q_RRDonnelley():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/sam-20130629.xml"
    xbrl = xbrl_parser.parse(file_to_parse)
    custom_obj = xbrl_parser.parseCustom(xbrl)

    if six.PY3:

        result = len(custom_obj())

        assert result == 13

    if six.PY2 and not __pypy__:

        result = custom_obj()

        assert result[0] == ('conversionofclassbcommonstocktoclassacommonstockshares', '100000')
        assert result[1] == ('percentageofproductionvolumes', '0.90')
        assert result[2] == ('sharebasedcompensationarrangementbysharebasedpaymentawardoptionstovestineachtranche', '5000')
        assert result[3] == ('weightedaveragenumberofsharesoutstandingbasicincludingnonvestedparticipatingsecurities', '12866000')
        assert result[4] == ('incrementalcommonsharesattributabletoconversionofcommonstock', '4007000')
        assert result[5] == ('sharebasedcompensationarrangementbysharebasedpaymentawardinvestmentsharesweightedaveragegrantdat', '59.62')
        assert result[6] == ('incomeallocatedtoequityinstrumentsotherthanoptionnonvested', '7000')
        assert result[7] == ('netproceedsfromsaleofinvestmentshares', '531000')
        assert result[8] == ('weightedaveragenumberofbasicsharesoutstandingequityinstrumentsotherthanoptionnonvested', '94000')
        assert result[9] == ('sharebasedcompensationarrangementbysharebasedpaymentawardemployeeinvestmentsharespurchase', '12894')
        assert result[10] == ('provisionforreductionofdoubtfulaccounts', '-28000')
        assert result[11] == ('receiptofgovernmentgrantsforfacilitiesexpansion', '770000')
        assert result[12] == ('netincomelossallocatedtoequityinstrumentsotherthanoptionnonvested', '-143000')
