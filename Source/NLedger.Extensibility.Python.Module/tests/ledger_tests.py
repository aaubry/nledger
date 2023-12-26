####################################################################################
# Copyright (c) 2015-2023, Dmitry Merzlyakov.  All rights reserved.
# Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
# 
# This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
# Copyright (c) 2003-2023, John Wiegley.  All rights reserved.
# See LICENSE.LEDGER file included with the distribution for details and disclaimer.
####################################################################################

# NLedger Python Extensibility module tests (ledger)
# Usage: [path_to_python_executable] ledger_tests.py

# If it is run on development environment, it uses the latest compiled binaries and module source code (no needs to install the module for testing)
# Otherwise, it imports module that was previously installed to the specified Python environment
# Check output messages to ensure what was tested

from typing import Iterable, Tuple
import unittest
import os
import os.path
import sys
import re
import collections

# Find path to the latest NLedger.Extensibility.Python.dll on development environment. 
# It returns path to either debug or release binaries depending what was built later.
# If binaries are not found (so, it is likely non-development environment), the function returns None
def get_nledger_dll_path():
    debugDLL = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../NLedger.Extensibility.Python/bin/Debug/netstandard2.0/NLedger.Extensibility.Python.dll'))
    releaseDLL = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../NLedger.Extensibility.Python/bin/Release/netstandard2.0/NLedger.Extensibility.Python.dll'))

    if os.path.isfile(releaseDLL):
        if os.path.isfile(debugDLL):
            debugBinDate = os.path.getmtime(debugDLL)
            releaseBinDate = os.path.getmtime(releaseDLL)
            if debugBinDate < releaseBinDate:
                return releaseDLL
            else:
                return debugDLL
        else:
            return releaseDLL
    else:
        if os.path.isfile(debugDLL):
            return debugDLL

    return None

def get_drewr3_dat_filename():
    filename = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'drewr3.dat'))
    if not os.path.isfile(filename):
        raise Exception('Cannot find file ' + filename)
    return filename

# Detecting environment configuration: if development binaries found, configure the module to use them
nledger_dll_path = get_nledger_dll_path()
if nledger_dll_path:
    print("Development environment detected. Found NLedger Python dll: " + nledger_dll_path)
    os.environ["nledger_extensibility_python_dll_path"] = nledger_dll_path

    # Before importing ledger module, it is important to add path to source code to the first position to override already installed module
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'src'))

import ledger
from ledger import Amount, Position, TransactionBase, Value
print("Module ledger is properly imported")
print("Path to NLedger Python dll: " + ledger.nledger_extensibility_python_dll_path)

from datetime import datetime
from datetime import date
from System import DateTime
from NLedger.Utility import Date

# Test classes

class LedgerModuleTests(unittest.TestCase):

    def test_commodity_scope_attributes(self):

        self.assertEqual(0, ledger.COMMODITY_STYLE_DEFAULTS)
        self.assertEqual(1, ledger.COMMODITY_STYLE_SUFFIXED)
        self.assertEqual(2, ledger.COMMODITY_STYLE_SEPARATED)
        self.assertEqual(4, ledger.COMMODITY_STYLE_DECIMAL_COMMA)
        self.assertEqual(8, ledger.COMMODITY_STYLE_THOUSANDS)
        self.assertEqual(0x10, ledger.COMMODITY_NOMARKET)
        self.assertEqual(0x20, ledger.COMMODITY_BUILTIN)
        self.assertEqual(0x40, ledger.COMMODITY_WALKED)
        self.assertEqual(0x80, ledger.COMMODITY_KNOWN)
        self.assertEqual(0x100, ledger.COMMODITY_PRIMARY)
        self.assertEqual(0x1000, ledger.COMMODITY_STYLE_TIME_COLON)

        self.assertIsNotNone(0x1000, ledger.commodities)
        self.assertIsInstance(ledger.commodities, ledger.CommodityPool)
        self.assertEqual("<class 'ledger.CommodityPool'>", str(type(ledger.commodities)))

    def test_account_scope_attributes(self):
        self.assertEqual(0x01, ledger.ACCOUNT_EXT_SORT_CALC)
        self.assertEqual(0x02, ledger.ACCOUNT_EXT_HAS_NON_VIRTUALS)
        self.assertEqual(0x04, ledger.ACCOUNT_EXT_HAS_UNB_VIRTUALS)
        self.assertEqual(0x08, ledger.ACCOUNT_EXT_AUTO_VIRTUALIZE)
        self.assertEqual(0x10, ledger.ACCOUNT_EXT_VISITED)
        self.assertEqual(0x20, ledger.ACCOUNT_EXT_MATCHING)
        self.assertEqual(0x40, ledger.ACCOUNT_EXT_TO_DISPLAY)
        self.assertEqual(0x80, ledger.ACCOUNT_EXT_DISPLAYED)

        self.assertEqual(0x00, ledger.ACCOUNT_NORMAL)
        self.assertEqual(0x01, ledger.ACCOUNT_KNOWN)
        self.assertEqual(0x02, ledger.ACCOUNT_TEMP)
        self.assertEqual(0x04, ledger.ACCOUNT_GENERATED)

    def test_journalitem_scope_attributes(self):
        self.assertEqual(0x00, ledger.ITEM_NORMAL)
        self.assertEqual(0x01, ledger.ITEM_GENERATED)
        self.assertEqual(0x02, ledger.ITEM_TEMP)

    def test_postingxdata_attributes(self):
        self.assertEqual(0x01, ledger.POST_EXT_RECEIVED)
        self.assertEqual(0x02, ledger.POST_EXT_HANDLED)
        self.assertEqual(0x04, ledger.POST_EXT_DISPLAYED)
        self.assertEqual(0x08, ledger.POST_EXT_DIRECT_AMT)
        self.assertEqual(0x10, ledger.POST_EXT_SORT_CALC)
        self.assertEqual(0x20, ledger.POST_EXT_COMPOUND)
        self.assertEqual(0x40, ledger.POST_EXT_VISITED)
        self.assertEqual(0x80, ledger.POST_EXT_MATCHES)
        self.assertEqual(0x100, ledger.POST_EXT_CONSIDERED)

    def test_posting_attributes(self):
        self.assertEqual(0x10, ledger.POST_VIRTUAL)
        self.assertEqual(0x20, ledger.POST_MUST_BALANCE)
        self.assertEqual(0x40, ledger.POST_CALCULATED)
        self.assertEqual(0x80, ledger.POST_COST_CALCULATED)

    def test_annotation_attributes(self):
        self.assertEqual(0x01, ledger.ANNOTATION_PRICE_CALCULATED)
        self.assertEqual(0x02, ledger.ANNOTATION_PRICE_FIXATED)
        self.assertEqual(0x04, ledger.ANNOTATION_PRICE_NOT_PER_UNIT)
        self.assertEqual(0x08, ledger.ANNOTATION_DATE_CALCULATED)
        self.assertEqual(0x10, ledger.ANNOTATION_TAG_CALCULATED)
        self.assertEqual(0x20, ledger.ANNOTATION_VALUE_EXPR_CALCULATED)

    def test_session_attribute(self):
        self.assertIsInstance(ledger.session, ledger.Session)

    def test_times_parse_datetime(self):
        self.assertEqual(datetime(2021, 5, 22, 18, 55, 59), ledger.parse_datetime("2021/5/22 18:55:59"))

    def test_times_parse_date(self):
        self.assertEqual(date(2021, 5, 22), ledger.parse_date("2021/5/22"))

    def test_config_attribute(self):
        self.assertIsInstance(ledger.config, ledger.Config)

    def test_execute_command(self):
        ledger.session.close_journal_files()
        filename = get_drewr3_dat_filename()
        jrn = ledger.read_journal(filename)
        
        cmd_result = ledger.execute_command("bal ^Expenses")
        cmd_output = cmd_result.Output
        cmd_error = cmd_result.Error
        self.assertIsInstance(cmd_output, str)
        self.assertIsInstance(cmd_error, str)
        self.assertTrue(cmd_output)     # contains some text
        self.assertFalse(cmd_error)     # empty string

        cmd_result = ledger.execute_command("bal ^Expenses", False)
        cmd_output = cmd_result.Output
        cmd_error = cmd_result.Error
        self.assertIsInstance(cmd_output, str)
        self.assertIsInstance(cmd_error, str)
        self.assertTrue(cmd_output)     # contains some text
        self.assertFalse(cmd_error)     # empty string

        cmd_result = ledger.execute_command(["bal", "^Expenses"])
        cmd_output = cmd_result.Output
        cmd_error = cmd_result.Error
        self.assertIsInstance(cmd_output, str)
        self.assertIsInstance(cmd_error, str)
        self.assertTrue(cmd_output)     # contains some text
        self.assertFalse(cmd_error)     # empty string

        cmd_result = ledger.execute_command(["bal", "^Expenses"], False)
        cmd_output = cmd_result.Output
        cmd_error = cmd_result.Error
        self.assertIsInstance(cmd_output, str)
        self.assertIsInstance(cmd_error, str)
        self.assertTrue(cmd_output)     # contains some text
        self.assertFalse(cmd_error)     # empty string

    def test_session_read_journal(self):
        ledger.session.close_journal_files()
        filename = get_drewr3_dat_filename()
        jrn = ledger.read_journal(filename)
        self.assertIsInstance(jrn, ledger.Journal)

    def test_session_read_journal_from_string(self):
        data = """
        
2010/12/01 * Checking balance
  Assets:Checking                   $1,000.00
  Equity:Opening Balances
        
        """
        jrn = ledger.read_journal_from_string(data)
        self.assertIsInstance(jrn, ledger.Journal)

    def test_to_pdate(self):

        self.assertIsNone(ledger.to_pdate(None))

        ndatetime = DateTime(2021, 5, 22, 23, 55, 50, 99)
        self.assertEqual(date(2021, 5, 22), ledger.to_pdate(ndatetime))

        ndate = Date(2021, 5, 22)
        self.assertEqual(date(2021, 5, 22), ledger.to_pdate(ndate))

        pdatetime = datetime(2021, 5, 22, 23, 55, 50, 99)
        self.assertEqual(date(2021, 5, 22), ledger.to_pdate(pdatetime))

        pdate = date(2021, 5, 22)
        self.assertEqual(date(2021, 5, 22), ledger.to_pdate(pdate))

    def test_to_pdatetime(self):

        self.assertIsNone(ledger.to_pdatetime(None))

        ndatetime = DateTime(2021, 5, 22, 23, 55, 50, 99)
        self.assertEqual(datetime(2021, 5, 22, 23, 55, 50, 99000), ledger.to_pdatetime(ndatetime))

        ndate = Date(2021, 5, 22)
        self.assertEqual(datetime(2021, 5, 22, 0, 0, 0, 0), ledger.to_pdatetime(ndate))

        pdatetime = datetime(2021, 5, 22, 23, 55, 50, 99)
        self.assertEqual(datetime(2021, 5, 22, 23, 55, 50, 99), ledger.to_pdatetime(pdatetime))

        pdate = date(2021, 5, 22)
        self.assertEqual(datetime(2021, 5, 22, 0, 0, 0, 0), ledger.to_pdatetime(pdate))

    def test_to_ndate(self):

        self.assertEqual(None, ledger.to_ndate(None))

        pdatetime = datetime(2021, 5, 22, 23, 55, 50, 99)
        self.assertEqual(Date(2021, 5, 22), ledger.to_ndate(pdatetime))

        pdate = date(2021, 5, 22)
        self.assertEqual(Date(2021, 5, 22), ledger.to_ndate(pdate))

        ndatetime = DateTime(2021, 5, 22, 23, 55, 50, 99)
        self.assertEqual(Date(2021, 5, 22), ledger.to_ndate(ndatetime))

        ndate = Date(2021, 5, 22)
        self.assertEqual(Date(2021, 5, 22), ledger.to_ndate(ndate))

    def test_to_ndatetime(self):

        self.assertEqual(None, ledger.to_ndatetime(None))

        pdatetime = datetime(2021, 5, 22, 23, 55, 50, 99000)
        self.assertEqual(DateTime(2021, 5, 22, 23, 55, 50, 99), ledger.to_ndatetime(pdatetime))

        pdate = date(2021, 5, 22)
        self.assertEqual(DateTime(2021, 5, 22), ledger.to_ndatetime(pdate))

        ndatetime = DateTime(2021, 5, 22, 23, 55, 50, 99)
        self.assertEqual(DateTime(2021, 5, 22, 23, 55, 50, 99), ledger.to_ndatetime(ndatetime))

        ndate = Date(2021, 5, 22)
        self.assertEqual(DateTime(2021, 5, 22), ledger.to_ndatetime(ndate))

class ConfigTests(unittest.TestCase):

    def test_config_is_atty(self):

        config = ledger.Config()
        is_atty = config.is_atty

        config.is_atty = True
        self.assertTrue(config.is_atty)

        config.is_atty = False
        self.assertFalse(config.is_atty)

        config.is_atty = is_atty

    def test_config_get_env(self):

        ledger.MainApplicationContext.Current.EnvironmentVariables["test-env-var"] = "test-env-val"
        config = ledger.Config()
        self.assertIsNone(config.get_env("this-variable-does-not-exist"))
        self.assertEqual("test-env-val", config.get_env("test-env-var"))

    def test_config_set_env(self):
        ledger.MainApplicationContext.Current.EnvironmentVariables.Remove("test-env-var")
        config = ledger.Config()
        self.assertIsNone(config.get_env("test-env-var"))
        config.set_env("test-env-var", "test-env-val")
        self.assertEqual("test-env-val", config.get_env("test-env-var"))

class ValueListTests(unittest.TestCase):

    def test_valuelist_init_creates_new_collection(self):
        vlist = ledger.ValueList()
        self.assertIsInstance(vlist, ledger.ValueList)
        self.assertIsInstance(vlist.origin, ledger.NetListAdapter[ledger.OriginValue])
        self.assertEqual(0, len(vlist))

    def test_valuelist_init_takes_sequence(self):
        seq = (ledger.Value(5), ledger.Value(10), ledger.Value(15))
        vlist = ledger.ValueList(seq)
        self.assertIsInstance(vlist, ledger.ValueList)
        self.assertIsInstance(vlist.origin, ledger.NetListAdapter[ledger.OriginValue])
        self.assertEqual(3, len(vlist))

    def test_valuelist_init_takes_dotnet_list(self):
        nlist = ledger.NetList[ledger.OriginValue]()
        nlist.Add(ledger.Value(5).origin)
        nlist.Add(ledger.Value(10).origin)
        vlist = ledger.ValueList(nlist)
        self.assertIsInstance(vlist, ledger.ValueList)
        self.assertIsInstance(vlist.origin, ledger.NetListAdapter[ledger.OriginValue])
        self.assertEqual(2, len(vlist))

    def test_valuelist_get_nclass_returns_net_type(self):
        vlist = ledger.ValueList()
        self.assertEqual(str(vlist.get_nclass()), str(ledger.NetListAdapter[ledger.OriginValue]))

    def test_valuelist_to_nitem(self):
        vlist = ledger.ValueList()
        nval = vlist.to_nitem(ledger.Value(10))
        self.assertIsInstance(nval, ledger.OriginValue)
        self.assertEqual(10, nval.AsLong)

    def test_valuelist_to_pitem(self):
        vlist = ledger.ValueList()
        pval = vlist.to_pitem(ledger.OriginValue(10))
        self.assertIsInstance(pval, ledger.Value)
        self.assertEqual(10, pval.to_long())

    def test_valuelist_repr(self):
        vlist = ledger.ValueList()
        self.assertEqual("<ValueList System.Collections.Generic.List`1[NLedger.Values.Value]>", repr(vlist))

    def test_valuelist_len(self):
        vlist = ledger.ValueList()
        self.assertEqual(0, len(vlist))
        vlist.append(ledger.Value(10))
        self.assertEqual(1, len(vlist))

    def test_valuelist_getitem(self):
        vlist = ledger.ValueList((ledger.Value(10), ledger.Value(20)))
        self.assertEqual(10, vlist[0].to_long())
        self.assertEqual(20, vlist[1].to_long())

    def test_valuelist_delitem(self):
        vlist = ledger.ValueList((ledger.Value(10), ledger.Value(20)))
        vlist.pop(1)
        vlist.pop(0)
        self.assertEqual(0, len(vlist))

        vlist = ledger.ValueList((ledger.Value(10), ledger.Value(20)))
        del vlist[1]
        del vlist[0]
        self.assertEqual(0, len(vlist))

    def test_valuelist_setitem(self):
        vlist = ledger.ValueList((ledger.Value(10), ledger.Value(20)))
        self.assertEqual(10, vlist[0].to_long())
        vlist[0] = ledger.Value(30)
        self.assertEqual(30, vlist[0].to_long())

    def test_valuelist_str(self):
        vlist = ledger.ValueList((ledger.Value(10), ledger.Value(20)))
        self.assertEqual("System.Collections.Generic.List`1[NLedger.Values.Value]", str(vlist))

    def test_valuelist_insert(self):
        vlist = ledger.ValueList((ledger.Value(10), ledger.Value(20)))
        vlist.insert(0, ledger.Value(30))
        self.assertEqual(30, vlist[0].to_long())
        self.assertEqual(10, vlist[1].to_long())
        self.assertEqual(20, vlist[2].to_long())

    def test_valuelist_append(self):
        vlist = ledger.ValueList((ledger.Value(10), ledger.Value(20)))
        vlist.append(ledger.Value(30))
        self.assertEqual(10, vlist[0].to_long())
        self.assertEqual(20, vlist[1].to_long())
        self.assertEqual(30, vlist[2].to_long())

# Expressions

class ExprTests(unittest.TestCase):

    def test_expr_constructor(self):
        expr = ledger.Expr()
        self.assertIsInstance(expr, ledger.Expr)

        expr = ledger.Expr("2+2")
        self.assertIsInstance(expr, ledger.Expr)

        expr = ledger.Expr(ledger.OriginExpr())
        self.assertIsInstance(expr, ledger.Expr)

    def test_expr_from_origin(self):
        expr = ledger.Expr.from_origin(ledger.OriginExpr())
        self.assertIsInstance(expr, ledger.Expr)

        expr = ledger.Expr.from_origin(None)
        self.assertIsNone(expr)

    def test_expr_bool(self):
        expr = ledger.Expr()
        self.assertFalse(bool(expr))

        expr = ledger.Expr("2+2")
        self.assertTrue(bool(expr))

    def test_expr_text(self):
        expr = ledger.Expr("2+2")
        self.assertEqual("2+2", expr.text())

    def test_expr_set_text(self):
        expr = ledger.Expr("2+2")
        self.assertEqual("2+2", expr.text())
        expr.set_text("2+2+2")
        self.assertEqual("2+2+2", expr.text())

    def test_expr_call(self):
        expr = ledger.Expr("2+2")
        self.assertEqual(4, expr(ledger.Posting()))

        expr.context = ledger.Posting()
        self.assertEqual(4, expr())

    def test_expr_context(self):
        expr = ledger.Expr()
        self.assertIsNone(expr.context)
        expr.context = ledger.Posting()
        self.assertIsInstance(expr.context, ledger.Posting)

    def test_expr_compile(self):
        expr = ledger.Expr("2+2")
        expr.compile(ledger.Posting())
        self.assertTrue(expr.origin.IsCompiled)

    def test_expr_is_constant(self):
        expr = ledger.Expr("2+2")
        self.assertFalse(expr.is_constant())

        expr = ledger.Expr("2")
        self.assertTrue(expr.is_constant())

# Commodities

