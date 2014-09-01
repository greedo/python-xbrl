import os
import sys
sys.path.insert(0, os.path.abspath('python-xbrl'))
import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from xbrl import soup_maker, XBRLParser, XBRLParserException, GAAP, GAAPSerializer

def test_parse_empty_file():
    xbrl_parser = XBRLParser()
    file_to_parse = "tests/nothing.xml"
    with pytest.raises(XBRLParserException):
        xbrl_parser.parse(file(file_to_parse))

def test_parse_GAAP10Q():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/sam-20130629.xml"
    xbrl = xbrl_parser.parse(file(file_to_parse))
    gaap_obj = xbrl_parser.parseGAAP(xbrl, str(file_to_parse.split("-")[1].split(".")[0][:4] + file_to_parse.split("-")[1].split(".")[0][4:6] + file_to_parse.split("-")[1].split(".")[0][6:8]), "10-K", "current")

    serialized = GAAPSerializer(gaap_obj)

    assert serialized.data['liabilities'] == 98032.0
    assert serialized.data['net_cash_flows_financing_continuing'] == 0.0
    assert serialized.data['revenue'] == 0.0
    assert serialized.data['income_tax_expense_benefit'] == 12107.0
    assert serialized.data['income_from_equity_investments'] == 0.0
    assert serialized.data['preferred_stock_dividends'] == 0.0
    assert serialized.data['redeemable_noncontrolling_interest'] == 0.0
    assert serialized.data['extraordary_items_gain_loss'] == 0.0
    assert serialized.data['temporary_equity'] == 0.0
    assert serialized.data['costs_and_expenses'] == 0.0
    assert serialized.data['non_current_assets'] == 5417.0
    assert serialized.data['net_cash_flows_discontinued'] == 0.0
    assert serialized.data['income_loss'] == 19715.0
    assert serialized.data['liabilities_and_equity'] == 60263.0
    assert serialized.data['other_operating_income'] == 0.0
    assert serialized.data['operating_income_loss'] == 0.0
    assert serialized.data['net_income_parent'] == 0.0
    assert serialized.data['equity'] == 0.0
    assert serialized.data['net_cash_flows_operating_discontinued'] == 0.0
    assert serialized.data['cost_of_revenue'] == 0.0
    assert serialized.data['operating_expenses'] == 65084.0
    assert serialized.data['noncurrent_liabilities'] == 0.0
    assert serialized.data['current_liabilities'] == 0.0
    assert serialized.data['net_cash_flows_investing'] == 0.0
    assert serialized.data['stockholders_equity'] == 253536.0
    assert serialized.data['net_income_loss'] == 19715.0
    assert serialized.data['net_cash_flows_investing_continuing'] == 0.0
    assert serialized.data['nonoperating_income_loss'] == 0.0
    assert serialized.data['net_cash_flows_financing'] == 0.0
    assert serialized.data['net_income_shareholders'] == 0.0
    assert serialized.data['comprehensive_income'] == 19715.0
    assert serialized.data['equity_attributable_interest'] == 0.0
    assert serialized.data['commitments_and_contingencies'] == 0.0
    assert serialized.data['comprehensive_income_parent'] == 19715.0
    assert serialized.data['income_before_equity_investments'] == 31822.0
    assert serialized.data['comprehensive_income_interest'] == 0.0
    assert serialized.data['other_comprehensive_income'] == 0.0
    assert serialized.data['equity_attributable_parent'] == 0.0
    assert serialized.data['assets'] == 5417.0
    assert serialized.data['gross_profit'] == 97132.0
    assert serialized.data['net_cash_flows_operating_continuing'] == 0.0
    assert serialized.data['current_assets'] == 0.0
    assert serialized.data['interest_and_debt_expense'] == 0.0
    assert serialized.data['net_income_loss_noncontrolling'] == 0.0
    assert serialized.data['net_cash_flows_operating'] == 0.0

def test_parse_GAAP10K():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/sam-20131228.xml"
    xbrl = xbrl_parser.parse(file(file_to_parse))
    gaap_obj = xbrl_parser.parseGAAP(xbrl, str(file_to_parse.split("-")[1].split(".")[0][:4] + file_to_parse.split("-")[1].split(".")[0][4:6] + file_to_parse.split("-")[1].split(".")[0][6:8]), "10-K", "current")

    serialized = GAAPSerializer(gaap_obj)

    assert serialized.data['liabilities'] == 104377.0
    assert serialized.data['net_cash_flows_financing_continuing'] == 0.0
    assert serialized.data['revenue'] == 0.0
    assert serialized.data['income_tax_expense_benefit'] == 0.0
    assert serialized.data['income_from_equity_investments'] == 0.0
    assert serialized.data['preferred_stock_dividends'] == 0.0
    assert serialized.data['redeemable_noncontrolling_interest'] == 0.0
    assert serialized.data['extraordary_items_gain_loss'] == 0.0
    assert serialized.data['temporary_equity'] == 0.0
    assert serialized.data['costs_and_expenses'] == 0.0
    assert serialized.data['non_current_assets'] == 9556.0
    assert serialized.data['net_cash_flows_discontinued'] == 0.0
    assert serialized.data['income_loss'] == 29120.0
    assert serialized.data['liabilities_and_equity'] == 69900.0
    assert serialized.data['other_operating_income'] == 0.0
    assert serialized.data['operating_income_loss'] == 0.0
    assert serialized.data['net_income_parent'] == 0.0
    assert serialized.data['equity'] == 0.0
    assert serialized.data['net_cash_flows_operating_discontinued'] == 0.0
    assert serialized.data['cost_of_revenue'] == 0.0
    assert serialized.data['operating_expenses'] == 0.0
    assert serialized.data['noncurrent_liabilities'] == 0.0
    assert serialized.data['current_liabilities'] == 0.0
    assert serialized.data['net_cash_flows_investing'] == 0.0
    assert serialized.data['stockholders_equity'] == 302085.0
    assert serialized.data['net_income_loss'] == 18079.0
    assert serialized.data['net_cash_flows_investing_continuing'] == 0.0
    assert serialized.data['nonoperating_income_loss'] == 0.0
    assert serialized.data['net_cash_flows_financing'] == 0.0
    assert serialized.data['net_income_shareholders'] == 0.0
    assert serialized.data['comprehensive_income'] == 0.0
    assert serialized.data['equity_attributable_interest'] == 0.0
    assert serialized.data['commitments_and_contingencies'] == 0.0
    assert serialized.data['comprehensive_income_parent'] == 0.0
    assert serialized.data['income_before_equity_investments'] == 0.0
    assert serialized.data['comprehensive_income_interest'] == 0.0
    assert serialized.data['other_comprehensive_income'] == 0.0
    assert serialized.data['equity_attributable_parent'] == 0.0
    assert serialized.data['assets'] == 1050.0
    assert serialized.data['gross_profit'] == 104628.0
    assert serialized.data['net_cash_flows_operating_continuing'] == 0.0
    assert serialized.data['current_assets'] == 0.0
    assert serialized.data['interest_and_debt_expense'] == 0.0
    assert serialized.data['net_income_loss_noncontrolling'] == 0.0
    assert serialized.data['net_cash_flows_operating'] == 0.0
