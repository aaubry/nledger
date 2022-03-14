﻿// **********************************************************************************
// Copyright (c) 2015-2022, Dmitry Merzlyakov.  All rights reserved.
// Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
// 
// This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
// Copyright (c) 2003-2022, John Wiegley.  All rights reserved.
// See LICENSE.LEDGER file included with the distribution for details and disclaimer.
// **********************************************************************************
using NLedger.Expressions;
using NLedger.Scopus;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace NLedger.Extensibility.Net
{
    public class NetClassScope : Scope
    {
        public NetClassScope(string className, IValueConverter valueConverter)
            : this (Type.GetType(className), valueConverter)
        { }

        public NetClassScope(Type type, IValueConverter valueConverter)
        {
            ClassType = type ?? throw new ArgumentNullException(nameof(type));
            ValueConverter = valueConverter ?? throw new ArgumentNullException(nameof(valueConverter));
        }

        public IValueConverter ValueConverter { get; }
        public Type ClassType { get; }

        public override string Description => ClassType.FullName;

        public override ExprOp Lookup(SymbolKindEnum kind, string name)
        {
            if (kind == SymbolKindEnum.FUNCTION)
            {
                var methods = ClassType.GetMethods().Where(m => m.Name == name).ToArray();
                if (methods.Any())
                    return ExprOp.WrapFunctor(new MethodFunctor(null, methods, ValueConverter).ExprFunctor);

                var field = ClassType.GetField(name);
                if (field != null)
                    return ExprOp.WrapFunctor(new ValueFunctor(field.GetValue(null), ValueConverter).ExprFunctor);

                var prop = ClassType.GetProperty(name);
                if (prop != null)
                    return ExprOp.WrapFunctor(new ValueFunctor(prop.GetValue(null), ValueConverter).ExprFunctor);
            }
            return null;
        }
    }
}