class CommodityPoolTests(unittest.TestCase):

    def test_commodity_pool_null_commodity(self):

        null_commodity = ledger.commodities.null_commodity
        self.assertIsNotNone(null_commodity)
        self.assertFalse(bool(null_commodity.symbol))
        self.assertEqual("<class 'ledger.Commodity'>", str(type(null_commodity)))

    def test_commodity_pool_null_commodity(self):

        default_commodity = ledger.commodities.default_commodity
        self.assertIsNone(default_commodity)

    def test_commodity_pool_keep_base(self):

        commodity_pool = ledger.commodities
        keep_base = commodity_pool.keep_base

        commodity_pool.keep_base = True
        self.assertTrue(commodity_pool.keep_base)

        commodity_pool.keep_base = False
        self.assertFalse(commodity_pool.keep_base)

        commodity_pool.keep_base = keep_base
        self.assertEqual(keep_base, commodity_pool.keep_base)

    def test_commodity_pool_price_db(self):

        commodity_pool = ledger.commodities
        price_db = commodity_pool.price_db

        commodity_pool.price_db = "some-price_db"
        self.assertEqual("some-price_db", commodity_pool.price_db)

        commodity_pool.price_db = price_db
        self.assertEqual(price_db, commodity_pool.price_db)

    def test_commodity_pool_quote_leeway(self):

        commodity_pool = ledger.commodities
        quote_leeway = commodity_pool.quote_leeway

        commodity_pool.quote_leeway = 111
        self.assertEqual(111, commodity_pool.quote_leeway)

        commodity_pool.quote_leeway = quote_leeway
        self.assertEqual(quote_leeway, commodity_pool.quote_leeway)

    def test_commodity_pool_get_quotes(self):

        commodity_pool = ledger.commodities
        get_quotes = commodity_pool.get_quotes

        commodity_pool.get_quotes = True
        self.assertTrue(commodity_pool.get_quotes)

        commodity_pool.get_quotes = False
        self.assertFalse(commodity_pool.get_quotes)

        commodity_pool.get_quotes = get_quotes
        self.assertEqual(get_quotes, commodity_pool.get_quotes)

    def test_commodity_pool_create(self):

        commodity_pool = ledger.commodities
        commodity = commodity_pool.create("XYZ1")

        self.assertIsNotNone(commodity)
        self.assertEqual("<class 'ledger.Commodity'>", str(type(commodity)))
        self.assertEqual('"XYZ1"', commodity.symbol)

        annotation = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag"))
        commodity = commodity_pool.create("XYZ2", annotation)

        self.assertIsNotNone(commodity)
        self.assertEqual("<class 'ledger.AnnotatedCommodity'>", str(type(commodity)))
        self.assertEqual('"XYZ2"', commodity.symbol)

    def test_commodity_pool_find_or_create(self):

        commodity_pool = ledger.commodities

        commodity = commodity_pool.find_or_create("XYZ10")
        self.assertIsNotNone(commodity)
        self.assertEqual("<class 'ledger.Commodity'>", str(type(commodity)))
        self.assertEqual('"XYZ10"', commodity.symbol)

        commodity = commodity_pool.find_or_create("XYZ10")
        self.assertIsNotNone(commodity)
        self.assertEqual("<class 'ledger.Commodity'>", str(type(commodity)))
        self.assertEqual('"XYZ10"', commodity.symbol)

        annotation = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag"))

        commodity = commodity_pool.find_or_create("XYZ11", annotation)
        self.assertIsNotNone(commodity)
        self.assertEqual("<class 'ledger.AnnotatedCommodity'>", str(type(commodity)))
        self.assertEqual('"XYZ11"', commodity.symbol)

        commodity = commodity_pool.find_or_create("XYZ11", annotation)
        self.assertIsNotNone(commodity)
        self.assertEqual("<class 'ledger.AnnotatedCommodity'>", str(type(commodity)))
        self.assertEqual('"XYZ11"', commodity.symbol)

    def test_commodity_pool_find(self):

        commodity_pool = ledger.commodities

        commodity = commodity_pool.find("XYZNONE999")
        self.assertIsNone(commodity)

        commodity_pool.find_or_create("XYZ20")
        commodity = commodity_pool.find("XYZ20")
        self.assertIsNotNone(commodity)
        self.assertEqual("<class 'ledger.Commodity'>", str(type(commodity)))
        self.assertEqual('"XYZ20"', commodity.symbol)

        annotation = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag"))
        commodity_pool.find_or_create("XYZ20", annotation)

        commodity = commodity_pool.find("XYZ20", annotation)
        self.assertIsNotNone(commodity)
        self.assertEqual("<class 'ledger.AnnotatedCommodity'>", str(type(commodity)))
        self.assertEqual('"XYZ20"', commodity.symbol)

    def test_commodity_exchange_2(self):

        commodity_pool = ledger.commodities
        commodity = commodity_pool.find_or_create("ZS1")
        amount = ledger.Amount("10")
        commodity_pool.exchange(commodity,amount)

    def test_commodity_exchange_3(self):

        commodity_pool = ledger.commodities
        commodity = commodity_pool.find_or_create("ZS1")
        amount = ledger.Amount("10")
        moment = datetime(2021, 5, 22)
        commodity_pool.exchange(commodity,amount,moment)

    def test_commodity_exchange_6(self):

        commodity_pool = ledger.commodities
        amount = ledger.Amount("10")
        cost = ledger.Amount("20")
        is_per_unit = True
        add_prices = True
        moment = datetime(2021, 5, 22)
        tag = "tag-1"
        commodity_pool.exchange(amount,cost,is_per_unit,add_prices)
        commodity_pool.exchange(amount,cost,is_per_unit,add_prices,moment)
        commodity_pool.exchange(amount,cost,is_per_unit,add_prices,moment,tag)

    def test_commodity_parse_price_directive(self):

        commodity_pool = ledger.commodities
        result1 = commodity_pool.parse_price_directive("2020-01-15 GAL $3")
        result2 = commodity_pool.parse_price_directive("1989/01/15 12:00:00 GAL $3",True)
        result3 = commodity_pool.parse_price_directive("1989/01/15 12:00:00 GAL $3",True,True)

        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertIsNotNone(result3)

        self.assertIsInstance(result1[0], ledger.Commodity)
        self.assertIsInstance(result1[1], ledger.PricePoint)

    def test_commodity_getitem(self):

        commodity_pool = ledger.commodities
        commodity_pool.find_or_create("QA22")

        comm = commodity_pool["QA22"]
        self.assertIsNotNone(comm)
        self.assertIsInstance(comm, ledger.Commodity)
        self.assertEqual('"QA22"', comm.symbol)

        with self.assertRaises(ValueError) as context:
            commodity_pool["non-existing-commodity"]

        self.assertEqual('Could not find commodity non-existing-commodity', str(context.exception))

    def test_commodity_keys(self):

        commodity_pool = ledger.commodities
        commodity_pool.find_or_create("QA22")

        keys = commodity_pool.keys()
        self.assertIsNotNone(keys)
        self.assertIsInstance(keys, list)
        self.assertTrue('QA22' in keys)

    def test_commodity_has_key(self):

        commodity_pool = ledger.commodities
        commodity_pool.find_or_create("QA22")

        self.assertTrue(commodity_pool.has_key("QA22"))
        self.assertFalse(commodity_pool.has_key("non-existing-commodity"))

    def test_commodity_contains(self):

        commodity_pool = ledger.commodities
        commodity_pool.find_or_create("QA22")

        self.assertTrue("QA22" in commodity_pool)
        self.assertFalse("non-existing-commodity" in commodity_pool)

    def test_commodity_values(self):

        commodity_pool = ledger.commodities
        comm = commodity_pool.find_or_create("QA22")

        values = commodity_pool.values()
        self.assertIsNotNone(values)
        self.assertIsInstance(values, list)        
        self.assertTrue(comm in values)

        for val in values:
            self.assertIsInstance(val, ledger.Commodity)

    def test_commodity_items(self):

        commodity_pool = ledger.commodities
        comm = commodity_pool.find_or_create("QA22")

        items = commodity_pool.items()
        self.assertIsNotNone(items)
        self.assertIsInstance(items, list)        
        self.assertTrue(("QA22", comm) in items)

        for val in items:
            self.assertIsInstance(val, Tuple)
            self.assertIsInstance(val[0], str)
            self.assertIsInstance(val[1], ledger.Commodity)

    def test_commodity_iter(self):

        commodity_pool = ledger.commodities
        comm = commodity_pool.find_or_create("QA22")

        for k in commodity_pool:
            self.assertIsNotNone(k)
            self.assertIsInstance(k, str)
            self.assertTrue(commodity_pool.has_key(k))

