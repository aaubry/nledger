﻿// **********************************************************************************
// Copyright (c) 2015-2022, Dmitry Merzlyakov.  All rights reserved.
// Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
// 
// This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
// Copyright (c) 2003-2022, John Wiegley.  All rights reserved.
// See LICENSE.LEDGER file included with the distribution for details and disclaimer.
// **********************************************************************************
using NLedger.Utility.Rnd;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xunit;

namespace NLedger.Tests.Utility.Rnd
{
    public class IntegerGeneratorTests
    {
        [Fact]
        public void IntegerGenerator_Value_ProvidesMassiveOfIntegersInSpecifiedRange()
        {
            int size = 1000;
            IntegerGenerator intGen = new IntegerGenerator(1, 3);
            
            int[] massive = new int[size];
            for (int i = 0; i < size; i++)
                massive[i] = intGen.Value();
            var usedNumbers = massive.Distinct().OrderBy(i => i).ToList();

            Assert.Equal(1, usedNumbers[0]);
            Assert.Equal(2, usedNumbers[1]);
            Assert.Equal(3, usedNumbers[2]);
        }
    }
}
