﻿// **********************************************************************************
// Copyright (c) 2015-2023, Dmitry Merzlyakov.  All rights reserved.
// Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
// 
// This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
// Copyright (c) 2003-2023, John Wiegley.  All rights reserved.
// See LICENSE.LEDGER file included with the distribution for details and disclaimer.
// **********************************************************************************
using NLedger.Amounts;
using NLedger.Expressions;
using NLedger.Times;
using NLedger.Utility;
using NLedger.Values;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xunit;

namespace NLedger.Tests.Expressions
{
    [TestFixtureInit(ContextInit.InitMainApplicationContext | ContextInit.InitTimesCommon)]
    public class ExprTokenTests : TestFixture
    {
        [Fact]
        public void ExprTokenTests_KindToString_VisualizesTokenKinds()
        {
            Assert.Equal("<error token>", ExprToken.KindToString(ExprTokenKind.ERROR));
            Assert.Equal("<value>", ExprToken.KindToString(ExprTokenKind.VALUE));
            Assert.Equal(">=", ExprToken.KindToString(ExprTokenKind.GREATEREQ));
            Assert.Equal("and", ExprToken.KindToString(ExprTokenKind.KW_AND));
            Assert.Equal("<end of input>", ExprToken.KindToString(ExprTokenKind.TOK_EOF));
        }

        [Fact]
        public void ExprTokenTests_TokenToString_VisualizesTokens()
        {
            ExprToken token1 = new ExprToken(ExprTokenKind.VALUE, Value.Get(22));
            Assert.Equal("<value '22'>", ExprToken.TokenToString(token1));

            ExprToken token2 = new ExprToken(ExprTokenKind.IDENT, Value.Get("someid"));
            Assert.Equal("<ident 'someid'>", ExprToken.TokenToString(token2));

            ExprToken token3 = new ExprToken(ExprTokenKind.MASK, Value.Get(new Mask(@"\s")));
            Assert.Equal(@"<mask '\s'>", ExprToken.TokenToString(token3));

            ExprToken token4 = new ExprToken(ExprTokenKind.GREATEREQ, Value.Empty);
            Assert.Equal(">=", ExprToken.TokenToString(token4));
        }

        [Fact]
        public void ExprTokenTests_Clear_ResetsAllProperties()
        {
            ExprToken token = new ExprToken(ExprTokenKind.VALUE, Value.Get(22));
            token.Clear();
            Assert.Equal(ExprTokenKind.UNKNOWN, token.Kind);
            Assert.Equal(0, token.Length);
            Assert.Equal(Value.Empty, token.Value);
            Assert.Equal(String.Empty, token.Symbol);
        }

        [Fact]
        public void ExprTokenTests_ParseReservedWord_DetectsReservedWords()
        {
            String source = "and div else false if or not true anything";
            InputTextStream inStream = new InputTextStream(source);

            ExprToken token = new ExprToken();
            Func<int> act = () => token.ParseReservedWord(inStream);

            ReadAndCheckTokenProps(act, ref token, inStream, 1, ExprTokenKind.KW_AND, 3, Value.Empty, "&");
            ReadAndCheckTokenProps(act, ref token, inStream, 1, ExprTokenKind.KW_DIV, 3, Value.Empty, "/");
            ReadAndCheckTokenProps(act, ref token, inStream, 1, ExprTokenKind.KW_ELSE, 4, Value.Empty, "else");
            ReadAndCheckTokenProps(act, ref token, inStream, 1, ExprTokenKind.VALUE, 5, Value.False, "false");
            ReadAndCheckTokenProps(act, ref token, inStream, 1, ExprTokenKind.KW_IF, 2, Value.Empty, "if");
            ReadAndCheckTokenProps(act, ref token, inStream, 1, ExprTokenKind.KW_OR, 2, Value.Empty, "|");
            ReadAndCheckTokenProps(act, ref token, inStream, 1, ExprTokenKind.EXCLAM, 3, Value.Empty, "!");
            ReadAndCheckTokenProps(act, ref token, inStream, 1, ExprTokenKind.VALUE, 4, Value.True, "true");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.UNKNOWN, 8, Value.Empty, String.Empty);
            ReadAndCheckTokenProps(act, ref token, inStream, -1, ExprTokenKind.UNKNOWN, 0, Value.Empty, String.Empty);
        }