class AnnotationTests(unittest.TestCase):

    def test_annotation_eq(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, None))
        annotation2 = ledger.Annotation(ledger.OriginAnnotation(None, None, None))
        self.assertTrue(annotation1 == annotation2)
        self.assertFalse(annotation1 != annotation2)

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(ledger.Amount(10), Date(2021, 5, 10), "tag"))
        annotation2 = ledger.Annotation(ledger.OriginAnnotation(ledger.Amount(10), Date(2021, 5, 10), "tag"))
        self.assertTrue(annotation1 == annotation2)
        self.assertFalse(annotation1 != annotation2)

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, Date(2021, 5, 10), "tag1"))
        annotation2 = ledger.Annotation(ledger.OriginAnnotation(None, Date(2021, 5, 10), "tag2"))
        self.assertFalse(annotation1 == annotation2)
        self.assertTrue(annotation1 != annotation2)

    def test_annotation_bool(self):

        self.assertFalse(bool(ledger.Annotation(ledger.OriginAnnotation(None, None, None))))
        self.assertTrue(bool(ledger.Annotation(ledger.OriginAnnotation(ledger.Amount(10).origin, None, None))))
        self.assertTrue(bool(ledger.Annotation(ledger.OriginAnnotation(None, Date(2021, 5, 10), None))))
        self.assertTrue(bool(ledger.Annotation(ledger.OriginAnnotation(None, None, "tag"))))

    def test_annotation_flags(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, None))
        self.assertEqual(0, annotation1.flags)
        annotation1.flags = ledger.ANNOTATION_DATE_CALCULATED | ledger.ANNOTATION_PRICE_FIXATED
        self.assertEqual(ledger.ANNOTATION_DATE_CALCULATED | ledger.ANNOTATION_PRICE_FIXATED, annotation1.flags)

    def test_annotation_has_flags(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, None))
        annotation1.flags = ledger.ANNOTATION_DATE_CALCULATED | ledger.ANNOTATION_PRICE_FIXATED

        self.assertTrue(annotation1.has_flags(ledger.ANNOTATION_DATE_CALCULATED))
        self.assertTrue(annotation1.has_flags(ledger.ANNOTATION_PRICE_FIXATED))
        self.assertTrue(annotation1.has_flags(ledger.ANNOTATION_DATE_CALCULATED | ledger.ANNOTATION_PRICE_FIXATED))
        self.assertFalse(annotation1.has_flags(ledger.ANNOTATION_VALUE_EXPR_CALCULATED))

    def test_annotation_clear_flags(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, None))
        annotation1.flags = ledger.ANNOTATION_DATE_CALCULATED | ledger.ANNOTATION_PRICE_FIXATED

        annotation1.clear_flags()
        self.assertEqual(0, annotation1.flags)

    def test_annotation_add_flags(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, None))
        annotation1.flags = ledger.ANNOTATION_DATE_CALCULATED

        annotation1.add_flags(ledger.ANNOTATION_PRICE_FIXATED)
        self.assertTrue(annotation1.has_flags(ledger.ANNOTATION_DATE_CALCULATED | ledger.ANNOTATION_PRICE_FIXATED))

    def test_annotation_drop_flags(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, None))
        annotation1.flags = ledger.ANNOTATION_DATE_CALCULATED | ledger.ANNOTATION_PRICE_FIXATED

        annotation1.drop_flags(ledger.ANNOTATION_PRICE_FIXATED)
        self.assertFalse(annotation1.has_flags(ledger.ANNOTATION_PRICE_FIXATED))
        self.assertTrue(annotation1.has_flags(ledger.ANNOTATION_DATE_CALCULATED))

    def test_annotation_price(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(ledger.Amount(10).origin, None, None))
        price = annotation1.price
        self.assertTrue(isinstance(price, ledger.Amount))
        self.assertEqual(ledger.Amount(10), price)
        annotation1.price = ledger.Amount(20)
        self.assertEqual(ledger.Amount(20), annotation1.price)

    def test_annotation_date(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, Date(2021, 5, 22), None))
        date1 = annotation1.date
        self.assertTrue(isinstance(date1, date))
        self.assertEqual(date(2021, 5, 22), date1)
        annotation1.date = date(2021, 5, 23)
        self.assertEqual(date(2021, 5, 23), annotation1.date)

    def test_annotation_tag(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag-1"))
        tag1 = annotation1.tag
        self.assertTrue(isinstance(tag1, str))
        self.assertEqual("tag-1", tag1)
        annotation1.tag = "tag-2"
        self.assertEqual("tag-2", annotation1.tag)

    def test_annotation_valid(self):

        annotation1 = ledger.Annotation(ledger.OriginAnnotation(ledger.Amount(10), None, "tag-1"))
        self.assertTrue(annotation1.valid())

class PricePointTests(unittest.TestCase):

    def test_pricepoint_constructor(self):

        when = datetime(2021, 5, 12, 22, 55, 59)
        price = Amount(10)

        price_point = ledger.PricePoint(when, price)

        self.assertIsNotNone(price_point)
        self.assertEqual(when, price_point.when)
        self.assertEqual(price, price_point.price)

    def test_pricepoint_eq(self):

        when1 = datetime(2021, 5, 12, 22, 55, 59)
        price1 = Amount(10)

        when2 = datetime(2020, 5, 12, 22, 55, 59)
        price2 = Amount(20)

        price_point1 = ledger.PricePoint(when1, price1)
        price_point1a = ledger.PricePoint(when1, price1)

        price_point2 = ledger.PricePoint(when2, price2)
        price_point2a = ledger.PricePoint(when2, price2)

        self.assertTrue(price_point1 == price_point1a)
        self.assertTrue(price_point2 == price_point2a)
        self.assertTrue(price_point1 != price_point2)
        self.assertTrue(price_point1 != price_point2a)
        self.assertFalse(price_point1 != price_point1a)
        self.assertFalse(price_point2 != price_point2a)
        self.assertFalse(price_point1 == price_point2)
        self.assertFalse(price_point1 == price_point2a)

    def test_pricepoint_when(self):

        when1 = datetime(2021, 5, 12, 22, 55, 59)
        when2 = datetime(2020, 5, 12, 22, 55, 59)
        price = Amount(20)

        price_point = ledger.PricePoint(when1, price)
        self.assertEqual(when1, price_point.when)
        price_point.when = when2
        self.assertEqual(when2, price_point.when)

    def test_pricepoint_price(self):

        when = datetime(2021, 5, 12, 22, 55, 59)
        price1 = Amount(10)
        price2 = Amount(20)

        price_point = ledger.PricePoint(when, price1)
        self.assertEqual(price1, price_point.price)
        price_point.price = price2
        self.assertEqual(price2, price_point.price)
        self.assertIsInstance(price_point.price, Amount)

class KeepDetailsTests(unittest.TestCase):

    def test_keepdetails_constructor(self):

        keepdetails1 = ledger.KeepDetails()
        self.assertFalse(keepdetails1.keep_price)
        self.assertFalse(keepdetails1.keep_date)
        self.assertFalse(keepdetails1.keep_tag)
        self.assertFalse(keepdetails1.only_actuals)

        keepdetails2 = ledger.KeepDetails(True)
        self.assertTrue(keepdetails2.keep_price)
        self.assertFalse(keepdetails2.keep_date)
        self.assertFalse(keepdetails2.keep_tag)
        self.assertFalse(keepdetails2.only_actuals)

        keepdetails3 = ledger.KeepDetails(True,True)
        self.assertTrue(keepdetails3.keep_price)
        self.assertTrue(keepdetails3.keep_date)
        self.assertFalse(keepdetails3.keep_tag)
        self.assertFalse(keepdetails3.only_actuals)

        keepdetails4 = ledger.KeepDetails(True,True,True)
        self.assertTrue(keepdetails4.keep_price)
        self.assertTrue(keepdetails4.keep_date)
        self.assertTrue(keepdetails4.keep_tag)
        self.assertFalse(keepdetails4.only_actuals)

        keepdetails5 = ledger.KeepDetails(True,True,True,True)
        self.assertTrue(keepdetails5.keep_price)
        self.assertTrue(keepdetails5.keep_date)
        self.assertTrue(keepdetails5.keep_tag)
        self.assertTrue(keepdetails5.only_actuals)

    def test_keepdetails_from_origin(self):

        origin = ledger.OriginAnnotationKeepDetails(True,True,True,True)
        keepdetails = ledger.KeepDetails.from_origin(origin)
        self.assertTrue(keepdetails.keep_price)
        self.assertTrue(keepdetails.keep_date)
        self.assertTrue(keepdetails.keep_tag)
        self.assertTrue(keepdetails.only_actuals)

    def test_keepdetails_keep_price(self):

        keepdetails = ledger.KeepDetails()
        self.assertFalse(keepdetails.keep_price)
        keepdetails.keep_price = True
        self.assertTrue(keepdetails.keep_price)
        keepdetails.keep_price = False
        self.assertFalse(keepdetails.keep_price)

    def test_keepdetails_keep_date(self):

        keepdetails = ledger.KeepDetails()
        self.assertFalse(keepdetails.keep_date)
        keepdetails.keep_date = True
        self.assertTrue(keepdetails.keep_date)
        keepdetails.keep_date = False
        self.assertFalse(keepdetails.keep_date)

    def test_keepdetails_keep_tag(self):

        keepdetails = ledger.KeepDetails()
        self.assertFalse(keepdetails.keep_tag)
        keepdetails.keep_tag = True
        self.assertTrue(keepdetails.keep_tag)
        keepdetails.keep_tag = False
        self.assertFalse(keepdetails.keep_tag)

    def test_keepdetails_only_actuals(self):

        keepdetails = ledger.KeepDetails()
        self.assertFalse(keepdetails.only_actuals)
        keepdetails.only_actuals = True
        self.assertTrue(keepdetails.only_actuals)
        keepdetails.only_actuals = False
        self.assertFalse(keepdetails.only_actuals)

    def test_keepdetails_keep_all(self):

        keepdetails = ledger.KeepDetails()
        self.assertFalse(keepdetails.keep_all())
        keepdetails = ledger.KeepDetails(True,True,True)
        self.assertTrue(keepdetails.keep_all())

        commodity = ledger.commodities.find_or_create("ZX9")
        keepdetails = ledger.KeepDetails()
        self.assertTrue(keepdetails.keep_all(commodity))

    def test_keepdetails_keep_any(self):

        keepdetails = ledger.KeepDetails()
        self.assertFalse(keepdetails.keep_any())
        keepdetails = ledger.KeepDetails(False,True,False)
        self.assertTrue(keepdetails.keep_any())

        commodity = ledger.commodities.find_or_create("ZX9")
        keepdetails = ledger.KeepDetails()
        self.assertFalse(keepdetails.keep_any(commodity))

class CommodityTests(unittest.TestCase):

    def test_commodity_decimal_comma_by_default(self):

        val = ledger.Commodity.decimal_comma_by_default

        ledger.Commodity.decimal_comma_by_default = True
        self.assertTrue(ledger.Commodity.decimal_comma_by_default)

        ledger.Commodity.decimal_comma_by_default = False
        self.assertFalse(ledger.Commodity.decimal_comma_by_default)

        ledger.Commodity.decimal_comma_by_default = val

    def test_commodity_flags(self):

        comm = ledger.commodities.find_or_create("WTC1")

        flags = comm.flags
        comm.flags = ledger.COMMODITY_PRIMARY
        self.assertEqual(ledger.COMMODITY_PRIMARY, comm.flags)
        comm.flags = flags
        self.assertEqual(flags, comm.flags)

    def test_commodity_has_flags(self):

        comm = ledger.commodities.find_or_create("WTC1")
        flags = comm.flags

        comm.flags = ledger.COMMODITY_PRIMARY | ledger.COMMODITY_STYLE_SUFFIXED | ledger.COMMODITY_STYLE_THOUSANDS
        self.assertTrue(comm.has_flags(ledger.COMMODITY_PRIMARY))
        self.assertTrue(comm.has_flags(ledger.COMMODITY_PRIMARY | ledger.COMMODITY_STYLE_THOUSANDS))
        self.assertTrue(comm.has_flags(ledger.COMMODITY_PRIMARY | ledger.COMMODITY_STYLE_SUFFIXED | ledger.COMMODITY_STYLE_THOUSANDS))
        self.assertFalse(comm.has_flags(ledger.COMMODITY_STYLE_SEPARATED))
        self.assertFalse(comm.has_flags(ledger.COMMODITY_STYLE_SEPARATED | ledger.COMMODITY_PRIMARY))

        comm.flags = flags

    def test_commodity_clear_flags(self):

        comm = ledger.commodities.find_or_create("WTC1")
        flags = comm.flags
        comm.flags = ledger.COMMODITY_PRIMARY | ledger.COMMODITY_STYLE_SUFFIXED | ledger.COMMODITY_STYLE_THOUSANDS

        comm.clear_flags()
        self.assertTrue(comm.flags == 0)

        comm.flags = flags

    def test_commodity_add_flags(self):

        comm = ledger.commodities.find_or_create("WTC1")
        flags = comm.flags

        comm.flags = ledger.COMMODITY_PRIMARY
        comm.add_flags(ledger.COMMODITY_STYLE_SUFFIXED | ledger.COMMODITY_STYLE_THOUSANDS)
        self.assertTrue(comm.has_flags(ledger.COMMODITY_PRIMARY | ledger.COMMODITY_STYLE_SUFFIXED | ledger.COMMODITY_STYLE_THOUSANDS))

        comm.flags = flags

    def test_commodity_drop_flags(self):

        comm = ledger.commodities.find_or_create("WTC1")
        flags = comm.flags

        comm.flags = ledger.COMMODITY_PRIMARY | ledger.COMMODITY_STYLE_SUFFIXED | ledger.COMMODITY_STYLE_THOUSANDS
        comm.drop_flags(ledger.COMMODITY_STYLE_SUFFIXED | ledger.COMMODITY_STYLE_THOUSANDS)
        self.assertFalse(comm.has_flags(ledger.COMMODITY_PRIMARY | ledger.COMMODITY_STYLE_SUFFIXED | ledger.COMMODITY_STYLE_THOUSANDS))
        self.assertFalse(comm.has_flags(ledger.COMMODITY_PRIMARY | ledger.COMMODITY_STYLE_SUFFIXED))
        self.assertTrue(comm.has_flags(ledger.COMMODITY_PRIMARY))

        comm.flags = flags

    def test_commodity_str_shows_symbol(self):

        comm = ledger.commodities.find_or_create("WTC2")
        self.assertEqual('"WTC2"', str(comm))
        self.assertEqual('"WTC2"', comm.symbol)

    def test_commodity_bool_checks_null_commodity(self):

        comm = ledger.commodities.find_or_create("WTC3")
        self.assertTrue(bool(comm))
        self.assertTrue(isinstance(comm, ledger.Commodity))
        # Empty amount has null commodity
        null_comm = ledger.Amount(0).commodity
        self.assertFalse(bool(null_comm))

    def test_commodity_symbol_needs_quotes(self):

        self.assertFalse(ledger.Commodity.symbol_needs_quotes("A"))
        self.assertTrue(ledger.Commodity.symbol_needs_quotes("A1"))

        comm = ledger.commodities.find_or_create("WTC2")
        self.assertFalse(comm.symbol_needs_quotes("A"))
        self.assertTrue(comm.symbol_needs_quotes("A1"))

    def test_commodity_referent(self):

        comm = ledger.commodities.find_or_create("WTC2")
        refr = comm.referent
        self.assertTrue(isinstance(refr, ledger.Commodity))

    def test_commodity_has_annotation(self):

        comm = ledger.commodities.find_or_create("WTC2")
        self.assertFalse(comm.has_annotation())

    def test_commodity_strip_annotations(self):

        comm = ledger.commodities.find_or_create("WTC2")
        self.assertEqual(comm, comm.strip_annotations())
        self.assertEqual(comm, comm.strip_annotations(ledger.KeepDetails()))

    def test_commodity_write_annotations(self):

        comm = ledger.commodities.find_or_create("WTC3")
        self.assertEqual("", comm.write_annotations())

    def test_commodity_pool(self):

        comm = ledger.commodities.find_or_create("WTC4")
        self.assertEqual(ledger.commodities.origin, comm.pool().origin)

    def test_commodity_base_symbol(self):

        comm = ledger.commodities.find_or_create("WTC5")
        self.assertEqual("WTC5", comm.base_symbol)

    def test_commodity_symbol(self):

        comm = ledger.commodities.find_or_create("WTC5")
        self.assertEqual('"WTC5"', comm.symbol)

    def test_commodity_name(self):

        comm = ledger.commodities.find_or_create("WTC6")
        name = comm.name

        comm.name = "name1"
        self.assertEqual("name1", comm.name)

        comm.name = name

    def test_commodity_note(self):

        comm = ledger.commodities.find_or_create("WTC6")
        note = comm.note

        comm.note = "note1"
        self.assertEqual("note1", comm.note)

        comm.note = note

    def test_commodity_precision(self):

        comm = ledger.commodities.find_or_create("WTC6")
        precision = comm.precision

        comm.precision = 5
        self.assertEqual(5, comm.precision)

        comm.precision = precision

    def test_commodity_smaller(self):

        comm = ledger.commodities.find_or_create("WTC6")
        smaller = comm.smaller

        amnt = Amount(5)
        comm.smaller = amnt
        self.assertEqual(amnt, comm.smaller)

        comm.smaller = smaller

    def test_commodity_larger(self):

        comm = ledger.commodities.find_or_create("WTC7")
        larger = comm.larger

        amnt = Amount(5)
        comm.larger = amnt
        self.assertEqual(amnt, comm.larger)

        comm.larger = larger

    def test_commodity_add_price(self):

        date = datetime.today()
        comm = ledger.commodities.find_or_create("WTC8")
        comm.add_price(date, ledger.Amount(10))
        comm.add_price(date, ledger.Amount(10), True)
        self.assertTrue("WTC8" in comm.pool().origin.CommodityPriceHistory.PrintMap(ledger.to_ndatetime(date)))

    def test_commodity_remove_price(self):

        date = datetime.today()
        amnt = ledger.Amount(10)
        comm = ledger.commodities.find_or_create("WTC9")
        comm.add_price(date, amnt)
        comm.remove_price(date, amnt.commodity)
        self.assertFalse("WTC9" in comm.pool().origin.CommodityPriceHistory.PrintMap(ledger.to_ndatetime(date)))

    def test_commodity_find_price(self):

        date = datetime.today()
        amnt = ledger.Amount(10)
        comm = ledger.commodities.find_or_create("WTD1")
        comm.add_price(date, amnt)
        self.assertIsNone(comm.find_price())
        self.assertIsNone(comm.find_price(comm))
        self.assertIsNone(comm.find_price(comm,date))
        self.assertIsNone(comm.find_price(comm,date,date))

    def test_commodity_check_for_updated_price(self):

        date = datetime.today()
        amnt = ledger.Amount(10)
        comm = ledger.commodities.find_or_create("WTD2")
        pricePoint = ledger.PricePoint(date,amnt)
        self.assertIsNone(comm.check_for_updated_price())
        self.assertIsNone(comm.check_for_updated_price(pricePoint))
        self.assertIsNone(comm.check_for_updated_price(pricePoint,date))
        self.assertIsNone(comm.check_for_updated_price(pricePoint,date,comm))

    def test_commodity_valid(self):

        date = datetime.today()
        amnt = ledger.Amount(10)
        comm = ledger.commodities.find_or_create("WTD3")
        comm.valid()  # no exception

class AnnotatedCommodityTests(unittest.TestCase):

    def test_annotatedcommodity_constructor(self):
        comm = ledger.commodities.find_or_create("WTD4")
        ann = ledger.OriginAnnotation()
        origin = ledger.OriginAnnotatedCommodity(comm.origin, ann)
        annotatedCommodity = ledger.AnnotatedCommodity(origin)
        self.assertTrue(isinstance(annotatedCommodity, ledger.AnnotatedCommodity))

    def test_annotatedcommodity_details(self):
        annotation = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag"))
        annotated_commodity = ledger.commodities.find_or_create("XYZ20", annotation)
        self.assertTrue(isinstance(annotated_commodity, ledger.AnnotatedCommodity))

        annotation2 = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag2"))
        details = annotated_commodity.details

        annotated_commodity.details = annotation2
        self.assertEqual(annotation2, annotated_commodity.details)

        annotated_commodity.details = annotation
        self.assertEqual(annotation, annotated_commodity.details)

    def test_annotatedcommodity_equals(self):
        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag1"))
        annotation2 = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag2"))
        annotated_commodity1 = ledger.commodities.find_or_create("XYZ21", annotation1)
        annotated_commodity1a = ledger.commodities.find_or_create("XYZ21", annotation1)
        annotated_commodity2 = ledger.commodities.find_or_create("XYZ21", annotation2)

        self.assertTrue(isinstance(annotated_commodity1, ledger.AnnotatedCommodity))
        self.assertTrue(isinstance(annotated_commodity1a, ledger.AnnotatedCommodity))
        self.assertTrue(isinstance(annotated_commodity2, ledger.AnnotatedCommodity))

        self.assertTrue(annotated_commodity1 == annotated_commodity1)
        self.assertTrue(annotated_commodity1a == annotated_commodity1)
        self.assertTrue(annotated_commodity1 == annotated_commodity1a)
        self.assertTrue(annotated_commodity1 != annotated_commodity2)
        self.assertTrue(annotated_commodity2 != annotated_commodity1)

        comm = ledger.commodities.find_or_create("XYZ21")
        self.assertTrue(isinstance(comm, ledger.Commodity))

        self.assertFalse(comm == annotated_commodity1)
        self.assertFalse(annotated_commodity1 == comm)

    def test_annotatedcommodity_referent(self):
        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag1"))
        annotation2 = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag2"))
        annotated_commodity1 = ledger.commodities.find_or_create("XYZ23", annotation1)
        annotated_commodity2 = ledger.commodities.find_or_create("XYZ23", annotation2)

        referent1 = annotated_commodity1.referent
        self.assertTrue(isinstance(referent1, ledger.Commodity))
        self.assertFalse(isinstance(referent1, ledger.AnnotatedCommodity))

        referent2 = annotated_commodity1.referent
        self.assertTrue(isinstance(referent2, ledger.Commodity))
        self.assertFalse(isinstance(referent2, ledger.AnnotatedCommodity))

        self.assertEqual(referent1, referent2)
        self.assertEqual('"XYZ23"', str(referent1))

    def test_annotatedcommodity_strip_annotations(self):
        annotation1 = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag1"))
        annotation2 = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag2"))
        annotated_commodity1 = ledger.commodities.find_or_create("XYZ24", annotation1)
        annotated_commodity2 = ledger.commodities.find_or_create("XYZ24", annotation2)

        stripped = annotated_commodity1.strip_annotations()
        self.assertTrue(isinstance(stripped, ledger.Commodity))
        self.assertFalse(isinstance(stripped, ledger.AnnotatedCommodity))
        self.assertEqual('"XYZ24"', str(stripped))

        stripped = annotated_commodity1.strip_annotations(ledger.KeepDetails(True, True, False, False))  # do not keep tags
        self.assertTrue(isinstance(stripped, ledger.Commodity))
        self.assertFalse(isinstance(stripped, ledger.AnnotatedCommodity))
        self.assertEqual('"XYZ24"', str(stripped))

        stripped = annotated_commodity1.strip_annotations(ledger.KeepDetails(True, True, True, True))  # keep tags
        self.assertTrue(isinstance(stripped, ledger.Commodity))
        self.assertTrue(isinstance(stripped, ledger.AnnotatedCommodity))
        self.assertEqual('"XYZ24"', str(stripped))

    def test_annotatedcommodity_write_annotations(self):
        annotation = ledger.Annotation(ledger.OriginAnnotation(None, None, "tag1"))
        annotated_commodity = ledger.commodities.find_or_create("XYZ25", annotation)
        self.assertEqual(' (tag1)', annotated_commodity.write_annotations())

# Accounts

class AccountXDataDetailsTests(unittest.TestCase):

    def test_accountxdata_constructor(self):
        xdata = ledger.AccountXDataDetails(ledger.OriginAccountXDataDetails())
        self.assertIsInstance(xdata, ledger.AccountXDataDetails)

    def test_accountxdata_from_origin(self):
        xdata = ledger.AccountXDataDetails.from_origin(ledger.OriginAccountXDataDetails())
        self.assertIsInstance(xdata, ledger.AccountXDataDetails)

        xdata = ledger.AccountXDataDetails.from_origin(None)
        self.assertIsNone(xdata)
        
    def test_accountxdata_total(self):
        xdata = ledger.AccountXDataDetails()
        self.assertIsInstance(xdata.total, ledger.Value)
        self.assertTrue(xdata.total.is_zero())

    def test_accountxdata_real_total(self):
        xdata = ledger.AccountXDataDetails()
        self.assertIsNone(xdata.real_total)

    def test_accountxdata_calculated(self):
        xdata = ledger.AccountXDataDetails()
        self.assertFalse(xdata.calculated)

    def test_accountxdata_gathered(self):
        xdata = ledger.AccountXDataDetails()
        self.assertFalse(xdata.gathered)

    def test_accountxdata_posts_count(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, xdata.posts_count)

        post = ledger.Posting()
        post.date = date.today()
        xdata.update(post)
        self.assertEqual(1, xdata.posts_count)

    def test_accountxdata_posts_virtuals_count(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, xdata.posts_virtuals_count)

        post = ledger.Posting()
        post.date = date.today()
        xdata.update(post)
        self.assertEqual(0, xdata.posts_virtuals_count)

        post = ledger.Posting()
        post.date = date.today()
        post.add_flags(ledger.POST_VIRTUAL)
        xdata.update(post)
        self.assertEqual(1, xdata.posts_virtuals_count)

    def test_accountxdata_posts_cleared_count(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, xdata.posts_cleared_count)

        post = ledger.Posting()
        post.date = date.today()
        xdata.update(post)
        self.assertEqual(0, xdata.posts_cleared_count)

        post = ledger.Posting()
        post.date = date.today()
        post.state = ledger.State.Cleared
        xdata.update(post)
        self.assertEqual(1, xdata.posts_cleared_count)

    def test_accountxdata_posts_last_7_count(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, xdata.posts_last_7_count)

        post = ledger.Posting()
        post.date = date.today()
        xdata.update(post)
        self.assertEqual(1, xdata.posts_last_7_count)

    def test_accountxdata_posts_last_30_count(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, xdata.posts_last_30_count)

        post = ledger.Posting()
        post.date = date.today()
        xdata.update(post)
        self.assertEqual(1, xdata.posts_last_30_count)

    def test_accountxdata_posts_this_month_count(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, xdata.posts_this_month_count)

    def test_accountxdata_earliest_post(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(date(1,1,1), xdata.earliest_post)

        post = ledger.Posting()
        post.date = date.today()
        xdata.update(post)
        self.assertEqual(post.date, xdata.earliest_post)

    def test_accountxdata_earliest_cleared_post(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(date(1,1,1), xdata.earliest_cleared_post)

        post = ledger.Posting()
        post.date = date.today()
        post.state = ledger.State.Cleared
        xdata.update(post)
        self.assertEqual(post.date, xdata.earliest_cleared_post)

    def test_accountxdata_latest_post(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(date(1,1,1), xdata.latest_post)

        post = ledger.Posting()
        post.date = date.today()
        xdata.update(post)
        self.assertEqual(post.date, xdata.latest_post)

    def test_accountxdata_latest_cleared_post(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(date(1,1,1), xdata.latest_cleared_post)

        post = ledger.Posting()
        post.date = date.today()
        post.state = ledger.State.Cleared
        xdata.update(post)
        self.assertEqual(post.date, xdata.latest_cleared_post)

    def test_accountxdata_filenames(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, len(xdata.filenames))

        post = ledger.Posting()
        post.date = date.today()
        post.pos = ledger.Position()
        post.pos.pathname = "file-name"
        post.account = ledger.Account(None, "account-name")
        post.set_tag("Payee", ledger.string_value("payee-name"))
        xdata.update(post, True)

        self.assertEqual(1, len(xdata.filenames))
        self.assertEqual("file-name", xdata.filenames[0])

    def test_accountxdata_accounts_referenced(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, len(xdata.accounts_referenced))

        post = ledger.Posting()
        post.date = date.today()
        post.pos = ledger.Position()
        post.pos.pathname = "file-name"
        post.account = ledger.Account(None, "account-name")
        post.set_tag("Payee", ledger.string_value("payee-name"))
        xdata.update(post, True)

        self.assertEqual(1, len(xdata.accounts_referenced))
        self.assertEqual("account-name", xdata.accounts_referenced[0])

    def test_accountxdata_payees_referenced(self):
        xdata = ledger.AccountXDataDetails()
        self.assertEqual(0, len(xdata.payees_referenced))

        post = ledger.Posting()
        post.date = date.today()
        post.pos = ledger.Position()
        post.pos.pathname = "file-name"
        post.account = ledger.Account(None, "account-name")
        post.set_tag("Payee", ledger.string_value("payee-name"))
        xdata.update(post, True)

        self.assertEqual(1, len(xdata.payees_referenced))
        self.assertEqual("payee-name", xdata.payees_referenced[0])

    def test_accountxdata_iadd(self):
        xdata1 = ledger.AccountXDataDetails()
        xdata2 = ledger.AccountXDataDetails()

        post = ledger.Posting()
        post.date = date.today()
        xdata1.update(post)
        xdata2.update(post)

        xdata1 += xdata2
        self.assertEqual(2, xdata1.posts_count)
        self.assertEqual(1, xdata2.posts_count)

    def test_accountxdata_update(self):
        xdata = ledger.AccountXDataDetails()

        post = ledger.Posting()
        post.date = date.today()
        xdata.update(post)
        self.assertEqual(1, xdata.posts_count)

        post = ledger.Posting()
        post.date = date.today()
        post.pos = ledger.Position()
        post.pos.pathname = "file-name"
        post.account = ledger.Account(None, "account-name")
        post.set_tag("Payee", ledger.string_value("payee-name"))
        xdata.update(post, True)
        self.assertEqual(2, xdata.posts_count)

class AccountXDataTests(unittest.TestCase):

    def test_accountxdata_constructor(self):
        xdata = ledger.AccountXData(ledger.OriginAccountXData())
        self.assertIsInstance(xdata, ledger.AccountXData)

    def test_accountxdata_from_origin(self):
        xdata = ledger.AccountXData.from_origin(ledger.OriginAccountXData())
        self.assertIsInstance(xdata, ledger.AccountXData)

        xdata = ledger.AccountXData.from_origin(None)
        self.assertIsNone(xdata)

    def test_accountxdata_flags(self):

        acnt = ledger.AccountXData()
        self.assertEqual(0, acnt.flags)
        acnt.flags = ledger.ACCOUNT_EXT_MATCHING | ledger.ACCOUNT_EXT_VISITED
        self.assertEqual(ledger.ACCOUNT_EXT_MATCHING | ledger.ACCOUNT_EXT_VISITED, acnt.flags)

    def test_accountxdata_has_flags(self):

        acnt = ledger.AccountXData()
        acnt.flags = ledger.ACCOUNT_EXT_MATCHING | ledger.ACCOUNT_EXT_VISITED

        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_EXT_MATCHING))
        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_EXT_VISITED))
        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_EXT_MATCHING | ledger.ACCOUNT_EXT_VISITED))
        self.assertFalse(acnt.has_flags(ledger.ACCOUNT_EXT_TO_DISPLAY))

    def test_accountxdata_clear_flags(self):

        acnt = ledger.AccountXData()
        acnt.flags = ledger.ACCOUNT_EXT_MATCHING | ledger.ACCOUNT_EXT_VISITED

        acnt.clear_flags()
        self.assertEqual(0, acnt.flags)

    def test_accountxdata_add_flags(self):

        acnt = ledger.AccountXData()
        acnt.flags = ledger.ACCOUNT_EXT_MATCHING | ledger.ACCOUNT_EXT_VISITED

        acnt.add_flags(ledger.ACCOUNT_EXT_TO_DISPLAY)
        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_EXT_MATCHING | ledger.ACCOUNT_EXT_TO_DISPLAY))

    def test_accountxdata_drop_flags(self):

        acnt = ledger.AccountXData()
        acnt.flags = ledger.ACCOUNT_EXT_MATCHING | ledger.ACCOUNT_EXT_VISITED

        acnt.drop_flags(ledger.ACCOUNT_EXT_MATCHING)
        self.assertFalse(acnt.has_flags(ledger.ACCOUNT_EXT_MATCHING))
        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_EXT_VISITED))

    def test_accountxdata_self_details(self):

        acnt = ledger.AccountXData()
        self.assertIsInstance(acnt.self_details, ledger.AccountXDataDetails)

    def test_accountxdata_family_details(self):

        acnt = ledger.AccountXData()
        self.assertIsInstance(acnt.family_details, ledger.AccountXDataDetails)

    def test_accountxdata_reported_posts(self):

        acnt = ledger.AccountXData()
        self.assertEqual(0, len(acnt.reported_posts))

        posts = acnt.reported_posts
        posts.append(ledger.Posting())
        self.assertEqual(1, len(acnt.reported_posts))

    def test_accountxdata_sort_values(self):

        acnt = ledger.AccountXData()
        self.assertEqual(0, len(acnt.sort_values))

        posts = acnt.sort_values
        posts.append((ledger.Value(10),True))
        self.assertEqual(1, len(acnt.sort_values))

