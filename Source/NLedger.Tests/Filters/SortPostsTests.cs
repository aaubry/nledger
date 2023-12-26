﻿// **********************************************************************************
// Copyright (c) 2015-2023, Dmitry Merzlyakov.  All rights reserved.
// Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
// 
// This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
// Copyright (c) 2003-2023, John Wiegley.  All rights reserved.
// See LICENSE.LEDGER file included with the distribution for details and disclaimer.
// **********************************************************************************
using NLedger.Filters;
using NLedger.Scopus;
using NLedger.Utility;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using NLedger.Chain;
using NLedger.Expressions;
using Xunit;

namespace NLedger.Tests.Filters
{
    public class SortPostsTests : TestFixture
    {
        [Fact]
        public void SortPosts_PostAccumulatedPosts_UsesStableSortAlgorithm()
        {
            CollectPosts collectPosts = new CollectPosts();
            SortPosts sortPosts = new SortPosts(collectPosts, "date", new Report());
            sortPosts.Posts.Add(new Post() { Date = new Date(2010, 8, 5), Note = "1" });
            sortPosts.Posts.Add(new Post() { Date = new Date(2010, 5, 5), Note = "2" });
            sortPosts.Posts.Add(new Post() { Date = new Date(2010, 5, 5), Note = "3" });
            sortPosts.Posts.Add(new Post() { Date = new Date(2010, 3, 5), Note = "4" });

            sortPosts.PostAccumulatedPosts();

            Assert.Equal("4", collectPosts.Posts[0].Note);
            Assert.Equal("2", collectPosts.Posts[1].Note);   // Posts with equal key keep original order (2, 3)
            Assert.Equal("3", collectPosts.Posts[2].Note);
            Assert.Equal("1", collectPosts.Posts[3].Note);
        }

        private class TestSortPosts : SortPosts
        {
            public TestSortPosts(PostHandler handler, string sortOrder, Report report) : base(handler, sortOrder, report)
            {  }

            public override void Handle(Post post)
            {
                throw new Exception("Method Handle must not be called");
            }
        }

        [Fact]
        public void SortPosts_PostAccumulatedPosts_CallsBaseHandler()
        {
            CollectPosts collectPosts = new CollectPosts();
            TestSortPosts sortPosts = new TestSortPosts(collectPosts, "date", new Report());
            sortPosts.Posts.Add(new Post() { Date = new Date(2010, 8, 5), Note = "1" });

            sortPosts.PostAccumulatedPosts();  // No exception expected; Handle is not called
        }
    }
}
