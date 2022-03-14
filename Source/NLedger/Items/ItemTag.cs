﻿// **********************************************************************************
// Copyright (c) 2015-2022, Dmitry Merzlyakov.  All rights reserved.
// Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
// 
// This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
// Copyright (c) 2003-2022, John Wiegley.  All rights reserved.
// See LICENSE.LEDGER file included with the distribution for details and disclaimer.
// **********************************************************************************
using NLedger.Values;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace NLedger.Items
{
    /// <summary>
    /// Parsed from item_t/tag_data_t (item.h)
    /// </summary>
    public struct ItemTag
    {
        public ItemTag(Value value, bool isParsed) : this()
        {
            if (value == null)
                throw new ArgumentNullException("value");

            Value = value;
            IsParsed = isParsed;
        }

        // Pair:first (see item.h - tag_data_t)
        public Value Value { get; set; }

        // Pair:second
        public bool IsParsed { get; set; }
    }
}