class AccountTests(unittest.TestCase):

    def test_account_constructors(self):
        acc1 = ledger.Account()
        self.assertTrue(isinstance(acc1, ledger.Account))

        acc2 = ledger.Account(acc1,"name","note")
        self.assertTrue(isinstance(acc2, ledger.Account))

        acc3 = ledger.Account(origin = ledger.OriginAccount())
        self.assertTrue(isinstance(acc3, ledger.Account))

    def test_account_from_origin(self):
        acc1 = ledger.Account.from_origin(None)
        self.assertIsNone(acc1)

        acc2 = ledger.Account.from_origin(ledger.OriginAccount())
        self.assertIsNotNone(acc2)
        self.assertTrue(isinstance(acc2, ledger.Account))

    def test_account_flags(self):

        acnt = ledger.Account()
        self.assertEqual(0, acnt.flags)
        acnt.flags = ledger.ACCOUNT_KNOWN | ledger.ACCOUNT_GENERATED
        self.assertEqual(ledger.ACCOUNT_KNOWN | ledger.ACCOUNT_GENERATED, acnt.flags)

    def test_account_has_flags(self):

        acnt = ledger.Account()
        acnt.flags = ledger.ACCOUNT_KNOWN | ledger.ACCOUNT_GENERATED

        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_KNOWN))
        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_GENERATED))
        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_KNOWN | ledger.ACCOUNT_GENERATED))
        self.assertFalse(acnt.has_flags(ledger.ACCOUNT_TEMP))

    def test_account_clear_flags(self):

        acnt = ledger.Account()
        acnt.flags = ledger.ACCOUNT_KNOWN | ledger.ACCOUNT_GENERATED

        acnt.clear_flags()
        self.assertEqual(0, acnt.flags)

    def test_account_add_flags(self):

        acnt = ledger.Account()
        acnt.flags = ledger.ACCOUNT_KNOWN | ledger.ACCOUNT_GENERATED

        acnt.add_flags(ledger.ACCOUNT_TEMP)
        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_KNOWN | ledger.ACCOUNT_TEMP))

    def test_account_drop_flags(self):

        acnt = ledger.Account()
        acnt.flags = ledger.ACCOUNT_KNOWN | ledger.ACCOUNT_GENERATED

        acnt.drop_flags(ledger.ACCOUNT_KNOWN)
        self.assertFalse(acnt.has_flags(ledger.ACCOUNT_KNOWN))
        self.assertTrue(acnt.has_flags(ledger.ACCOUNT_GENERATED))

    def test_account_parent(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)

        self.assertIsNone(acnt1.parent)
        self.assertIsNotNone(acnt2.parent)
        self.assertTrue(isinstance(acnt2.parent, ledger.Account))
        self.assertEqual("account 1", acnt2.parent.name)

    def test_account_name(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)

        self.assertEqual("account 1", acnt1.name)
        self.assertEqual("account 2", acnt2.name)

    def test_account_note(self):

        acnt1 = ledger.Account(None, "account 1", "note 1")
        acnt2 = ledger.Account(acnt1, "account 2", "note 2")
        acnt1.add_account(acnt2)

        self.assertEqual("note 1", acnt1.note)
        self.assertEqual("note 2", acnt2.note)

    def test_account_depth(self):

        acnt1 = ledger.Account(None, "account 1", "note 1")
        acnt2 = ledger.Account(acnt1, "account 2", "note 2")
        acnt1.add_account(acnt2)

        self.assertEqual(0, acnt1.depth)
        self.assertEqual(1, acnt2.depth)

    def test_account_str(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)

        self.assertEqual("account 1", str(acnt1))
        self.assertEqual("account 1:account 2", str(acnt2))

    def test_account_fullname(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)

        self.assertEqual("account 1", acnt1.fullname())
        self.assertEqual("account 1:account 2", acnt2.fullname())

    def test_account_partial_name(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)

        self.assertEqual("account 1", acnt1.partial_name())
        self.assertEqual("account 2", acnt2.partial_name())
        self.assertEqual("account 1", acnt1.partial_name(True))
        self.assertEqual("account 2", acnt2.partial_name(True))

    def test_account_add_account(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")

        acnt1.add_account(acnt2)
        self.assertEqual(str(acnt2), str(acnt1.find_account("account 2")))

    def test_account_remove_account(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")

        acnt1.add_account(acnt2)
        acnt1.remove_account(acnt2)

        self.assertIsNone(acnt1.find_account("account 2", False))

    def test_account_find_account(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)

        res1 = acnt1.find_account("account 2", False)
        self.assertTrue(isinstance(res1, ledger.Account))
        self.assertEqual("account 1:account 2", str(res1))

        self.assertIsNone(acnt1.find_account("account 3", False))

        res2 = acnt1.find_account("account 3", True) # auto-creating
        self.assertTrue(isinstance(res2, ledger.Account))
        self.assertEqual("account 1:account 3", str(res2))

    def test_account_find_account_re(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)

        res1 = acnt1.find_account_re("account 2")
        self.assertTrue(isinstance(res1, ledger.Account))
        self.assertEqual("account 1:account 2", str(res1))

        self.assertIsNone(acnt1.find_account_re("account 3"))

    def test_account_add_post(self):

        acnt = ledger.Account(None, "account")
        post = ledger.Posting()

        acnt.add_post(post)
        self.assertEqual(post, acnt.posts()[0])

    def test_account_remove_post(self):

        acnt = ledger.Account(None, "account")
        post = ledger.Posting()

        self.assertEqual(0, len(acnt.posts()))
        acnt.add_post(post)
        self.assertEqual(1, len(acnt.posts()))
        acnt.remove_post(post)
        self.assertEqual(0, len(acnt.posts()))

    def test_account_valid(self):

        acnt = ledger.Account(None, "account")
        self.assertTrue(acnt.valid())

    def test_account_len(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")

        self.assertEqual(0, len(acnt1))
        acnt1.add_account(acnt2)
        self.assertEqual(1, len(acnt1))
        acnt1.remove_account(acnt2)
        self.assertEqual(0, len(acnt1))

    def test_account_getitem(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)
        self.assertEqual(acnt2.origin, acnt1[0].origin)

    def test_account_iter(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)
        for item in acnt1:
            self.assertIsInstance(item, ledger.Account)
            self.assertEqual(item.origin, acnt2.origin)

    def test_account_accounts(self):

        acnt1 = ledger.Account(None, "account 1")
        acnt2 = ledger.Account(acnt1, "account 2")
        acnt1.add_account(acnt2)
        for item in acnt1.accounts():
            self.assertIsInstance(item, ledger.Account)
            self.assertEqual(item.origin, acnt2.origin)

    def test_account_posts(self):

        acnt = ledger.Account(None, "account")
        post = ledger.Posting()
        acnt.add_post(post)
        for item in acnt.posts():
            self.assertIsInstance(item, ledger.Posting)
            self.assertEqual(item.origin, post.origin)

    def test_account_has_xdata(self):

        acnt = ledger.Account(None, "account")
        self.assertFalse(acnt.has_xdata())
        acnt.xdata()
        self.assertTrue(acnt.has_xdata())

    def test_account_clear_xdata(self):

        acnt = ledger.Account(None, "account")
        acnt.xdata()
        self.assertTrue(acnt.has_xdata())
        acnt.clear_xdata()
        self.assertFalse(acnt.has_xdata())

    def test_account_xdata(self):

        acnt = ledger.Account(None, "account")
        self.assertIsInstance(acnt.xdata(), ledger.AccountXData)

    def test_account_amount(self):

        acnt = ledger.Account(None, "account")
        self.assertIsInstance(acnt.amount(), ledger.Value)
        self.assertTrue(acnt.amount().is_zero())
        self.assertIsInstance(acnt.amount(ledger.Expr()), ledger.Value)
        self.assertTrue(acnt.amount(ledger.Expr()).is_zero())

    def test_account_total(self):

        acnt = ledger.Account(None, "account")
        self.assertIsInstance(acnt.total(), ledger.Value)
        self.assertTrue(acnt.total().is_zero())
        self.assertIsInstance(acnt.total(ledger.Expr()), ledger.Value)
        self.assertTrue(acnt.total(ledger.Expr()).is_zero())

    def test_account_self_details(self):

        acnt = ledger.Account(None, "account")
        self.assertIsInstance(acnt.self_details(), ledger.AccountXDataDetails)
        self.assertIsInstance(acnt.self_details(True), ledger.AccountXDataDetails)

    def test_account_family_details(self):

        acnt = ledger.Account(None, "account")
        self.assertIsInstance(acnt.family_details(), ledger.AccountXDataDetails)
        self.assertIsInstance(acnt.family_details(True), ledger.AccountXDataDetails)

    def test_account_has_xflags(self):

        acnt = ledger.Account(None, "account")
        self.assertFalse(acnt.has_xflags(ledger.ACCOUNT_EXT_VISITED))

    def test_account_children_with_flags(self):

        acnt = ledger.Account(None, "account")
        self.assertEqual(0, acnt.children_with_flags(False, False))

# Posts

class PostingXDataTests(unittest.TestCase):

    def test_postingxdata_constructors(self):
        pxd = ledger.PostingXData()
        self.assertTrue(isinstance(pxd, ledger.PostingXData))
        pxd = ledger.PostingXData(ledger.OriginPostXData())
        self.assertTrue(isinstance(pxd, ledger.PostingXData))

    def test_postingxdata_from_origin(self):
        pxd = ledger.PostingXData.from_origin(None)
        self.assertIsNone(pxd)

        pxd = ledger.PostingXData.from_origin(ledger.OriginPostXData())
        self.assertIsNotNone(pxd)
        self.assertTrue(isinstance(pxd, ledger.PostingXData))

    def test_postingxdata_flags(self):

        pxd = ledger.PostingXData()
        self.assertEqual(0, pxd.flags)
        pxd.flags = ledger.POST_EXT_DISPLAYED | ledger.POST_EXT_SORT_CALC
        self.assertEqual(ledger.POST_EXT_DISPLAYED | ledger.POST_EXT_SORT_CALC, pxd.flags)

    def test_postingxdata_has_flags(self):

        pxd = ledger.PostingXData()
        pxd.flags = ledger.POST_EXT_DISPLAYED | ledger.POST_EXT_SORT_CALC

        self.assertTrue(pxd.has_flags(ledger.POST_EXT_DISPLAYED))
        self.assertTrue(pxd.has_flags(ledger.POST_EXT_SORT_CALC))
        self.assertTrue(pxd.has_flags(ledger.POST_EXT_DISPLAYED | ledger.POST_EXT_SORT_CALC))
        self.assertFalse(pxd.has_flags(ledger.POST_EXT_VISITED))

    def test_postingxdata_clear_flags(self):

        pxd = ledger.PostingXData()
        pxd.flags = ledger.POST_EXT_DISPLAYED | ledger.POST_EXT_SORT_CALC

        pxd.clear_flags()
        self.assertEqual(0, pxd.flags)

    def test_postingxdata_add_flags(self):

        pxd = ledger.PostingXData()
        pxd.flags = ledger.POST_EXT_DISPLAYED | ledger.POST_EXT_SORT_CALC

        pxd.add_flags(ledger.POST_EXT_VISITED)
        self.assertTrue(pxd.has_flags(ledger.POST_EXT_DISPLAYED | ledger.POST_EXT_VISITED))

    def test_postingxdata_drop_flags(self):

        pxd = ledger.PostingXData()
        pxd.flags = ledger.POST_EXT_DISPLAYED | ledger.POST_EXT_SORT_CALC

        pxd.drop_flags(ledger.POST_EXT_DISPLAYED)
        self.assertFalse(pxd.has_flags(ledger.POST_EXT_DISPLAYED))
        self.assertTrue(pxd.has_flags(ledger.POST_EXT_SORT_CALC))

    def test_postingxdata_visited_value(self):

        pxd = ledger.PostingXData()
        pxd.visited_value = ledger.Value(10)
        self.assertEqual(ledger.Value(10), pxd.visited_value)
        pxd.visited_value = None
        self.assertEqual(None, pxd.visited_value)

    def test_postingxdata_compound_value(self):

        pxd = ledger.PostingXData()
        pxd.compound_value = ledger.Value(10)
        self.assertEqual(ledger.Value(10), pxd.compound_value)
        pxd.compound_value = None
        self.assertEqual(None, pxd.compound_value)

    def test_postingxdata_total(self):

        pxd = ledger.PostingXData()
        pxd.total = ledger.Value(10)
        self.assertEqual(ledger.Value(10), pxd.total)
        pxd.total = None
        self.assertEqual(None, pxd.total)

    def test_postingxdata_count(self):

        pxd = ledger.PostingXData()
        pxd.count = 10
        self.assertEqual(10, pxd.count)
        pxd.count = 0
        self.assertEqual(0, pxd.count)

    def test_postingxdata_date(self):

        pxd = ledger.PostingXData()
        pxd.date = date(2021,5,22)
        self.assertEqual(date(2021,5,22), pxd.date)
        pxd.date = date(2021,5,25)
        self.assertEqual(date(2021,5,25), pxd.date)

    def test_postingxdata_datetime(self):

        pxd = ledger.PostingXData()
        pxd.datetime = datetime(2021,5,22, 22,25)
        self.assertEqual(datetime(2021,5,22, 22,25), pxd.datetime)
        pxd.datetime = datetime(2021,5,25)
        self.assertEqual(datetime(2021,5,25), pxd.datetime)

    def test_postingxdata_account(self):

        acc = ledger.Account()
        pxd = ledger.PostingXData()
        pxd.account = acc
        self.assertEqual(acc.origin, pxd.account.origin)
        pxd.account = None
        self.assertEqual(None, pxd.account)

    def test_postingxdata_sort_values(self):

        pxd = ledger.PostingXData()
        sval = pxd.sort_values
        sval.append((ledger.Value(10),True))
        pxd.sort_values.append((ledger.Value(20),False))
        self.assertEqual(2, len(pxd.sort_values))
        self.assertEqual(10, pxd.sort_values[0][0].to_long())

class PostingTests(unittest.TestCase):

    def test_posting_constructors(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertTrue(isinstance(pst, ledger.Posting))

    def test_posting_from_origin(self):
        pst = ledger.Posting.from_origin(None)
        self.assertIsNone(pst)

        pst = ledger.Posting.from_origin(ledger.OriginPost())
        self.assertIsNotNone(pst)
        self.assertTrue(isinstance(pst, ledger.Posting))

    def test_posting_id(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertEqual("0", pst.id())

    def test_posting_seq(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertEqual(0, pst.seq())

    def test_posting_xact(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertIsNone(pst.xact)

        trx = ledger.Transaction()
        pst.xact = trx
        self.assertIsInstance(pst.xact, ledger.Transaction)
        self.assertEqual(pst.xact.origin, trx.origin)

        pst.xact = None
        self.assertIsNone(pst.xact)

    def test_posting_account(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertIsNone(pst.account)

        acc = ledger.Account()
        pst.account = acc
        self.assertIsInstance(pst.account, ledger.Account)
        self.assertEqual(pst.account.origin, acc.origin)

        pst.account = None
        self.assertIsNone(pst.account)

    def test_posting_amount(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertIsNone(pst.amount)

        amt = ledger.Amount(10)
        pst.amount = amt
        self.assertIsInstance(pst.amount, ledger.Amount)
        self.assertEqual(pst.amount, amt)

        pst.amount = None
        self.assertIsNone(pst.amount)

    def test_posting_cost(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertIsNone(pst.cost)

        amt = ledger.Amount(10)
        pst.cost = amt
        self.assertIsInstance(pst.cost, ledger.Amount)
        self.assertEqual(pst.cost, amt)

        pst.cost = None
        self.assertIsNone(pst.cost)

    def test_posting_given_cost(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertIsNone(pst.given_cost)

        amt = ledger.Amount(10)
        pst.given_cost = amt
        self.assertIsInstance(pst.given_cost, ledger.Amount)
        self.assertEqual(pst.given_cost, amt)

        pst.given_cost = None
        self.assertIsNone(pst.given_cost)

    def test_posting_assigned_amount(self):
        pst = ledger.Posting(ledger.OriginPost())
        self.assertIsNone(pst.assigned_amount)

        amt = ledger.Amount(10)
        pst.assigned_amount = amt
        self.assertIsInstance(pst.assigned_amount, ledger.Amount)
        self.assertEqual(pst.assigned_amount, amt)

        pst.assigned_amount = None
        self.assertIsNone(pst.assigned_amount)

    def test_posting_has_tag(self):

        pst = ledger.Posting(ledger.OriginPost())
        pst.set_tag("tag-1")

        self.assertTrue(pst.has_tag("tag-1"))
        self.assertFalse(pst.has_tag("tag-2"))

        self.assertTrue(pst.has_tag(ledger.Mask("tag-1")))
        self.assertFalse(pst.has_tag(ledger.Mask("tag-2")))

        pst.set_tag("tag-2", ledger.string_value("some-value"))
        self.assertFalse(pst.has_tag(ledger.Mask("tag-1"), ledger.Mask("some-value")))
        self.assertTrue(pst.has_tag(ledger.Mask("tag-2"), ledger.Mask("some-value")))
        self.assertFalse(pst.has_tag(ledger.Mask("tag-2"), ledger.Mask("unknown-value")))

    def test_posting_get_tag(self):

        pst = ledger.Posting(ledger.OriginPost())

        pst.set_tag("tag-1")
        self.assertFalse(bool(pst.get_tag("tag-1")))

        pst.set_tag("tag-2", ledger.string_value("some-value"))
        self.assertEqual("some-value", str(pst.get_tag("tag-2")))
        self.assertEqual("some-value", str(pst.get_tag(ledger.Mask("tag-2"))))
        self.assertEqual("some-value", str(pst.get_tag(ledger.Mask("tag-2"), ledger.Mask("some-value"))))
        self.assertFalse(bool(pst.get_tag(ledger.Mask("tag-2"), ledger.Mask("unknown-value"))))

    def test_posting_date(self):

        pst = ledger.Posting(ledger.OriginPost())
        dt = date(2021, 5, 12)

        pst.date = dt
        self.assertEqual(dt, pst.date)

    def test_posting_aux_date(self):

        pst = ledger.Posting(ledger.OriginPost())
        dt = date(2021, 5, 15)

        pst.aux_date = dt
        self.assertEqual(dt, pst.aux_date)

    def test_posting_must_balance(self):

        pst = ledger.Posting(ledger.OriginPost())
        self.assertTrue(pst.must_balance())

    def test_posting_has_xdata(self):

        pst = ledger.Posting(ledger.OriginPost())
        self.assertFalse(pst.has_xdata())

        self.assertIsNotNone(pst.xdata())
        self.assertTrue(pst.has_xdata())

    def test_posting_clear_xdata(self):

        pst = ledger.Posting(ledger.OriginPost())

        self.assertIsNotNone(pst.xdata())
        self.assertTrue(pst.has_xdata())

        pst.clear_xdata()
        self.assertFalse(pst.has_xdata())

    def test_posting_xdata(self):

        pst = ledger.Posting(ledger.OriginPost())
        self.assertIsNotNone(pst.xdata())
        self.assertIsInstance(pst.xdata(), ledger.PostingXData)

    def test_posting_reported_account(self):

        pst = ledger.Posting(ledger.OriginPost())

        acc = ledger.Account(None, "acc-name")
        pst.set_reported_account(acc)
        self.assertIsInstance(pst.reported_account(), ledger.Account)
        self.assertEqual("acc-name", pst.reported_account().name)

# Value tests

class MaskTests(unittest.TestCase):

    def test_mask_constructor(self):
        mask = ledger.Mask()
        self.assertIsInstance(mask, ledger.Mask)

        mask = ledger.Mask(ledger.OriginMask())
        self.assertIsInstance(mask, ledger.Mask)

        mask = ledger.Mask("pattern")
        self.assertIsInstance(mask, ledger.Mask)

    def test_mask_from_origin(self):
        mask = ledger.Mask.from_origin(ledger.OriginMask())
        self.assertIsInstance(mask, ledger.Mask)

        mask = ledger.Mask.from_origin(None)
        self.assertIsNone(mask)

    def test_mask_match(self):
        mask = ledger.Mask("pattern")
        self.assertTrue(mask.match("contains pattern"))
        self.assertFalse(mask.match("does not contain"))

    def test_mask_is_empty(self):
        mask = ledger.Mask()
        self.assertTrue(mask.is_empty)

        mask = ledger.Mask("pattern")
        self.assertFalse(mask.is_empty)

    def test_mask_str_method(self):
        mask = ledger.Mask("pattern")
        self.assertEqual("pattern", mask.str())

    def test_mask_str(self):
        mask = ledger.Mask("pattern")
        self.assertEqual("pattern", str(mask))

class ValueTests(unittest.TestCase):

    def test_value_constructor_takes_bool(self):
        val = ledger.Value(True)
        self.assertEqual(ledger.ValueType.Boolean, val.type())

    def test_value_constructor_takes_datetime(self):
        val = ledger.Value(datetime(2020,10,15,22,55,59))
        self.assertEqual(ledger.ValueType.DateTime, val.type())

    def test_value_constructor_takes_date(self):
        val = ledger.Value(date(2020,10,15))
        self.assertEqual(ledger.ValueType.Date, val.type())

    def test_value_constructor_takes_integer(self):
        val = ledger.Value(10)
        self.assertEqual(ledger.ValueType.Integer, val.type())

    def test_value_constructor_takes_double(self):
        val = ledger.Value(10.00)
        self.assertEqual(ledger.ValueType.Amount, val.type())

    def test_value_constructor_takes_amount(self):
        val = ledger.Value(ledger.Amount(20))
        self.assertEqual(ledger.ValueType.Amount, val.type())

    def test_value_constructor_takes_balance(self):
        val = ledger.Value(ledger.Balance(10))
        self.assertEqual(ledger.ValueType.Balance, val.type())

    def test_value_constructor_takes_mask(self):
        val = ledger.Value(ledger.Mask("ABC"))
        self.assertEqual(ledger.ValueType.Mask, val.type())

    def test_value_constructor_takes_str(self):
        val = ledger.Value("10")
        self.assertEqual(ledger.ValueType.Amount, val.type())

    def test_value_constructor_takes_another_value(self):
        val = ledger.Value(ledger.Value(10))
        self.assertEqual(ledger.ValueType.Integer, val.type())

    def test_value_is_equal_to(self):
        self.assertTrue(ledger.Value(10).is_equal_to(ledger.Value(10)))
        self.assertFalse(ledger.Value(10).is_equal_to(ledger.Value(20)))

    def test_value_is_less_than(self):
        self.assertFalse(ledger.Value(10).is_less_than(ledger.Value(10)))
        self.assertFalse(ledger.Value(10).is_less_than(ledger.Value(5)))
        self.assertTrue(ledger.Value(10).is_less_than(ledger.Value(20)))

    def test_value_is_less_than(self):
        self.assertFalse(ledger.Value(10).is_greater_than(ledger.Value(10)))
        self.assertTrue(ledger.Value(10).is_greater_than(ledger.Value(5)))
        self.assertFalse(ledger.Value(10).is_greater_than(ledger.Value(20)))

    def test_value_eq(self):
        self.assertTrue(ledger.Value(10) == ledger.Value(10))
        self.assertFalse(ledger.Value(10) == ledger.Value(20))

        self.assertTrue(ledger.Value(10) == 10)
        self.assertFalse(ledger.Value(10) == 20)

        self.assertTrue(10 == ledger.Value(10))
        self.assertFalse(20 == ledger.Value(10))

        self.assertTrue(ledger.Value(10.0) == ledger.Amount(10))
        self.assertFalse(ledger.Value(10.0) == ledger.Amount(20))

        self.assertTrue(ledger.Amount(10) == ledger.Value(10.0))
        self.assertFalse(ledger.Amount(20) == ledger.Value(10.0))

        self.assertTrue(ledger.Value(ledger.Balance(10)) == ledger.Balance(10))
        self.assertFalse(ledger.Value(ledger.Balance(10)) == ledger.Balance(20))

        self.assertTrue(ledger.Balance(10) == ledger.Value(ledger.Balance(10)))
        self.assertFalse(ledger.Balance(20) == ledger.Value(ledger.Balance(10)))

    def test_value_ne(self):
        self.assertFalse(ledger.Value(10) != ledger.Value(10))
        self.assertTrue(ledger.Value(10) != ledger.Value(20))

        self.assertFalse(ledger.Value(10) != 10)
        self.assertTrue(ledger.Value(10) != 20)

        self.assertFalse(10 != ledger.Value(10))
        self.assertTrue(20 != ledger.Value(10))

        self.assertFalse(ledger.Value(10.0) != ledger.Amount(10))
        self.assertTrue(ledger.Value(10.0) != ledger.Amount(20))

        self.assertFalse(ledger.Amount(10) != ledger.Value(10.0))
        self.assertTrue(ledger.Amount(20) != ledger.Value(10.0))

        self.assertFalse(ledger.Value(ledger.Balance(10)) != ledger.Balance(10))
        self.assertTrue(ledger.Value(ledger.Balance(10)) != ledger.Balance(20))

        self.assertFalse(ledger.Balance(10) != ledger.Value(ledger.Balance(10)))
        self.assertTrue(ledger.Balance(20) != ledger.Value(ledger.Balance(10)))

    def test_value_bool(self):
        self.assertFalse(ledger.Value(False))
        self.assertTrue(ledger.Value(True))

        self.assertTrue(not ledger.Value(False))
        self.assertFalse(not ledger.Value(True))

        self.assertFalse(bool(ledger.Value(False)))
        self.assertTrue(bool(ledger.Value(True)))

        self.assertTrue(not bool(ledger.Value(False)))
        self.assertFalse(not bool(ledger.Value(True)))

    def test_value_lt(self):
        self.assertFalse(ledger.Value(10) < ledger.Value(5))
        self.assertFalse(ledger.Value(10) < ledger.Value(10))
        self.assertTrue(ledger.Value(10) < ledger.Value(20))

        self.assertFalse(ledger.Value(10) < 5)
        self.assertFalse(ledger.Value(10) < 10)
        self.assertTrue(ledger.Value(10) < 20)

        self.assertTrue(5 < ledger.Value(10))
        self.assertFalse(10 < ledger.Value(10))
        self.assertFalse(20 < ledger.Value(10))

        self.assertFalse(ledger.Value(10.0) < ledger.Amount(5))
        self.assertFalse(ledger.Value(10.0) < ledger.Amount(10))
        self.assertTrue(ledger.Value(10.0) < ledger.Amount(20))

        self.assertTrue(ledger.Amount(5) < ledger.Value(10.0))
        self.assertFalse(ledger.Amount(10) < ledger.Value(10.0))
        self.assertFalse(ledger.Amount(20) < ledger.Value(10.0))

    def test_value_le(self):
        self.assertFalse(ledger.Value(10) <= ledger.Value(5))
        self.assertTrue(ledger.Value(10) <= ledger.Value(10))
        self.assertTrue(ledger.Value(10) <= ledger.Value(20))

        self.assertFalse(ledger.Value(10) <= 5)
        self.assertTrue(ledger.Value(10) <= 10)
        self.assertTrue(ledger.Value(10) <= 20)

        self.assertTrue(5 <= ledger.Value(10))
        self.assertTrue(10 <= ledger.Value(10))
        self.assertFalse(20 <= ledger.Value(10))

        self.assertFalse(ledger.Value(10.0) <= ledger.Amount(5))
        self.assertTrue(ledger.Value(10.0) <= ledger.Amount(10))
        self.assertTrue(ledger.Value(10.0) <= ledger.Amount(20))

        self.assertTrue(ledger.Amount(5) <= ledger.Value(10.0))
        self.assertTrue(ledger.Amount(10) <= ledger.Value(10.0))
        self.assertFalse(ledger.Amount(20) <= ledger.Value(10.0))

    def test_value_gt(self):
        self.assertTrue(ledger.Value(10) > ledger.Value(5))
        self.assertFalse(ledger.Value(10) > ledger.Value(10))
        self.assertFalse(ledger.Value(10) > ledger.Value(20))

        self.assertTrue(ledger.Value(10) > 5)
        self.assertFalse(ledger.Value(10) > 10)
        self.assertFalse(ledger.Value(10) > 20)

        self.assertFalse(5 > ledger.Value(10))
        self.assertFalse(10 > ledger.Value(10))
        self.assertTrue(20 > ledger.Value(10))

        self.assertTrue(ledger.Value(10.0) > ledger.Amount(5))
        self.assertFalse(ledger.Value(10.0) > ledger.Amount(10))
        self.assertFalse(ledger.Value(10.0) > ledger.Amount(20))

        self.assertFalse(ledger.Amount(5) > ledger.Value(10.0))
        self.assertFalse(ledger.Amount(10) > ledger.Value(10.0))
        self.assertTrue(ledger.Amount(20) > ledger.Value(10.0))

    def test_value_ge(self):
        self.assertTrue(ledger.Value(10) >= ledger.Value(5))
        self.assertTrue(ledger.Value(10) >= ledger.Value(10))
        self.assertFalse(ledger.Value(10) >= ledger.Value(20))

        self.assertTrue(ledger.Value(10) >= 5)
        self.assertTrue(ledger.Value(10) >= 10)
        self.assertFalse(ledger.Value(10) >= 20)

        self.assertFalse(5 >= ledger.Value(10))
        self.assertTrue(10 >= ledger.Value(10))
        self.assertTrue(20 >= ledger.Value(10))

        self.assertTrue(ledger.Value(10.0) >= ledger.Amount(5))
        self.assertTrue(ledger.Value(10.0) >= ledger.Amount(10))
        self.assertFalse(ledger.Value(10.0) >= ledger.Amount(20))

        self.assertFalse(ledger.Amount(5) >= ledger.Value(10.0))
        self.assertTrue(ledger.Amount(10) >= ledger.Value(10.0))
        self.assertTrue(ledger.Amount(20) >= ledger.Value(10.0))

    def test_value_add(self):
        self.assertEqual(5, ledger.Value(2) + ledger.Value(3))
        self.assertEqual(5, ledger.Value(2) + 3)
        self.assertEqual(5, 2 + ledger.Value(3))
        self.assertEqual(5, ledger.Value(2) + ledger.Amount(3))
        self.assertEqual(5, ledger.Amount(2) + ledger.Value(3))
        self.assertEqual(5, ledger.Value(2) + ledger.Balance(3))

    def test_value_add_assignment(self):

        val = ledger.Value(2)
        val += ledger.Value(3)
        self.assertEqual(5, val)

        val = ledger.Value(2)
        val += 3
        self.assertEqual(5, val)

        val = ledger.Value(2)
        val += ledger.Amount(3)
        self.assertEqual(5, val)

        val = ledger.Value(2)
        val += ledger.Balance(3)
        self.assertEqual(5, val)

    def test_value_sub(self):
        self.assertEqual(2, ledger.Value(5) - ledger.Value(3))
        self.assertEqual(2, ledger.Value(5) - 3)
        self.assertEqual(2, 5 - ledger.Value(3))
        self.assertEqual(2, ledger.Value(5) - ledger.Amount(3))
        self.assertEqual(2, ledger.Amount(5) - ledger.Value(3))
        self.assertEqual(2, ledger.Value(5) - ledger.Balance(3))

    def test_value_sub_assignment(self):

        val = ledger.Value(5)
        val -= ledger.Value(3)
        self.assertEqual(2, val)

        val = ledger.Value(5)
        val -= 3
        self.assertEqual(2, val)

        val = ledger.Value(5)
        val -= ledger.Amount(3)
        self.assertEqual(2, val)

        val = ledger.Value(5)
        val -= ledger.Balance(3)
        self.assertEqual(2, val)

    def test_value_mul(self):
        self.assertEqual(6, ledger.Value(2) * ledger.Value(3))
        self.assertEqual(6, ledger.Value(2) * 3)
        self.assertEqual(6, 2 * ledger.Value(3))
        self.assertEqual(6, ledger.Value(2) * ledger.Amount(3))
        self.assertEqual(6, ledger.Amount(2) * ledger.Value(3))

    def test_value_mul_assignment(self):

        val = ledger.Value(2)
        val *= ledger.Value(3)
        self.assertEqual(6, val)

        val = ledger.Value(2)
        val *= 3
        self.assertEqual(6, val)

        val = ledger.Value(2)
        val *= ledger.Amount(3)
        self.assertEqual(6, val)

    def test_value_div(self):
        self.assertEqual(2, ledger.Value(6) / ledger.Value(3))
        self.assertEqual(2, ledger.Value(6) / 3)
        self.assertEqual(2, 6 / ledger.Value(3))
        self.assertEqual(2, ledger.Value(6) / ledger.Value(ledger.Amount(3)))
        self.assertEqual(2, ledger.Amount(6) / ledger.Value(3))

    def test_value_div_assignment(self):

        val = ledger.Value(6)
        val /= ledger.Value(3)
        self.assertEqual(2, val)

        val = ledger.Value(6)
        val /= 3
        self.assertEqual(2, val)

        val = ledger.Value(6)
        val /= ledger.Amount(3)
        self.assertEqual(2, val)

    def test_value_negated(self):

        val1 = ledger.Value(6)
        val2 = val1.negated()
        self.assertEqual(6, val1)
        self.assertEqual(-6, val2)
        self.assertTrue(isinstance(val2, ledger.Value))

    def test_value_in_place_negate(self):

        val1 = ledger.Value(6)
        val1.in_place_negate()
        self.assertEqual(-6, val1)
        self.assertTrue(isinstance(val1, ledger.Value))

    def test_value_in_place_not(self):

        val1 = ledger.Value(False)
        val1.in_place_negate()
        self.assertEqual(True, val1)
        self.assertTrue(isinstance(val1, ledger.Value))

    def test_value_neg(self):

        val1 = ledger.Value(6)
        val2 = -val1
        self.assertEqual(6, val1)
        self.assertEqual(-6, val2)
        self.assertTrue(isinstance(val2, ledger.Value))

    def test_value_abs(self):

        val1 = ledger.Value(-6)
        val2 = val1.abs()
        self.assertEqual(-6, val1)
        self.assertEqual(6, val2)
        self.assertTrue(isinstance(val2, ledger.Value))

    def test_value_rounded(self):

        amt = ledger.Amount("2.00 ZXC")
        amt.keep_precision = True
        
        v1 = ledger.Value(amt)
        v2 = v1 / 3

        self.assertEqual("2.00 ZXC", str(v1))
        self.assertEqual("0.66666667 ZXC", str(v2))
        self.assertEqual("0.67 ZXC", str(v2.rounded()))
        self.assertEqual("<class 'ledger.Value'>", str(type(v2.rounded())))

    def test_value_in_place_round(self):

        amt = ledger.Amount("2.00 ZXC")
        amt.keep_precision = True

        v1 = ledger.Value(amt)
        v1 = v1 / 3
        
        self.assertEqual("0.66666667 ZXC", str(v1))
        v1.in_place_round()
        self.assertEqual("0.67 ZXC", str(v1))
        self.assertEqual("<class 'ledger.Value'>", str(type(v1)))

    def test_value_truncated(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXC"))
        a2 = a1 / 3

        self.assertEqual("2.00 ZXC", str(a1))
        self.assertEqual("0.67 ZXC", str(a2))
        self.assertEqual("0.67 ZXC", str(a2.truncated()))
        self.assertEqual("<class 'ledger.Value'>", str(type(a2.truncated())))

    def test_value_in_place_truncate(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXC"))
        a1 = a1 / 3
        
        a1.in_place_truncate()
        self.assertEqual("0.67 ZXC", str(a1))
        self.assertEqual("<class 'ledger.Value'>", str(type(a1)))

    def test_value_floored(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXD"))
        a2 = a1 / 3

        self.assertEqual("2.00 ZXD", str(a1))
        self.assertEqual("0.67 ZXD", str(a2))
        self.assertEqual("0.00 ZXD", str(a2.floored()))
        self.assertEqual("<class 'ledger.Value'>", str(type(a2.floored())))

    def test_value_in_place_floor(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXD"))
        a1 = a1 / 3
        
        a1.in_place_floor()
        self.assertEqual("0.00 ZXD", str(a1))
        self.assertEqual("<class 'ledger.Value'>", str(type(a1)))

    def test_value_unrounded(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXD"))
        a2 = a1 / 3

        self.assertEqual("2.00 ZXD", str(a1))
        self.assertEqual("0.67 ZXD", str(a2))
        self.assertEqual("0.66666667 ZXD", str(a2.unrounded()))
        self.assertEqual("<class 'ledger.Value'>", str(type(a2.unrounded())))

    def test_value_in_place_unround(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXD"))
        a1 = a1 / 3
        
        a1.in_place_unround()
        self.assertEqual("0.66666667 ZXD", str(a1))
        self.assertEqual("<class 'ledger.Value'>", str(type(a1)))

    def test_value_reduced(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXD"))
        a2 = a1 / 3

        self.assertEqual("2.00 ZXD", str(a1))
        self.assertEqual("0.67 ZXD", str(a2))
        self.assertEqual("0.67 ZXD", str(a2.reduced()))
        self.assertEqual("<class 'ledger.Value'>", str(type(a2.reduced())))

    def test_value_in_place_reduce(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXD"))
        a1 = a1 / 3
        
        a1.in_place_reduce()
        self.assertEqual("0.67 ZXD", str(a1))
        self.assertEqual("<class 'ledger.Value'>", str(type(a1)))

    def test_value_unreduced(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXD"))
        a2 = a1 / 3

        self.assertEqual("2.00 ZXD", str(a1))
        self.assertEqual("0.67 ZXD", str(a2))
        self.assertEqual("0.67 ZXD", str(a2.unreduced()))
        self.assertEqual("<class 'ledger.Value'>", str(type(a2.unreduced())))

    def test_value_in_place_unreduce(self):

        a1 = ledger.Value(ledger.Amount("2.00 ZXD"))
        a1 = a1 / 3
        
        a1.in_place_unreduce()
        self.assertEqual("0.67 ZXD", str(a1))
        self.assertEqual("<class 'ledger.Value'>", str(type(a1)))

    def test_value_value(self):

        amt = ledger.Amount("2.00 ZWS")
        val = ledger.Value(amt)
        v1 = val.value()
        v2 = val.value(amt.commodity)
        v3 = val.value(amt.commodity, date.today())
        v4 = val.value(amt.commodity, datetime.today())
        self.assertTrue(isinstance(v1, ledger.Value))
        self.assertTrue(isinstance(v2, ledger.Value))
        self.assertTrue(isinstance(v3, ledger.Value))
        self.assertTrue(isinstance(v4, ledger.Value))

    def test_value_exchange_commodities(self):

        amt = ledger.Amount("2.00 ZWG")
        val = ledger.Value(amt)
        v1 = val.exchange_commodities("ZWG")
        v2 = val.exchange_commodities("ZWG", True)
        v3 = val.exchange_commodities("ZWG", False, date.today())
        self.assertTrue(isinstance(v1, ledger.Value))
        self.assertTrue(isinstance(v2, ledger.Value))
        self.assertTrue(isinstance(v3, ledger.Value))

    def test_value_is_nonzero(self):

        self.assertTrue(ledger.Value(1).is_nonzero())
        self.assertFalse(ledger.Value(0).is_nonzero())

    def test_value_is_zero(self):

        self.assertFalse(ledger.Value(1).is_zero())
        self.assertTrue(ledger.Value(0).is_zero())

    def test_value_is_null(self):

        self.assertFalse(ledger.Value(1).is_null())
        self.assertFalse(ledger.Value(0).is_null())
        self.assertTrue(ledger.Value(ledger.NULL_VALUE.is_null()))

    def test_value_type(self):

        self.assertEqual(ledger.ValueType.Void, ledger.NULL_VALUE.type())
        self.assertEqual(ledger.ValueType.Boolean, ledger.Value(True).type())
        self.assertEqual(ledger.ValueType.Date, ledger.Value(date.today()).type())
        self.assertEqual(ledger.ValueType.DateTime, ledger.Value(datetime.today()).type())
        self.assertEqual(ledger.ValueType.Integer, ledger.Value(1).type())
        self.assertEqual(ledger.ValueType.Amount, ledger.Value(1.0).type())
        self.assertEqual(ledger.ValueType.Balance, ledger.Value(ledger.Balance(1)).type())
        self.assertEqual(ledger.ValueType.String, ledger.string_value("A").type())
        self.assertEqual(ledger.ValueType.Mask, ledger.Value(ledger.Mask("A")).type())

    def test_value_is_type(self):

        self.assertTrue(ledger.NULL_VALUE.is_type(ledger.ValueType.Void))
        self.assertFalse(ledger.NULL_VALUE.is_type(ledger.ValueType.Boolean))

        self.assertTrue(ledger.Value(True).is_type(ledger.ValueType.Boolean))
        self.assertTrue(ledger.Value(date.today()).is_type(ledger.ValueType.Date))
        self.assertTrue(ledger.Value(datetime.today()).is_type(ledger.ValueType.DateTime))
        self.assertTrue(ledger.Value(1).is_type(ledger.ValueType.Integer))
        self.assertTrue(ledger.Value(1.0).is_type(ledger.ValueType.Amount))
        self.assertTrue(ledger.Value(ledger.Balance(1)).is_type(ledger.ValueType.Balance))
        self.assertTrue(ledger.string_value("A").is_type(ledger.ValueType.String))
        self.assertTrue(ledger.Value(ledger.Mask("A")).is_type(ledger.ValueType.Mask))

    def test_value_is_boolean(self):

        self.assertTrue(ledger.Value(False).is_boolean())
        self.assertTrue(ledger.Value(True).is_boolean())
        self.assertFalse(ledger.Value(1).is_boolean())

    def test_value_set_boolean(self):

        val = ledger.Value(10)
        self.assertFalse(val.is_boolean())
        val.set_boolean(False)
        self.assertTrue(val.is_boolean())

    def test_value_is_datetime(self):

        self.assertTrue(ledger.Value(datetime.today()).is_datetime())
        self.assertFalse(ledger.Value(1).is_datetime())

    def test_value_set_datetime(self):

        val = ledger.Value(10)
        self.assertFalse(val.is_datetime())
        val.set_datetime(datetime.today())
        self.assertTrue(val.is_datetime())

    def test_value_is_date(self):

        self.assertTrue(ledger.Value(date.today()).is_date())
        self.assertFalse(ledger.Value(1).is_date())

    def test_value_set_date(self):

        val = ledger.Value(10)
        self.assertFalse(val.is_date())
        val.set_date(date.today())
        self.assertTrue(val.is_date())

    def test_value_is_long(self):

        self.assertTrue(ledger.Value(1).is_long())
        self.assertFalse(ledger.Value(1.0).is_long())

    def test_value_set_long(self):

        val = ledger.Value(1.0)
        self.assertFalse(val.is_long())
        val.set_long(1)
        self.assertTrue(val.is_long())

    def test_value_is_amount(self):

        self.assertTrue(ledger.Value(1.0).is_amount())
        self.assertFalse(ledger.Value(1).is_amount())

    def test_value_set_amount(self):

        val = ledger.Value(1)
        self.assertFalse(val.is_amount())
        val.set_amount(ledger.Amount(1))
        self.assertTrue(val.is_amount())

    def test_value_is_balance(self):

        self.assertTrue(ledger.Value(ledger.Balance(10)).is_balance())
        self.assertFalse(ledger.Value(1).is_balance())

    def test_value_set_balance(self):

        val = ledger.Value(1)
        self.assertFalse(val.is_balance())
        val.set_balance(ledger.Balance(1))
        self.assertTrue(val.is_balance())

    def test_value_is_string(self):

        self.assertTrue(ledger.string_value("A").is_string())
        self.assertFalse(ledger.Value(1).is_string())

    def test_value_set_string(self):

        val = ledger.Value(1)
        self.assertFalse(val.is_string())
        val.set_string("A")
        self.assertTrue(val.is_string())

    def test_value_is_mask(self):

        self.assertTrue(ledger.Value(ledger.Mask("A")).is_mask())
        self.assertFalse(ledger.Value(1).is_mask())

    def test_value_set_mask(self):

        val = ledger.Value(1)
        self.assertFalse(val.is_mask())
        val.set_mask(ledger.Mask("A"))
        self.assertTrue(val.is_mask())

    def test_value_is_sequence(self):

        seq = (ledger.Value(1), ledger.Value(2), ledger.Value(3))
        val = ledger.Value(ledger.ValueList(seq))

        self.assertTrue(val.is_sequence())
        self.assertFalse(ledger.Value(1).is_sequence())

    def test_value_set_sequence(self):

        val = ledger.Value(1)
        self.assertFalse(val.is_sequence())
        val.set_sequence((ledger.Value(1),ledger.Value(2)))
        self.assertTrue(val.is_sequence())

    def test_value_to_boolean(self):

        self.assertEqual(False, ledger.Value(False).to_boolean())
        self.assertEqual(True, ledger.Value(True).to_boolean())
        self.assertEqual(False, ledger.Value(0).to_boolean())
        self.assertEqual(True, ledger.Value(1).to_boolean())

    def test_value_to_long(self):

        self.assertEqual(0, ledger.Value(False).to_long())
        self.assertEqual(1, ledger.Value(True).to_long())
        self.assertEqual(0, ledger.Value(0).to_long())
        self.assertEqual(1, ledger.Value(1).to_long())

    def test_value_to_datetime(self):

        self.assertEqual(datetime(2021, 5, 22, 23, 55, 55), ledger.Value(datetime(2021, 5, 22, 23, 55, 55)).to_datetime())
        self.assertEqual(datetime(2021, 5, 22, 0, 0, 0), ledger.Value(date(2021, 5, 22)).to_datetime())

    def test_value_to_date(self):

        self.assertEqual(date(2021, 5, 22), ledger.Value(datetime(2021, 5, 22, 0, 0, 0)).to_date())
        self.assertEqual(date(2021, 5, 22), ledger.Value(date(2021, 5, 22)).to_date())

    def test_value_to_amount(self):

        self.assertEqual(ledger.Amount(1), ledger.Value(1).to_amount())
        self.assertEqual(ledger.Amount(1), ledger.Value(1.0).to_amount())
        self.assertEqual(ledger.Amount(1), ledger.Value(ledger.Amount(1)).to_amount())

    def test_value_to_balance(self):

        bal = ledger.Value(1).to_balance()
        self.assertTrue(isinstance(bal, ledger.Balance))

    def test_value_to_string(self):

        self.assertEqual('false', ledger.Value(False).to_string())
        self.assertEqual('true', ledger.Value(True).to_string())
        self.assertEqual('0', ledger.Value(0).to_string())
        self.assertEqual('1', ledger.Value(1).to_string())

    def test_value_str(self):

        self.assertEqual('false', str(ledger.Value(False)))
        self.assertEqual('true', str(ledger.Value(True)))
        self.assertEqual('0', str(ledger.Value(0)))
        self.assertEqual('1', str(ledger.Value(1)))

    def test_value_to_mask(self):

        mask = ledger.string_value("A").to_mask()
        self.assertTrue(isinstance(mask, ledger.Mask))

    def test_value_to_sequence(self):

        seq = ledger.string_value("A").to_sequence()
        self.assertTrue(isinstance(seq, collections.abc.Iterable))
        self.assertEqual("A", seq[0].to_string())
        self.assertEqual(ledger.ValueType.String, seq[0].type())

        seq = (ledger.Value(10),ledger.Value(20))
        val = ledger.Value(ledger.ValueList(seq))
        self.assertEqual(2, len(val.to_sequence()))
        val.to_sequence().append(ledger.Value(30))
        self.assertEqual(3, len(val.to_sequence()))


    def test_value_repr(self):

        self.assertEqual("10 UUP", repr(ledger.Value("10 UUP")))

    def test_value_casted(self):

        val = ledger.Value(1)
        self.assertEqual(ledger.ValueType.String, val.casted(ledger.ValueType.String).type())
        self.assertEqual(ledger.ValueType.Integer, val.casted(ledger.ValueType.Integer).type())

    def test_value_in_place_cast(self):

        val = ledger.Value(1)
        self.assertEqual(ledger.ValueType.Integer, val.type())
        val.in_place_cast(ledger.ValueType.String)
        self.assertEqual(ledger.ValueType.String, val.type())

    def test_value_simplified(self):

        val = ledger.Value(ledger.Amount(0))
        self.assertEqual(ledger.ValueType.Integer, val.simplified().type())

    def test_value_in_place_simplify(self):

        val = ledger.Value(ledger.Amount(0))
        val.in_place_simplify()
        self.assertEqual(ledger.ValueType.Integer, val.type())

    def test_value_number(self):

        val = ledger.Value(False).number()
        self.assertEqual(ledger.ValueType.Integer, val.type())
        self.assertEqual("0", str(val))

        val = ledger.Value(True).number()
        self.assertEqual(ledger.ValueType.Integer, val.type())
        self.assertEqual("1", str(val))

    def test_value_annotate_and_annotation(self):

        ann = ledger.Annotation(ledger.OriginAnnotation(ledger.Amount(5), None, "tag"))
        val = ledger.Value(ledger.Amount("10 TTR"))
        
        val.annotate(ann)
        ann1 = val.annotation

        self.assertEqual(ann, ann1)

    def test_value_has_annotation(self):

        ann = ledger.Annotation(ledger.OriginAnnotation(ledger.Amount(5), None, "tag"))
        val = ledger.Value(ledger.Amount("10 TTR"))

        self.assertFalse(val.has_annotation())        
        val.annotate(ann)
        self.assertTrue(val.has_annotation())        

    def test_value_strip_annotations(self):

        ann = ledger.Annotation(ledger.OriginAnnotation(ledger.Amount(5), None, "tag"))
        val = ledger.Value(ledger.Amount("10 TTR"))
        
        self.assertFalse(val.has_annotation())        
        val.annotate(ann)
        self.assertTrue(val.has_annotation())
        val.strip_annotations()
        self.assertTrue(val.has_annotation())
        keepDetails = ledger.KeepDetails()
        val.strip_annotations(keepDetails)
        self.assertTrue(val.has_annotation())

    def test_value_push_back(self):

        val = ledger.Value(1)
        val.push_back(ledger.Value(2))
        self.assertEqual(2, len(val.to_sequence()))

    def test_value_pop_back(self):

        val = ledger.Value(1)
        val.push_back(ledger.Value(2))
        self.assertEqual(2, len(val.to_sequence()))
        val.pop_back()
        self.assertEqual(1, len(val.to_sequence()))

    def test_value_size(self):

        val = ledger.Value(1)
        val.push_back(ledger.Value(2))
        self.assertEqual(2, val.size())
        val.pop_back()
        self.assertEqual(1, val.size())

    def test_value_label(self):

        self.assertEqual("a boolean", ledger.Value(True).label())
        self.assertEqual("an integer", ledger.Value(1).label())

    def test_value_valid(self):

        self.assertTrue(ledger.Value(False).valid())

    def test_value_basetype(self):

        self.assertEqual(type(bool), ledger.Value(False).basetype())
        self.assertEqual(type(int), ledger.Value(1).basetype())
        self.assertEqual(type(str), ledger.string_value("A").basetype())

    def test_string_value(self):

        val = ledger.string_value("A")
        self.assertTrue(isinstance(val, ledger.Value))
        self.assertEqual(ledger.ValueType.String, val.type())
        self.assertEqual("A", val.to_string())

    def test_mask_value(self):

        val = ledger.mask_value("A")
        self.assertTrue(isinstance(val, ledger.Value))
        self.assertEqual(ledger.ValueType.Mask, val.type())
        self.assertEqual("A", val.to_string())

    def test_value_context(self):

        val = ledger.mask_value("A")
        self.assertEqual('                 /A/', ledger.value_context(val))

    def test_NULL_VALUE(self):

        self.assertEqual(ledger.ValueType.Void, ledger.NULL_VALUE.type())

# Transactions

class TransactionBaseTests(unittest.TestCase):

    def test_transactionbase_constructor(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        self.assertIsInstance(tbase, ledger.TransactionBase)

    def test_transactionbase_from_origin(self):
        tbase = ledger.TransactionBase.from_origin(ledger.OriginXact())
        self.assertIsInstance(tbase, ledger.TransactionBase)

        tbase = ledger.TransactionBase.from_origin(None)
        self.assertIsNone(tbase)

    def test_transactionbase_journal(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        self.assertIsNone(tbase.journal)

        tbase.journal = ledger.Journal()
        self.assertIsInstance(tbase.journal, ledger.Journal)

        tbase.journal = None
        self.assertIsNone(tbase.journal)

    def test_transactionbase_len(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        self.assertEqual(0, len(tbase))

        tbase.add_post(ledger.Posting())
        self.assertEqual(1, len(tbase))

    def test_transactionbase_getitem(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        post = ledger.Posting()

        tbase.add_post(post)
        self.assertEqual(post, tbase[0])
        self.assertIsInstance(tbase[0], ledger.Posting)

    def test_transactionbase_add_post(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        tbase.add_post(ledger.Posting())
        tbase.add_post(ledger.Posting())
        self.assertEqual(2, len(tbase))

    def test_transactionbase_remove_post(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        post1 = ledger.Posting()
        post2 = ledger.Posting()

        tbase.add_post(post1)
        tbase.add_post(post2)
        self.assertEqual(2, len(tbase))
        self.assertTrue(tbase.remove_post(post1))
        self.assertEqual(1, len(tbase))
        self.assertTrue(tbase.remove_post(post2))
        self.assertEqual(0, len(tbase))
        self.assertTrue(tbase.remove_post(post2))

    def test_transactionbase_finalize(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        self.assertFalse(tbase.finalize())

    def test_transactionbase_valid(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        self.assertFalse(tbase.valid())

    def test_transactionbase_posts(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        tbase.add_post(ledger.Posting())
        tbase.add_post(ledger.Posting())

        posts = tbase.posts()
        self.assertIsInstance(posts, Iterable)
        self.assertEqual(2, len(posts))
        for item in posts:
            self.assertIsInstance(item, ledger.Posting)        
    
    def test_transactionbase_iter(self):
        tbase = ledger.TransactionBase(ledger.OriginXact())
        tbase.add_post(ledger.Posting())
        tbase.add_post(ledger.Posting())

        self.assertIsInstance(tbase, Iterable)
        self.assertEqual(2, len(tbase))
        for item in tbase:
            self.assertIsInstance(item, ledger.Posting)        

class TransactionTests(unittest.TestCase):

    def test_transaction_constructor(self):
        trx = ledger.Transaction(ledger.OriginXact())
        self.assertIsInstance(trx, ledger.Transaction)

    def test_transaction_from_origin(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        self.assertIsInstance(trx, ledger.Transaction)

        trx = ledger.Transaction.from_origin(None)
        self.assertIsNone(trx)

    def test_transaction_id(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        self.assertEqual("0", trx.id())

    def test_transaction_seq(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        self.assertEqual(0, trx.seq())

    def test_transaction_code(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        self.assertIsNone(trx.code)

        trx.code = "code"
        self.assertEqual("code", trx.code)

        trx.code = None
        self.assertIsNone(trx.code)

    def test_transaction_payee(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        self.assertIsNone(trx.payee)

        trx.payee = "payee"
        self.assertEqual("payee", trx.payee)

        trx.payee = None
        self.assertIsNone(trx.payee)

    def test_transaction_magnitude(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        magnitude = trx.magnitude()
        self.assertIsInstance(magnitude, ledger.Value)
        self.assertEqual(0, magnitude)

    def test_transaction_has_xdata(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        self.assertFalse(trx.has_xdata())

    def test_transaction_clear_xdata(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        trx.clear_xdata()
        self.assertFalse(trx.has_xdata())

    def test_transaction_str(self):
        trx = ledger.Transaction.from_origin(ledger.OriginXact())
        self.assertEqual("", str(trx))

class PeriodicTransactionTests(unittest.TestCase):

    def test_periodictransaction_constructor(self):
        trx = ledger.PeriodicTransaction(ledger.OriginPeriodXact())
        self.assertIsInstance(trx, ledger.PeriodicTransaction)

    def test_periodictransaction_from_origin(self):
        trx = ledger.PeriodicTransaction.from_origin(ledger.OriginPeriodXact())
        self.assertIsInstance(trx, ledger.PeriodicTransaction)

        trx = ledger.PeriodicTransaction.from_origin(None)
        self.assertIsNone(trx)

    def test_periodictransaction_from_origin(self):
        trx = ledger.PeriodicTransaction(ledger.OriginPeriodXact())
        self.assertIsNone(trx.period)

    def test_periodictransaction_period_string(self):
        trx = ledger.PeriodicTransaction(ledger.OriginPeriodXact())
        self.assertIsNone(trx.period_string)

class AutomatedTransactionTransactionTests(unittest.TestCase):

    def test_autotransaction_constructor(self):
        trx = ledger.AutomatedTransaction(ledger.OriginAutoXact())
        self.assertIsInstance(trx, ledger.AutomatedTransaction)

    def test_autotransaction_from_origin(self):
        trx = ledger.AutomatedTransaction.from_origin(ledger.OriginAutoXact())
        self.assertIsInstance(trx, ledger.AutomatedTransaction)

        trx = ledger.AutomatedTransaction.from_origin(None)
        self.assertIsNone(trx)

    def test_autotransaction_predicate(self):
        trx = ledger.AutomatedTransaction()
        self.assertIsNone(trx.predicate)

    def test_autotransaction_extend_xact(self):
        trx = ledger.AutomatedTransaction()
        trx.extend_xact(ledger.AutomatedTransaction())
        self.assertTrue(trx.valid())

# Amount tests

class AmountTests(unittest.TestCase):

    def test_amount_number_constructors(self):

        amount = ledger.Amount(10)
        self.assertEqual("10",str(amount))

        amount = ledger.Amount(20)
        self.assertEqual("20",str(amount))

    def test_amount_str_constructors(self):

        amount = ledger.Amount("10")
        self.assertEqual("10",str(amount))

        amount = ledger.Amount("20 EUR")
        self.assertEqual("20 EUR",str(amount))

    def test_amount_exact(self):

        amount = ledger.Amount.exact("20 EUR")
        self.assertEqual("20 EUR",str(amount))

    def test_amount_classname(self):

        amount = ledger.Amount(10)
        self.assertEqual("<class 'ledger.Amount'>",str(type(amount)))

    def test_amount_eq(self):

        # Amount vs amount

        a1 = ledger.Amount("20 EUR")
        a2 = ledger.Amount("30 EUR")
        a3 = ledger.Amount("20 EUR")

        self.assertFalse(a1 == a2)
        self.assertTrue(a1 != a2)

        self.assertTrue(a1 == a3)
        self.assertFalse(a1 != a3)

        # Amount vs number

        a1 = ledger.Amount("20")
        
        self.assertTrue(a1 == 20)
        self.assertFalse(a1 != 20)
        self.assertFalse(a1 == 30)
        self.assertTrue(a1 != 30)

        self.assertTrue(20 == a1)
        self.assertFalse(20 != a1)
        self.assertFalse(30 == a1)
        self.assertTrue(30 != a1)

    def test_amount_bool(self):

        a1 = ledger.Amount(0)
        a2 = ledger.Amount(10)

        self.assertFalse(bool(a1))
        self.assertTrue(bool(a2))

        self.assertFalse(a1)
        self.assertTrue(a2)

        self.assertTrue(not a1)
        self.assertFalse(not a2)

    def test_amount_less(self):

        a1 = ledger.Amount(0)
        a2 = ledger.Amount(10)
        a3 = ledger.Amount(10)

        self.assertTrue(a1 < a2)
        self.assertTrue(a1 <= a2)

        self.assertFalse(a2 < a1)
        self.assertFalse(a2 <= a1)

        self.assertFalse(a2 < a3)
        self.assertTrue(a2 <= a3)

        self.assertFalse(a3 < a2)
        self.assertTrue(a3 <= a2)

        self.assertTrue(0 < a2)
        self.assertTrue(0 <= a2)

        self.assertFalse(a2 < 0)
        self.assertFalse(a2 <= 0)

        self.assertFalse(10 < a3)
        self.assertTrue(10 <= a3)

        self.assertFalse(a3 < 10)
        self.assertTrue(a3 <= 10)

    def test_amount_greater(self):

        a1 = ledger.Amount(0)
        a2 = ledger.Amount(10)
        a3 = ledger.Amount(10)

        self.assertFalse(a1 > a2)
        self.assertFalse(a1 >= a2)

        self.assertTrue(a2 > a1)
        self.assertTrue(a2 >= a1)

        self.assertFalse(a2 > a3)
        self.assertTrue(a2 >= a3)

        self.assertFalse(a3 > a2)
        self.assertTrue(a3 >= a2)

        self.assertFalse(0 > a2)
        self.assertFalse(0 >= a2)

        self.assertTrue(a2 > 0)
        self.assertTrue(a2 >= 0)

        self.assertFalse(10 > a3)
        self.assertTrue(10 >= a3)

        self.assertFalse(a3 > 10)
        self.assertTrue(a3 >= 10)

    def test_amount_plus(self):

        a1 = ledger.Amount(10)
        a2 = ledger.Amount(10)
        a3 = ledger.Amount(20)

        self.assertEqual(a3, a1 + a2)
        self.assertEqual(a3, a1 + 10)
        self.assertEqual(a3, 10 + a1)

        a1 += a2
        a2 += 10
        self.assertEqual(a3, a1)
        self.assertEqual(a3, a2)

        self.assertEqual("<class 'ledger.Amount'>", str(type(a1 + a2)))
        self.assertEqual("<class 'ledger.Amount'>", str(type(10 + a2)))

    def test_amount_minus(self):

        a1 = ledger.Amount(30)
        a2 = ledger.Amount(10)
        a3 = ledger.Amount(20)

        self.assertEqual(a3, a1 - a2)
        self.assertEqual(a3, a1 - 10)
        self.assertEqual(a3, 30 - a2)

        a1 -= a2
        self.assertEqual(a3, a1)
        a3 -= 10
        self.assertEqual(a2, a3)

        self.assertEqual("<class 'ledger.Amount'>", str(type(a1 - a2)))
        self.assertEqual("<class 'ledger.Amount'>", str(type(10 - a2)))

    def test_amount_multiply(self):

        a1 = ledger.Amount(2)
        a2 = ledger.Amount(3)
        a3 = ledger.Amount(6)

        self.assertEqual(a3, a1 * a2)
        self.assertEqual(a3, a1 * 3)
        self.assertEqual(a3, 2 * a2)

        a1 *= a2
        a2 *= 2
        self.assertEqual(a3, a1)
        self.assertEqual(a3, a2)

        self.assertEqual("<class 'ledger.Amount'>", str(type(a1 * a2)))
        self.assertEqual("<class 'ledger.Amount'>", str(type(10 * a2)))

    def test_amount_divide(self):

        a1 = ledger.Amount(6)
        a2 = ledger.Amount(3)
        a3 = ledger.Amount(2)

        self.assertEqual(a3, a1 / a2)
        self.assertEqual(a3, a1 / 3)
        self.assertEqual(a2, 6 / a3)

        a1 /= a2
        self.assertEqual(a3, a1)

        a1 = ledger.Amount(6)
        a1 /= 2
        self.assertEqual(a2, a1)

        self.assertEqual("<class 'ledger.Amount'>", str(type(a2 / a2)))
        self.assertEqual("<class 'ledger.Amount'>", str(type(6 / a2)))

    def test_amount_neg(self):

        a1 = ledger.Amount(6)
        a2 = ledger.Amount(-6)

        self.assertEqual(a1, -a2)
        self.assertEqual(a2, -a1)
        self.assertEqual("<class 'ledger.Amount'>", str(type(-a1)))

    def test_amount_precision(self):

        a1 = ledger.Amount(10)
        self.assertEqual(0, a1.precision)

        a1 = ledger.Amount("11.11 ZXA")
        self.assertEqual(2, a1.precision)

    def test_amount_display_precision(self):

        a1 = ledger.Amount(10)
        self.assertEqual(0, a1.display_precision)

        a1 = ledger.Amount("11.11 ZXB")
        self.assertEqual(2, a1.display_precision)

    def test_amount_keep_precision(self):

        a1 = ledger.Amount(10)
        self.assertFalse(a1.keep_precision)
        a1.keep_precision = True
        self.assertTrue(a1.keep_precision)
        a1.keep_precision = False
        self.assertFalse(a1.keep_precision)

    def test_amount_negated(self):

        a1 = ledger.Amount(10)
        a2 = a1.negated()

        self.assertEqual(ledger.Amount(-10), a2)
        self.assertEqual(ledger.Amount(10), a1)
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2)))

    def test_amount_in_place_negate(self):

        a1 = ledger.Amount(10)
        a2 = a1.in_place_negate()

        self.assertEqual(ledger.Amount(-10), a2)
        self.assertEqual(ledger.Amount(-10), a1)
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2)))

    def test_amount_abs(self):

        a1 = ledger.Amount(-10)
        a2 = a1.abs()

        self.assertEqual(ledger.Amount(10), a2)
        self.assertEqual(ledger.Amount(-10), a1)
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2)))

    def test_amount_inverted(self):

        a1 = ledger.Amount(10)
        a2 = a1.inverted()

        self.assertEqual(ledger.Amount(0.1), a2)
        self.assertEqual(ledger.Amount(10), a1)
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2)))

    def test_amount_rounded(self):

        a1 = ledger.Amount("2.00 ZXC")
        a1.keep_precision = True
        a2 = a1 / 3

        self.assertEqual("2.00 ZXC", str(a1))
        self.assertEqual("0.66666667 ZXC", str(a2))
        self.assertEqual("0.67 ZXC", str(a2.rounded()))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2.rounded())))

    def test_amount_in_place_round(self):

        a1 = ledger.Amount("2.00 ZXC")
        a1.keep_precision = True

        a1 = a1 / 3
        
        self.assertEqual("0.66666667 ZXC", str(a1))
        a1.in_place_round()
        self.assertEqual("0.67 ZXC", str(a1))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a1)))

    def test_amount_truncated(self):

        a1 = ledger.Amount("2.00 ZXC")
        a2 = a1 / 3

        self.assertEqual("2.00 ZXC", str(a1))
        self.assertEqual("0.67 ZXC", str(a2))
        self.assertEqual("0.67 ZXC", str(a2.truncated()))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2.truncated())))

    def test_amount_in_place_truncate(self):

        a1 = ledger.Amount("2.00 ZXC")
        a1 = a1 / 3
        
        a1.in_place_truncate()
        self.assertEqual("0.67 ZXC", str(a1))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a1)))

    def test_amount_floored(self):

        a1 = ledger.Amount("2.00 ZXD")
        a2 = a1 / 3

        self.assertEqual("2.00 ZXD", str(a1))
        self.assertEqual("0.67 ZXD", str(a2))
        self.assertEqual("0.00 ZXD", str(a2.floored()))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2.floored())))

    def test_amount_in_place_floor(self):

        a1 = ledger.Amount("2.00 ZXD")
        a1 = a1 / 3
        
        a1.in_place_floor()
        self.assertEqual("0.00 ZXD", str(a1))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a1)))

    def test_amount_unrounded(self):

        a1 = ledger.Amount("2.00 ZXD")
        a2 = a1 / 3

        self.assertEqual("2.00 ZXD", str(a1))
        self.assertEqual("0.67 ZXD", str(a2))
        self.assertEqual("0.66666667 ZXD", str(a2.unrounded()))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2.unrounded())))

    def test_amount_in_place_unround(self):

        a1 = ledger.Amount("2.00 ZXD")
        a1 = a1 / 3
        
        a1.in_place_unround()
        self.assertEqual("0.66666667 ZXD", str(a1))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a1)))

    def test_amount_reduced(self):

        a1 = ledger.Amount("2.00 ZXD")
        a2 = a1 / 3

        self.assertEqual("2.00 ZXD", str(a1))
        self.assertEqual("0.67 ZXD", str(a2))
        self.assertEqual("0.67 ZXD", str(a2.reduced()))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2.reduced())))

    def test_amount_in_place_reduce(self):

        a1 = ledger.Amount("2.00 ZXD")
        a1 = a1 / 3
        
        a1.in_place_reduce()
        self.assertEqual("0.67 ZXD", str(a1))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a1)))

    def test_amount_unreduced(self):

        a1 = ledger.Amount("2.00 ZXD")
        a2 = a1 / 3

        self.assertEqual("2.00 ZXD", str(a1))
        self.assertEqual("0.67 ZXD", str(a2))
        self.assertEqual("0.67 ZXD", str(a2.unreduced()))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a2.unreduced())))

    def test_amount_in_place_unreduce(self):

        a1 = ledger.Amount("2.00 ZXD")
        a1 = a1 / 3
        
        a1.in_place_unreduce()
        self.assertEqual("0.67 ZXD", str(a1))
        self.assertEqual("<class 'ledger.Amount'>", str(type(a1)))

    def test_amount_value(self):

        amnt = ledger.Amount("2.00 ZXR")
        self.assertIsNone(amnt.value())
        self.assertIsInstance(amnt.value(ledger.commodities.find("ZXR")), ledger.Amount)
        self.assertIsInstance(amnt.value(ledger.commodities.find("ZXR"), date.today()), ledger.Amount)
        self.assertIsInstance(amnt.value(ledger.commodities.find("ZXR"), datetime.now()), ledger.Amount)

    def test_amount_price(self):

        amnt = ledger.Amount("2.00 ZXR")
        self.assertIsNone(amnt.price())

        details = ledger.Annotation()
        details.price = ledger.Amount("3.00 ZXR")
        amnt.annotate(details)

        self.assertIsInstance(amnt.price(), ledger.Amount)

    def test_amount_sign(self):

        amnt = ledger.Amount("2.00 ZXR")
        self.assertEqual(1, amnt.sign())

        amnt = ledger.Amount("-2.00 ZXR")
        self.assertEqual(-1, amnt.sign())

        amnt = ledger.Amount("0")
        self.assertEqual(0, amnt.sign())

    def test_amount_is_nonzero(self):

        amnt = ledger.Amount("2.00 ZXR")
        self.assertTrue(amnt.is_nonzero())

        amnt = ledger.Amount("0")
        self.assertFalse(amnt.is_nonzero())

    def test_amount_is_zero(self):

        amnt = ledger.Amount("2.00 ZXR")
        self.assertFalse(amnt.is_zero())

        amnt = ledger.Amount("0")
        self.assertTrue(amnt.is_zero())

    def test_amount_is_realzero(self):

        amnt = ledger.Amount("2.00 ZXR")
        self.assertFalse(amnt.is_realzero())

        amnt = ledger.Amount("0")
        self.assertTrue(amnt.is_realzero())

    def test_amount_is_null(self):

        amnt = ledger.Amount("2.00 ZXR")
        self.assertFalse(amnt.is_null())

        amnt = ledger.Amount(ledger.OriginAmount())
        self.assertTrue(amnt.is_null())

    def test_amount_to_double(self):

        amnt = ledger.Amount("2.00 ZXR")
        dbl = amnt.to_double()
        self.assertIsInstance(dbl, float)
        self.assertEqual(2, dbl)

    def test_amount_float(self):

        amnt = ledger.Amount("2.00 ZXR")
        dbl = float(amnt)
        self.assertIsInstance(dbl, float)
        self.assertEqual(2, dbl)

    def test_amount_to_long(self):

        amnt = ledger.Amount("2.00 ZXR")
        lng = amnt.to_long()
        self.assertIsInstance(lng, int)
        self.assertEqual(2, lng)

    def test_amount_int(self):

        amnt = ledger.Amount("2.00 ZXR")
        lng = int(amnt)
        self.assertIsInstance(lng, int)
        self.assertEqual(2, lng)

    def test_amount_fits_in_long(self):

        self.assertTrue(ledger.Amount("2.00 ZXR").fits_in_long())
        self.assertFalse(ledger.Amount("2.50 ZXR").fits_in_long())

    def test_amount_to_string(self):

        self.assertTrue("2.00 ZXR", ledger.Amount("2.00 ZXR").to_string())

    def test_amount_str(self):

        self.assertTrue("2.00 ZXR", str(ledger.Amount("2.00 ZXR")))

    def test_amount_to_fullstring(self):

        self.assertTrue("2.00 ZXR", ledger.Amount("2.00 ZXR").to_fullstring())

    def test_amount_repr(self):

        self.assertTrue("2.00 ZXR", repr(ledger.Amount("2.00 ZXR")))

    def test_amount_quantity_string(self):

        self.assertTrue("2.00", ledger.Amount("2.00 ZXR").quantity_string())

    def test_amount_commodity(self):

        amnt = ledger.Amount("2.00 ZXD")
        comm = amnt.commodity
        self.assertEqual("ZXD", str(comm))
        self.assertEqual(amnt.commodity, ledger.commodities.find("ZXD"))
        amnt.commodity = None
        self.assertIsNone(amnt.commodity)

    def test_amount_has_commodity(self):

        amnt = ledger.Amount("2.00 ZXD")
        self.assertTrue(amnt.has_commodity())

        amnt = ledger.Amount("2")
        self.assertFalse(amnt.has_commodity())

    def test_amount_with_commodity(self):

        amnt = ledger.Amount("2.00 ZXD")
        self.assertIsInstance(amnt.with_commodity(None), ledger.Amount)
        self.assertIsInstance(amnt.with_commodity(ledger.commodities.find("ZXD")), ledger.Amount)

    def test_amount_clear_commodity(self):

        amnt = ledger.Amount("2.00 ZXD")
        self.assertTrue(amnt.has_commodity())
        amnt.clear_commodity()
        self.assertFalse(amnt.has_commodity())

    def test_amount_number(self):

        amnt = ledger.Amount("2.00 ZXD")
        nmb = amnt.number()
        self.assertIsInstance(nmb, ledger.Amount)
        self.assertEqual(2, nmb)

    def test_amount_annotate(self):

        amnt = ledger.Amount("2.00 ZXD")
        self.assertFalse(amnt.origin.HasAnnotation)
        amnt.annotate(ledger.Annotation())
        self.assertTrue(amnt.origin.HasAnnotation)

    def test_amount_has_annotation(self):

        amnt = ledger.Amount("2.00 ZXD")
        self.assertFalse(amnt.has_annotation())
        amnt.annotate(ledger.Annotation())
        self.assertTrue(amnt.has_annotation())

    def test_amount_annotation(self):

        amnt = ledger.Amount("2.00 ZXD")
        amnt.annotate(ledger.Annotation())
        self.assertIsInstance(amnt.annotation, ledger.Annotation)

    def test_amount_strip_annotations(self):

        amnt = ledger.Amount("2.00 ZXD")
        amnt.annotate(ledger.Annotation())
        amnt = amnt.strip_annotations()
        self.assertFalse(amnt.has_annotation())

        amnt = ledger.Amount("2.00 ZXD")
        annt = ledger.Annotation()
        annt.price = ledger.Amount("3.00 ZXD")
        amnt.annotate(annt)
        keep = ledger.KeepDetails(keepPrice=True)
        amnt = amnt.strip_annotations(keep)
        self.assertTrue(amnt.has_annotation())

    def test_amount_parse(self):

        amnt = ledger.Amount()
        amnt.parse("2.00 ZXD")
        self.assertEqual(2, amnt.number())

        amnt = ledger.Amount()
        amnt.parse("2.00 ZXD", ledger.ParseFlags.NoReduce)
        self.assertEqual(2, amnt.number())

        amnt = ledger.Amount()
        amnt.parse("2.00 ZXD", ledger.ParseFlags.NoReduce | ledger.ParseFlags.Partial)
        self.assertEqual(2, amnt.number())

    def test_amount_parse_conversion(self):

        Amount.parse_conversion("100 FTR", "10 FTY")
        amnt = ledger.Amount("20.00 FTR")
        amnt = amnt.with_commodity(ledger.commodities.find("FTY"))
        self.assertIsInstance(amnt, ledger.Amount)
        self.assertEqual(200, amnt.number())

    def test_amount_valid(self):

        amnt = ledger.Amount("2.00 ZXD")
        self.assertTrue(2, amnt.valid())

