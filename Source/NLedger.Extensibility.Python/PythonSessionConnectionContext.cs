﻿// **********************************************************************************
// Copyright (c) 2015-2023, Dmitry Merzlyakov.  All rights reserved.
// Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
// 
// This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
// Copyright (c) 2003-2023, John Wiegley.  All rights reserved.
// See LICENSE.LEDGER file included with the distribution for details and disclaimer.
// **********************************************************************************
using NLedger.Extensibility.Python.Platform;
using Python.Runtime;
using System;
using System.Collections.Generic;
using System.Text;

namespace NLedger.Extensibility.Python
{
    public class PythonSessionConnectionContext : PythonConnectionContext
    {
        public PythonSessionConnectionContext(PythonConnector pythonConnector, PythonSession pythonSession) : base(pythonConnector)
        {
            PythonSession = pythonSession ?? throw new ArgumentNullException(nameof(pythonSession));
        }

        public PythonSession PythonSession { get; }
        public PythonModule MainModule { get; private set; }
        public PyModule LedgerModule { get; private set; }

        public override void OnConnected(bool isPlatformInitialization)
        {
            if (!PythonEngine.IsInitialized)
                throw new InvalidOperationException("assert(Py_IsInitialized());");

            using (PythonSession.GIL())
            {
                MainModule = new PythonModule(PythonSession, "__main__", Py.CreateScope());
                LedgerModule = (PyModule)MainModule.ModuleObject.Import("ledger");

                if (!PythonSession.IsPythonHost && isPlatformInitialization)
                    LedgerModule.Exec("acquire_output_streams()");
            }
        }

        public override void OnDisconnected(bool isPlatformDisposing)
        {
            using (PythonSession.GIL())
            {
                if (!PythonSession.IsPythonHost && isPlatformDisposing)
                    LedgerModule?.Exec("release_output_streams()");

                MainModule.ModuleObject.Dispose();
            }
        }
    }
}
