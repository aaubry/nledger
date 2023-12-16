﻿// **********************************************************************************
// Copyright (c) 2015-2023, Dmitry Merzlyakov.  All rights reserved.
// Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
// 
// This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
// Copyright (c) 2003-2023, John Wiegley.  All rights reserved.
// See LICENSE.LEDGER file included with the distribution for details and disclaimer.
// **********************************************************************************
using NLedger.Commodities;
using NLedger.Output;
using NLedger.Scopus;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xunit;

namespace NLedger.Tests.Output
{
    public class ReportCommoditiesTests : TestFixture
    {
        [Fact]
        public void ReportCommodities_Flush_ReturnsItemsInAlphabeticalOrder()
        {
            CommodityBase commBase1 = new CommodityBase("comm1");
            Commodity commodity11 = new Commodity(CommodityPool.Current, commBase1) { QualifiedSymbol = "A1" };
            Commodity commodity12 = new Commodity(CommodityPool.Current, commBase1) { QualifiedSymbol = "A2" };
            Commodity commodity13 = new Commodity(CommodityPool.Current, commBase1) { QualifiedSymbol = "A3" };

            Post post1 = new Post() { Amount = new NLedger.Amounts.Amount(1, commodity13) };
            Post post2 = new Post() { Amount = new NLedger.Amounts.Amount(1, commodity11) };
            Post post3 = new Post() { Amount = new NLedger.Amounts.Amount(1, commodity12) };

            Report report = new Report(new Session());
            StringWriter output = new StringWriter();
            report.OutputStream = output;

            ReportCommodities reportCommodities = new ReportCommodities(report);
            reportCommodities.Handle(post1);
            reportCommodities.Handle(post2);
            reportCommodities.Handle(post3);
            reportCommodities.Flush();

            report.OutputStream.Flush();
            Assert.Equal("A1\nA2\nA3\n", report.OutputStream.ToString().RemoveCarriageReturns());
        }
    }
}