class ParseFlagsTests(unittest.TestCase):
    def test_parseflags_members(self):
        self.assertEqual(ledger.ParseFlags.Default, int(ledger.NetEnum.Format(ledger.OriginAmountParseFlagsEnum, ledger.OriginAmountParseFlagsEnum.PARSE_DEFAULT, "d")))
        self.assertEqual(ledger.ParseFlags.Partial, int(ledger.NetEnum.Format(ledger.OriginAmountParseFlagsEnum, ledger.OriginAmountParseFlagsEnum.PARSE_PARTIAL, "d")))
        self.assertEqual(ledger.ParseFlags.Single, int(ledger.NetEnum.Format(ledger.OriginAmountParseFlagsEnum, ledger.OriginAmountParseFlagsEnum.PARSE_SINGLE, "d")))
        self.assertEqual(ledger.ParseFlags.NoMigrate, int(ledger.NetEnum.Format(ledger.OriginAmountParseFlagsEnum, ledger.OriginAmountParseFlagsEnum.PARSE_NO_MIGRATE, "d")))
        self.assertEqual(ledger.ParseFlags.NoReduce, int(ledger.NetEnum.Format(ledger.OriginAmountParseFlagsEnum, ledger.OriginAmountParseFlagsEnum.PARSE_NO_REDUCE, "d")))
        self.assertEqual(ledger.ParseFlags.NoAssign, int(ledger.NetEnum.Format(ledger.OriginAmountParseFlagsEnum, ledger.OriginAmountParseFlagsEnum.PARSE_NO_ASSIGN, "d")))
        self.assertEqual(ledger.ParseFlags.OpContext, int(ledger.NetEnum.Format(ledger.OriginAmountParseFlagsEnum, ledger.OriginAmountParseFlagsEnum.PARSE_OP_CONTEXT, "d")))
        self.assertEqual(ledger.ParseFlags.SoftFail, int(ledger.NetEnum.Format(ledger.OriginAmountParseFlagsEnum, ledger.OriginAmountParseFlagsEnum.PARSE_SOFT_FAIL, "d")))