        [Fact]
        public void ExprTokenTests_ParseIdent_DetectsIdentifiers()
        {
            String source = "ident ident1 ident_2";
            InputTextStream inStream = new InputTextStream(source);

            ExprToken token = new ExprToken();
            Func<int> act = () => { token.ParseIdent(inStream); return 0; };

            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.IDENT, 5, Value.Get("ident"), String.Empty);
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.IDENT, 6, Value.Get("ident1"), String.Empty);
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.IDENT, 7, Value.Get("ident_2"), String.Empty);
        }

        [Fact]
        public void ExprTokenTests_Next_DetectsTokensInLine()
        {
            String source = "& && | || ( ) [2015/10/15] 'ASD' \"qwe\" {22} ! != !~ - -> + * ? : /\\\\s/ = =~ == < <= > >= . , ; and my_ident , 23";
            InputTextStream inStream = new InputTextStream(source);

            ExprToken token = new ExprToken();
            Func<int> act = () => { token.Next(inStream, AmountParseFlagsEnum.PARSE_NO_MIGRATE); return 0; };

            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.KW_AND, 1, Value.Empty, "&");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.KW_AND, 2, Value.Empty, "&");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.KW_OR, 1, Value.Empty, "|");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.KW_OR, 2, Value.Empty, "|");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.LPAREN, 1, Value.Empty, "(");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.RPAREN, 1, Value.Empty, ")");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.VALUE, 12, Value.Get(new Date(2015,10,15)), "[");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.VALUE, 5, Value.Get("ASD"), "'");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.VALUE, 5, Value.Get("qwe"), "\"");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.VALUE, 2, Value.Get(new Amount(22)), "{");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.EXCLAM, 1, Value.Empty, "!");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.NEQUAL, 2, Value.Empty, "!=");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.NMATCH, 2, Value.Empty, "!~");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.MINUS, 1, Value.Empty, "-");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.ARROW, 2, Value.Empty, "->");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.PLUS, 1, Value.Empty, "+");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.STAR, 1, Value.Empty, "*");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.QUERY, 1, Value.Empty, "?");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.COLON, 1, Value.Empty, ":");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.VALUE, 5, Value.Get(new Mask("\\s")), "/");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.ASSIGN, 1, Value.Empty, "=");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.MATCH, 2, Value.Empty, "=~");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.EQUAL, 2, Value.Empty, "==");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.LESS, 1, Value.Empty, "<");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.LESSEQ, 2, Value.Empty, "<=");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.GREATER, 1, Value.Empty, ">");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.GREATEREQ, 2, Value.Empty, ">=");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.DOT, 1, Value.Empty, ".");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.COMMA, 1, Value.Empty, ",");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.SEMI, 1, Value.Empty, ";");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.KW_AND, 3, Value.Empty, "&");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.IDENT, 8, Value.Get("my_ident"), "m");
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.COMMA, 1, Value.Empty, ",");  // divider
            ReadAndCheckTokenProps(act, ref token, inStream, 0, ExprTokenKind.VALUE, 2, Value.Get(new Amount("23")), "2");
        }

        [Fact]
        public void ExprToken_ParseIdent_ReturnsEmptyStringValueForEmptyIdent()
        {
            var source = "";
            ExprToken token = new ExprToken();
            token.ParseIdent(new InputTextStream(source));
            Assert.Equal(ValueTypeEnum.String, token.Value.Type);
            Assert.Equal(String.Empty, token.Value.AsString);
        }

        [Fact]
        public void ExprToken_Next_ReturnsEmptyStringValueForEmptyInput()
        {
            var source = "\"\"";
            ExprToken token = new ExprToken();
            token.Next(new InputTextStream(source), AmountParseFlagsEnum.PARSE_DEFAULT);
            Assert.Equal(ValueTypeEnum.String, token.Value.Type);
            Assert.Equal(String.Empty, token.Value.AsString);
        }

        private void ReadAndCheckTokenProps(Func<int> act, ref ExprToken token, InputTextStream inStream, int expectedResult, ExprTokenKind expectedKind, int expectedLength, Value expectedValue, string expectedSymbol)
        {
            inStream.PeekNextNonWS();
            token.Clear();
            int result = act();
            Assert.Equal(expectedResult, result);
            Assert.Equal(expectedKind, token.Kind);
            Assert.Equal(expectedLength, token.Length);
            Assert.True(expectedValue.IsEqualTo(token.Value));
            Assert.Equal(expectedSymbol, token.Symbol);
        }

    }
}