class BalanceTests(unittest.TestCase):

    def test_balance_constructor(self):
        bal = ledger.Balance()
        self.assertIsInstance(bal, ledger.Balance)

        bal = ledger.Balance(ledger.OriginBalance())
        self.assertIsInstance(bal, ledger.Balance)

        bal = ledger.Balance(ledger.Amount(10))
        self.assertIsInstance(bal, ledger.Balance)

        bal = ledger.Balance(ledger.Balance())
        self.assertIsInstance(bal, ledger.Balance)

        bal = ledger.Balance("0")
        self.assertIsInstance(bal, ledger.Balance)

        bal = ledger.Balance(0)
        self.assertIsInstance(bal, ledger.Balance)

        bal = ledger.Balance(0.0)
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_from_origin(self):
        bal = ledger.Balance.from_origin(ledger.OriginBalance())
        self.assertIsInstance(bal, ledger.Balance)

        bal = ledger.Balance.from_origin(None)
        self.assertIsNone(bal)

    def test_balance_add(self):
        bal = ledger.Balance(10)

        bal = bal + ledger.Balance(20)
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal + ledger.Amount(10)
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal + 10
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal + 10.0
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_iadd(self):
        bal = ledger.Balance(10)

        bal += ledger.Balance(20)
        self.assertIsInstance(bal, ledger.Balance)

        bal += ledger.Amount(10)
        self.assertIsInstance(bal, ledger.Balance)

        bal += 10
        self.assertIsInstance(bal, ledger.Balance)

        bal += 10.0
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_sub(self):
        bal = ledger.Balance(10)

        bal = bal - ledger.Balance(20)
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal - ledger.Amount(10)
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal - 10
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal - 10.0
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_isub(self):
        bal = ledger.Balance(10)

        bal -= ledger.Balance(20)
        self.assertIsInstance(bal, ledger.Balance)

        bal -= ledger.Amount(10)
        self.assertIsInstance(bal, ledger.Balance)

        bal -= 10
        self.assertIsInstance(bal, ledger.Balance)

        bal -= 10.0
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_mul(self):
        bal = ledger.Balance(10)

        bal = bal * ledger.Amount(10)
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal * 10
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal * 10.0
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_imul(self):
        bal = ledger.Balance(10)

        bal *= ledger.Amount(10)
        self.assertIsInstance(bal, ledger.Balance)

        bal *= 10
        self.assertIsInstance(bal, ledger.Balance)

        bal *= 10.0
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_div(self):
        bal = ledger.Balance(10)

        bal = bal / ledger.Amount(10)
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal / 10
        self.assertIsInstance(bal, ledger.Balance)

        bal = bal / 10.0
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_idiv(self):
        bal = ledger.Balance(10)

        bal /= ledger.Amount(10)
        self.assertIsInstance(bal, ledger.Balance)

        bal /= 10
        self.assertIsInstance(bal, ledger.Balance)

        bal /= 10.0
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_neg(self):
        bal = ledger.Balance(10)

        bal = -bal
        self.assertIsInstance(bal, ledger.Balance)

    def test_balance_eq(self):
        bal = ledger.Balance(10)

        self.assertTrue(bal == ledger.Balance(10))
        self.assertTrue(bal == ledger.Amount(10))
        self.assertTrue(bal == 10)

    def test_balance_ne(self):
        bal = ledger.Balance(10)

        self.assertFalse(bal != ledger.Balance(10))
        self.assertFalse(bal != ledger.Amount(10))
        self.assertFalse(bal != 10)

    def test_balance_bool(self):
        bal = ledger.Balance(10)
        self.assertTrue(bool(bal))
        self.assertTrue(bal)
        self.assertFalse(not bal)

    def test_balance_to_string(self):
        bal = ledger.Balance(10)
        self.assertEqual("10", bal.to_string())

    def test_balance_str(self):
        bal = ledger.Balance(10)
        self.assertEqual("10", str(bal))

    def test_balance_negated(self):
        bal = ledger.Balance(10)
        bal1 = bal.negated()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("-10", str(bal1))
        self.assertEqual("10", str(bal))

    def test_balance_in_place_negate(self):
        bal = ledger.Balance(10)
        bal.in_place_negate()
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("-10", str(bal))

    def test_balance_len(self):
        bal = ledger.Balance(-10)
        self.assertEqual(1, len(bal))

    def test_balance_getitem(self):
        bal = ledger.Balance(10)
        amt = bal[0]
        self.assertIsInstance(amt, ledger.Amount)
        self.assertEqual(10, amt)

    def test_balance_iter(self):
        bal = ledger.Balance(10)
        for amt in bal:            
            self.assertIsInstance(amt, ledger.Amount)
            self.assertEqual(10, amt)

    def test_balance_abs(self):
        bal = ledger.Balance(-10)
        bal1 = bal.abs()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("-10", str(bal))
        self.assertEqual("10", str(bal1))
        self.assertEqual("10", str(abs(bal)))

    def test_balance_rounded(self):
        bal = ledger.Balance(10.7)
        bal1 = bal.rounded()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("11", str(bal1))
        self.assertEqual("11", str(bal))

    def test_balance_in_place_round(self):
        bal = ledger.Balance(10.7)
        bal.in_place_round()
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("11", str(bal))

    def test_balance_truncated(self):
        bal = ledger.Balance(10.7)
        bal1 = bal.truncated()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("11", str(bal1))
        self.assertEqual("11", str(bal))

    def test_balance_in_place_truncate(self):
        bal = ledger.Balance(10.7)
        bal.in_place_truncate()
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("11", str(bal))

    def test_balance_floored(self):
        bal = ledger.Balance(10.7)
        bal1 = bal.floored()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("10", str(bal1))
        self.assertEqual("11", str(bal))

    def test_balance_in_place_floor(self):
        bal = ledger.Balance(10.7)
        bal.in_place_floor()
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("10", str(bal))

    def test_balance_unrounded(self):
        bal = ledger.Balance(10.7)
        bal1 = bal.unrounded()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("11", str(bal1))
        self.assertEqual("11", str(bal))

    def test_balance_in_place_unround(self):
        bal = ledger.Balance(10.7)
        bal.in_place_unround()
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("11", str(bal))

    def test_balance_reduced(self):
        bal = ledger.Balance(10.7)
        bal1 = bal.reduced()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("11", str(bal1))
        self.assertEqual("11", str(bal))

    def test_balance_in_place_reduce(self):
        bal = ledger.Balance(10.7)
        bal.in_place_reduce()
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("11", str(bal))

    def test_balance_unreduced(self):
        bal = ledger.Balance(10.7)
        bal1 = bal.unreduced()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("11", str(bal1))
        self.assertEqual("11", str(bal))

    def test_balance_in_place_unreduce(self):
        bal = ledger.Balance(10.7)
        bal.in_place_unreduce()
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("11", str(bal))

    def test_balance_value(self):
        amnt1 = ledger.Amount("2.00 BLT1")
        amnt1.commodity.add_flags(ledger.COMMODITY_PRIMARY)

        bal = ledger.Balance()
        bal += amnt1

        val = bal.value()
        self.assertIsNone(val)

        val = bal.value(amnt1.commodity)
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("2.00 BLT", str(bal))

        val = bal.value(amnt1.commodity, date.today())
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("2.00 BLT", str(bal))

        val = bal.value(amnt1.commodity, datetime.today())
        self.assertIsInstance(bal, ledger.Balance)
        self.assertEqual("2.00 BLT", str(bal))

    def test_balance_is_nonzero(self):
        bal = ledger.Balance(10)
        self.assertTrue(bal.is_nonzero())

        bal = ledger.Balance()
        self.assertFalse(bal.is_nonzero())

    def test_balance_is_zero(self):
        bal = ledger.Balance(10)
        self.assertFalse(bal.is_zero())

        bal = ledger.Balance()
        self.assertTrue(bal.is_zero())

    def test_balance_is_realzero(self):
        bal = ledger.Balance(10)
        self.assertFalse(bal.is_realzero())

        bal = ledger.Balance()
        self.assertTrue(bal.is_realzero())

    def test_balance_is_empty(self):
        bal = ledger.Balance(10)
        self.assertFalse(bal.is_empty())

        bal = ledger.Balance()
        self.assertTrue(bal.is_empty())

    def test_balance_single_amount(self):
        bal = ledger.Balance(10)
        self.assertIsInstance(bal.single_amount(), ledger.Amount)
        self.assertEqual(10, bal.single_amount())

    def test_balance_to_amount(self):
        bal = ledger.Balance(10)
        self.assertIsInstance(bal.to_amount(), ledger.Amount)
        self.assertEqual(10, bal.to_amount())

    def test_balance_commodity_count(self):
        bal = ledger.Balance()
        self.assertEqual(0, bal.commodity_count())

        bal += ledger.Amount("2 BLT1")
        self.assertEqual(1, bal.commodity_count())

    def test_balance_commodity_amount(self):
        amnt = ledger.Amount("2 BLT1")
        bal = ledger.Balance(amnt)
        self.assertIsInstance(bal.commodity_amount(), ledger.Amount)
        self.assertIsInstance(bal.commodity_amount(amnt.commodity), ledger.Amount)

    def test_balance_number(self):
        amnt = ledger.Amount("2 BLT1")
        bal = ledger.Balance(amnt)
        bal1 = bal.number()
        self.assertIsInstance(bal1, ledger.Balance)
        self.assertEqual("2", str(bal1))

    def test_balance_strip_annotations(self):
        amnt = ledger.Amount("2 BLT1")
        bal = ledger.Balance(amnt)
        self.assertIsInstance(bal.strip_annotations(), ledger.Balance)
        self.assertIsInstance(bal.strip_annotations(ledger.KeepDetails(keepPrice=True)), ledger.Balance)

    def test_balance_strip_valid(self):
        bal = ledger.Balance()
        self.assertTrue(bal.valid())

class PositionTests(unittest.TestCase):

    def test_position_constructor_allows_no_arguments(self):

        pos = ledger.Position()
        self.assertTrue(isinstance(pos,ledger.Position))
        self.assertEqual(None, pos.pathname)
        self.assertEqual(0, pos.beg_pos)
        self.assertEqual(0, pos.beg_line)
        self.assertEqual(0, pos.end_pos)
        self.assertEqual(0, pos.end_line)

    def test_position_constructor_takes_origin(self):

        pos = ledger.Position(ledger.OriginItemPosition())
        self.assertTrue(isinstance(pos,ledger.Position))
        self.assertEqual(None, pos.pathname)
        self.assertEqual(0, pos.beg_pos)
        self.assertEqual(0, pos.beg_line)
        self.assertEqual(0, pos.end_pos)
        self.assertEqual(0, pos.end_line)

    def test_position_pathname(self):

        pos = ledger.Position()
        pos.pathname = "some-name"
        self.assertEqual("some-name", pos.pathname)
        pos.pathname = None
        self.assertEqual(None, pos.pathname)

    def test_position_beg_pos(self):

        pos = ledger.Position()
        pos.beg_pos = 10
        self.assertEqual(10, pos.beg_pos)
        pos.beg_pos = 0
        self.assertEqual(0, pos.beg_pos)

    def test_position_beg_line(self):

        pos = ledger.Position()
        pos.beg_line = 10
        self.assertEqual(10, pos.beg_line)
        pos.beg_line = 0
        self.assertEqual(0, pos.beg_line)

    def test_position_end_pos(self):

        pos = ledger.Position()
        pos.end_pos = 10
        self.assertEqual(10, pos.end_pos)
        pos.end_pos = 0
        self.assertEqual(0, pos.end_pos)

    def test_position_end_line(self):

        pos = ledger.Position()
        pos.end_line = 10
        self.assertEqual(10, pos.end_line)
        pos.end_line = 0
        self.assertEqual(0, pos.end_line)

class StateTests(unittest.TestCase):
    def test_parseflags_members(self):
        self.assertEqual(ledger.State.Uncleared.value, int(ledger.NetEnum.Format(ledger.OriginItemStateEnum, ledger.OriginItemStateEnum.Uncleared, "d")))
        self.assertEqual(ledger.State.Cleared.value, int(ledger.NetEnum.Format(ledger.OriginItemStateEnum, ledger.OriginItemStateEnum.Cleared, "d")))
        self.assertEqual(ledger.State.Pending.value, int(ledger.NetEnum.Format(ledger.OriginItemStateEnum, ledger.OriginItemStateEnum.Pending, "d")))

class JournalItemTests(unittest.TestCase):

    def test_journalitem_flags(self):

        item = ledger.JournalItem(ledger.OriginPost())

        item.flags = ledger.ITEM_GENERATED
        self.assertEqual(ledger.ITEM_GENERATED, item.flags)
        item.flags = ledger.ITEM_TEMP
        self.assertEqual(ledger.ITEM_TEMP, item.flags)

    def test_journalitem_has_flags(self):

        item = ledger.JournalItem(ledger.OriginPost())

        item.flags = ledger.ITEM_GENERATED | ledger.ITEM_TEMP
        self.assertTrue(item.has_flags(ledger.ITEM_GENERATED))
        self.assertTrue(item.has_flags(ledger.ITEM_TEMP))
        self.assertTrue(item.has_flags(ledger.ITEM_TEMP | ledger.ITEM_GENERATED))

        item.flags = ledger.ITEM_GENERATED
        self.assertTrue(item.has_flags(ledger.ITEM_GENERATED))
        self.assertFalse(item.has_flags(ledger.ITEM_TEMP))

    def test_journalitem_clear_flags(self):

        item = ledger.JournalItem(ledger.OriginPost())
        item.flags = ledger.ITEM_GENERATED | ledger.ITEM_TEMP

        item.clear_flags()
        self.assertTrue(item.flags == 0)

    def test_journalitem_add_flags(self):

        item = ledger.JournalItem(ledger.OriginPost())

        item.flags = ledger.ITEM_GENERATED
        item.add_flags(ledger.ITEM_TEMP)
        self.assertTrue(item.has_flags(ledger.ITEM_GENERATED | ledger.ITEM_TEMP))

    def test_journalitem_drop_flags(self):

        item = ledger.JournalItem(ledger.OriginPost())

        item.flags = ledger.ITEM_GENERATED | ledger.ITEM_TEMP
        item.drop_flags(ledger.ITEM_GENERATED)
        self.assertFalse(item.has_flags(ledger.ITEM_GENERATED))
        self.assertTrue(item.has_flags(ledger.ITEM_TEMP))

    def test_journalitem_description(self):

        item = ledger.JournalItem(ledger.OriginPost())
        self.assertEqual("generated posting", item.description)

    def test_journalitem_type_context(self):

        item = ledger.JournalItem(ledger.OriginPost())
        self.assertEqual(ledger.ValueType.Void, item.type_context)

    def test_journalitem_type_required(self):

        item = ledger.JournalItem(ledger.OriginPost())
        self.assertEqual(False, item.type_required)

    def test_journalitem_note(self):

        item = ledger.JournalItem(ledger.OriginPost())
        item.note = "note-1"
        self.assertEqual("note-1", item.note)
        item.note = None
        self.assertEqual(None, item.note)

    def test_journalitem_pos(self):

        item = ledger.JournalItem(ledger.OriginPost())
        self.assertTrue(isinstance(item.pos, Position))

        pos = ledger.Position()
        pos.end_line = 10

        item.pos = pos
        self.assertEqual(10, item.pos.end_line)
        self.assertTrue(isinstance(item.pos, Position))

        item.pos.end_line = 20
        self.assertEqual(20, item.pos.end_line)

    def test_journalitem_metadata(self):

        item = ledger.JournalItem(ledger.OriginPost())
        self.assertEqual(0, len(item.metadata))

        item.set_tag("tag-1")
        self.assertEqual(1, len(item.metadata))
        self.assertTrue("tag-1" in item.metadata)
        self.assertFalse(bool(item.metadata["tag-1"][0])) # Empty value
        self.assertFalse(item.metadata["tag-1"][1])

        val = ledger.string_value("some_value")
        item.set_tag("tag-2", val)
        self.assertEqual(2, len(item.metadata))
        self.assertTrue("tag-2" in item.metadata)
        self.assertEqual(val, item.metadata["tag-2"][0])
        self.assertFalse(item.metadata["tag-2"][1])

    def test_journalitem_copy_details(self):

        item1 = ledger.JournalItem(ledger.OriginPost())
        item1.note = "note-1"

        item2 = ledger.JournalItem(ledger.OriginPost())
        item2.copy_details(item1)
        self.assertEqual("note-1", item2.note)

    def test_journalitem_eq_ne(self):

        item1 = ledger.JournalItem(ledger.OriginPost())
        item2 = ledger.JournalItem(ledger.OriginPost())
        self.assertTrue(item1 == item1)
        self.assertFalse(item1 == item2)
        self.assertFalse(item1 != item1)
        self.assertTrue(item1 != item2)

    def test_journalitem_has_tag(self):

        item = ledger.JournalItem(ledger.OriginPost())
        item.set_tag("tag-1")

        self.assertTrue(item.has_tag("tag-1"))
        self.assertFalse(item.has_tag("tag-2"))

        self.assertTrue(item.has_tag(ledger.Mask("tag-1")))
        self.assertFalse(item.has_tag(ledger.Mask("tag-2")))

        item.set_tag("tag-2", ledger.string_value("some-value"))
        self.assertFalse(item.has_tag(ledger.Mask("tag-1"), ledger.Mask("some-value")))
        self.assertTrue(item.has_tag(ledger.Mask("tag-2"), ledger.Mask("some-value")))
        self.assertFalse(item.has_tag(ledger.Mask("tag-2"), ledger.Mask("unknown-value")))

    def test_journalitem_get_tag(self):

        item = ledger.JournalItem(ledger.OriginPost())

        item.set_tag("tag-1")
        self.assertFalse(bool(item.get_tag("tag-1")))

        item.set_tag("tag-2", ledger.string_value("some-value"))
        self.assertEqual("some-value", str(item.get_tag("tag-2")))
        self.assertEqual("some-value", str(item.get_tag(ledger.Mask("tag-2"))))
        self.assertEqual("some-value", str(item.get_tag(ledger.Mask("tag-2"), ledger.Mask("some-value"))))
        self.assertFalse(bool(item.get_tag(ledger.Mask("tag-2"), ledger.Mask("unknown-value"))))

    def test_journalitem_tag(self):

        item = ledger.JournalItem(ledger.OriginPost())

        item.set_tag("tag-1")
        self.assertFalse(bool(item.tag("tag-1")))

        item.set_tag("tag-2", ledger.string_value("some-value"))
        self.assertEqual("some-value", str(item.tag("tag-2")))
        self.assertEqual("some-value", str(item.tag(ledger.Mask("tag-2"))))
        self.assertEqual("some-value", str(item.tag(ledger.Mask("tag-2"), ledger.Mask("some-value"))))
        self.assertFalse(bool(item.tag(ledger.Mask("tag-2"), ledger.Mask("unknown-value"))))

    def test_journalitem_set_tag(self):

        item = ledger.JournalItem(ledger.OriginPost())

        item.set_tag("tag-1")
        self.assertTrue(item.has_tag("tag-1"))

        item.set_tag("tag-2", ledger.string_value("first-value"))
        self.assertEqual("first-value", str(item.tag("tag-2")))

        item.set_tag("tag-2", ledger.string_value("second-value"), True)
        self.assertEqual("second-value", str(item.tag("tag-2")))

    def test_journalitem_parse_tags(self):

        item = ledger.JournalItem(ledger.OriginPost())
        scope = ledger.JournalItem(ledger.OriginPost())

        item.parse_tags("; Happy: Valley", scope)
        self.assertEqual("Valley", str(item.tag("Happy")))

        item.parse_tags("; Happy: More", scope, True)
        self.assertEqual("More", str(item.tag("Happy")))

    def test_journalitem_append_note(self):

        item = ledger.JournalItem(ledger.OriginPost())
        scope = ledger.JournalItem(ledger.OriginPost())

        item.append_note("; Happy: Valley", scope)
        self.assertEqual("Valley", str(item.tag("Happy")))

        item.append_note("; Happy: More", scope, True)
        self.assertEqual("More", str(item.tag("Happy")))

    def test_journalitem_use_aux_date(self):

        orig_value = ledger.JournalItem.use_aux_date

        ledger.JournalItem.use_aux_date = False
        self.assertFalse(ledger.JournalItem.use_aux_date)

        ledger.JournalItem.use_aux_date = True
        self.assertTrue(ledger.JournalItem.use_aux_date)

        item = ledger.JournalItem(ledger.OriginPost())

        item.use_aux_date = False
        self.assertFalse(item.use_aux_date)

        item.use_aux_date = True
        self.assertTrue(item.use_aux_date)

        ledger.JournalItem.use_aux_date = orig_value

    def test_journalitem_date(self):

        item = ledger.JournalItem(ledger.OriginPost())
        dt = date(2021, 5, 12)

        item.date = dt
        self.assertEqual(dt, item.date)

    def test_journalitem_aux_date(self):

        item = ledger.JournalItem(ledger.OriginPost())
        dt = date(2021, 5, 15)

        item.aux_date = dt
        self.assertEqual(dt, item.aux_date)

    def test_journalitem_state(self):

        item = ledger.JournalItem(ledger.OriginPost())

        item.state = ledger.State.Uncleared
        self.assertEqual(ledger.State.Uncleared, item.state)

        item.state = ledger.State.Cleared
        self.assertEqual(ledger.State.Cleared, item.state)

        item.state = ledger.State.Pending
        self.assertEqual(ledger.State.Pending, item.state)

    def test_journalitem_lookup(self):

        item = ledger.JournalItem(ledger.OriginPost())
        self.assertIsNone(item.lookup(ledger.SymbolKind.FUNCTION, "unknown"))

    def test_journalitem_valid(self):

        item = ledger.JournalItem(ledger.OriginPost())
        self.assertFalse(item.valid())

# Sessions

class SessionTests(unittest.TestCase):

    def test_session_constructor(self):
        ssn = ledger.Session(ledger.ExtendedSession.Current)
        self.assertIsInstance(ssn, ledger.Session)

    def test_session_from_origin(self):
        ssn = ledger.Session.from_origin(ledger.ExtendedSession.Current)
        self.assertIsInstance(ssn, ledger.Session)

        ssn = ledger.Session.from_origin(None)
        self.assertIsNone(ssn)

    def test_session_read_journal(self):
        ledger.session.close_journal_files()
        filename = get_drewr3_dat_filename()

        jrn = ledger.session.read_journal(filename)
        self.assertIsInstance(jrn, ledger.Journal)

    def test_session_read_journal_from_string(self):
        data = """
        
2010/12/01 * Checking balance
  Assets:Checking                   $1,000.00
  Equity:Opening Balances
        
        """
        jrn = ledger.session.read_journal_from_string(data)
        self.assertIsInstance(jrn, ledger.Journal)

    def test_session_read_journal_files(self):
        ledger.session.close_journal_files()

        jrn = ledger.session.read_journal_files()
        self.assertIsInstance(jrn, ledger.Journal)

    def test_session_close_journal_files(self):
        filename = get_drewr3_dat_filename()
        ledger.session.close_journal_files()

        jrn = ledger.session.read_journal(filename)
        self.assertIsInstance(jrn, ledger.Journal)

        # It is essential to close journal before reading a new file
        ledger.session.close_journal_files()

        jrn = ledger.session.read_journal(filename)
        self.assertIsInstance(jrn, ledger.Journal)

    def test_session_journal(self):
        jrn = ledger.session.journal()
        self.assertIsInstance(jrn, ledger.Journal)

# Journals

class FileInfoTests(unittest.TestCase):

    def test_fileinfo_constructor(self):
        fileinfo = ledger.FileInfo()
        self.assertIsInstance(fileinfo, ledger.FileInfo)

        fileinfo = ledger.FileInfo(ledger.OriginJournalFileInfo())
        self.assertIsInstance(fileinfo, ledger.FileInfo)

        fileinfo = ledger.FileInfo(get_drewr3_dat_filename())
        self.assertIsInstance(fileinfo, ledger.FileInfo)

    def test_fileinfo_from_origin(self):
        fileinfo = ledger.FileInfo.from_origin(ledger.OriginJournalFileInfo())
        self.assertIsInstance(fileinfo, ledger.FileInfo)

        fileinfo = ledger.FileInfo.from_origin(None)
        self.assertIsNone(fileinfo)

    def test_fileinfo_filename(self):
        fileinfo = ledger.FileInfo()
        self.assertIsNone(fileinfo.filename)

        filename = get_drewr3_dat_filename()
        fileinfo = ledger.FileInfo(filename)
        self.assertEqual(filename, fileinfo.filename)

    def test_fileinfo_size(self):
        fileinfo = ledger.FileInfo()
        self.assertEqual(0, fileinfo.size)

        filename = get_drewr3_dat_filename()
        fileinfo = ledger.FileInfo(filename)
        self.assertNotEqual(0, fileinfo.size)

    def test_fileinfo_modtime(self):
        fileinfo = ledger.FileInfo()
        self.assertEqual(fileinfo.modtime, datetime(1, 1, 1, 0, 0))

        filename = get_drewr3_dat_filename()
        fileinfo = ledger.FileInfo(filename)
        self.assertIsInstance(fileinfo.modtime, datetime)

    def test_fileinfo_from_stream(self):
        fileinfo = ledger.FileInfo()
        self.assertTrue(fileinfo.from_stream)

        filename = get_drewr3_dat_filename()
        fileinfo = ledger.FileInfo(filename)
        self.assertFalse(fileinfo.from_stream)

class JournalTests(unittest.TestCase):

    def test_journal_constructor(self):
        jrn = ledger.Journal()
        self.assertIsInstance(jrn, ledger.Journal)

        jrn = ledger.Journal(ledger.OriginJournal())
        self.assertIsInstance(jrn, ledger.Journal)

    def test_journal_from_origin(self):
        jrn = ledger.Journal.from_origin(ledger.OriginJournal())
        self.assertIsInstance(jrn, ledger.Journal)

        jrn = ledger.Journal.from_origin(None)
        self.assertIsNone(jrn)

    def test_journal_master(self):
        jrn = ledger.Journal()
        self.assertIsInstance(jrn.master, ledger.Account)
        jrn.master = ledger.Account(None, "accntname")
        self.assertIsInstance(jrn.master, ledger.Account)
        self.assertEqual(jrn.master.name, "accntname")

    def test_journal_bucket(self):
        jrn = ledger.Journal()
        self.assertIsNone(jrn.bucket)
        jrn.bucket = ledger.Account(None, "accntname")
        self.assertIsInstance(jrn.bucket, ledger.Account)
        self.assertEqual(jrn.bucket.name, "accntname")

    def test_journal_add_account(self):
        acc = ledger.Account(None, "accntname")
        jrn = ledger.Journal()
        jrn.add_account(acc)
        self.assertEqual(jrn.find_account(acc.name).name, "accntname")

    def test_journal_remove_account(self):
        acc = ledger.Account(None, "accntname")
        jrn = ledger.Journal()
        jrn.add_account(acc)
        self.assertTrue(jrn.remove_account(acc))
        self.assertFalse(jrn.remove_account(acc))
        self.assertIsNone(jrn.find_account("accntname", False))

    def test_journal_find_account(self):
        jrn = ledger.Journal()
        self.assertIsInstance(jrn.find_account("accnt1"), ledger.Account)   # auto-creation
        jrn.add_account(ledger.Account(None, "accnt2"))
        self.assertIsInstance(jrn.find_account("accnt2", False), ledger.Account) 
        self.assertIsInstance(jrn.find_account("accnt2", True), ledger.Account)
        self.assertIsNone(jrn.find_account("accnt3", False), ledger.Account) # no auto-creation

    def test_journal_find_account_re(self):
        jrn = ledger.Journal()
        jrn.add_account(ledger.Account(None, "accntname"))
        self.assertIsInstance(jrn.find_account_re("accntname"), ledger.Account)
        self.assertIsNone(jrn.find_account_re("unknown"))

    def test_journal_register_account(self):
        jrn = ledger.Journal()

        acc = jrn.register_account("acc1", None)
        self.assertIsInstance(acc, ledger.Account)

        acc = jrn.register_account("acc1", ledger.Posting())
        self.assertIsInstance(acc, ledger.Account)

    def test_journal_expand_aliases(self):
        acc = ledger.Account(None, "accntname")
        jrn = ledger.Journal()        
        jrn.add_account(acc)

        jrn.origin.NoAliases = False
        jrn.origin.AccountAliases.Add("alias1", acc.origin)

        acc = jrn.expand_aliases("alias1")
        self.assertIsInstance(acc, ledger.Account)

    def test_journal_add_xact(self):
        jrn = ledger.Journal()
        self.assertEqual(0, len(jrn.xacts()))

        xact = ledger.Transaction();

        post = ledger.Posting()
        post.amount = ledger.Amount("22 JAX")
        post.account = jrn.find_account("source")
        xact.add_post(post)

        post = ledger.Posting()
        post.amount = ledger.Amount("-22 JAX")
        post.account = jrn.find_account("destination")
        xact.add_post(post)
        
        self.assertTrue(jrn.add_xact(xact))
        self.assertEqual(1, len(jrn.xacts()))

    def test_journal_remove_xact(self):
        jrn = ledger.Journal()
        xact = ledger.Transaction();

        post = ledger.Posting()
        post.amount = ledger.Amount("22 JAX")
        post.account = jrn.find_account("source")
        xact.add_post(post)

        post = ledger.Posting()
        post.amount = ledger.Amount("-22 JAX")
        post.account = jrn.find_account("destination")
        xact.add_post(post)
        
        self.assertTrue(jrn.add_xact(xact))
        self.assertEqual(1, len(jrn.xacts()))

        self.assertTrue(jrn.remove_xact(xact))
        self.assertFalse(jrn.remove_xact(xact))
        self.assertEqual(0, len(jrn.xacts()))

    def test_journal_len(self):
        jrn = ledger.Journal()

        xact = ledger.Transaction();
        post = ledger.Posting()
        post.amount = ledger.Amount("22 JAX")
        post.account = jrn.find_account("source")
        xact.add_post(post)
        post = ledger.Posting()
        post.amount = ledger.Amount("-22 JAX")
        post.account = jrn.find_account("destination")
        xact.add_post(post)        
        jrn.add_xact(xact)

        self.assertEqual(1, len(jrn))

    def test_journal_getitem(self):
        jrn = ledger.Journal()

        xact = ledger.Transaction();
        post = ledger.Posting()
        post.amount = ledger.Amount("22 JAX")
        post.account = jrn.find_account("source")
        xact.add_post(post)
        post = ledger.Posting()
        post.amount = ledger.Amount("-22 JAX")
        post.account = jrn.find_account("destination")
        xact.add_post(post)        
        jrn.add_xact(xact)

        self.assertIsInstance(jrn[0], ledger.Transaction)

    def test_journal_iter(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        for xact in jrn:
            self.assertIsInstance(xact, ledger.Transaction)

    def test_journal_xacts(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        xacts = jrn.xacts()
        self.assertEqual(11, len(xacts))
        for xact in xacts:
            self.assertIsInstance(xact, ledger.Transaction)

    def test_journal_auto_xacts(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        xacts = jrn.auto_xacts()
        self.assertEqual(1, len(xacts))
        for xact in xacts:
            self.assertIsInstance(xact, ledger.AutomatedTransaction)

    def test_journal_period_xacts(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        xacts = jrn.period_xacts()
        self.assertEqual(0, len(xacts))

    def test_journal_sources(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        src = jrn.sources()
        self.assertEqual(1, len(src))
        for fileInfo in src:
            self.assertIsInstance(fileInfo, ledger.FileInfo)

    def test_journal_has_xdata(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        self.assertFalse(jrn.has_xdata())

    def test_journal_clear_xdata(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        jrn.clear_xdata()
        self.assertFalse(jrn.has_xdata())

    def test_journal_query(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        for post in jrn.query("^expenses:"):
            self.assertIsInstance(post, ledger.Posting)

    def test_journal_valid(self):
        ledger.session.close_journal_files()
        jrn = ledger.session.read_journal(get_drewr3_dat_filename())
        self.assertTrue(jrn.valid())


if __name__ == '__main__':
    unittest.main()
