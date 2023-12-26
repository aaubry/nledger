﻿// **********************************************************************************
// Copyright (c) 2015-2023, Dmitry Merzlyakov.  All rights reserved.
// Licensed under the FreeBSD Public License. See LICENSE file included with the distribution for details and disclaimer.
// 
// This file is part of NLedger that is a .Net port of C++ Ledger tool (ledger-cli.org). Original code is licensed under:
// Copyright (c) 2003-2023, John Wiegley.  All rights reserved.
// See LICENSE.LEDGER file included with the distribution for details and disclaimer.
// **********************************************************************************
using System;
using System.Collections.Generic;
using System.Text;
using System.Linq;

namespace NLedger.Extensibility.Python.Platform
{
    /// <summary>
    /// PythonConnector manages PythonHost and connections objects: it provides Python configuration for PythonHost; 
    /// initializes the host when Python connection was requested; keeps a pool of connection objects and
    /// destroys the host when all connections are released.
    /// </summary>
    public class PythonConnector
    {
        public static PythonConnector Current => _Current.Value;

        public static void Configure(IPythonConfigurationReader pythonConfigurationReader)
        {
            lock(SyncRoot)
            {
                if (_Current.IsValueCreated && Current.HasActiveConnections)
                    throw new InvalidOperationException("Python Connector has active connections");

                _Current = new Lazy<PythonConnector>(() => new PythonConnector(pythonConfigurationReader), true);
            }           
        }

        protected PythonConnector(IPythonConfigurationReader pythonConfigurationReader)
        {
            PythonConfigurationReader = pythonConfigurationReader ?? throw new ArgumentNullException(nameof(pythonConfigurationReader));
        }

        public IPythonConfigurationReader PythonConfigurationReader { get; }
        public PythonHost PythonHost { get; private set; }

        public bool IsAvailable => PythonHost != null || PythonConfigurationReader.IsAvailable;
        public bool HasActiveConnections => Connections.Any();
        public bool KeepAlive { get; set; } = true;

        public PythonConnectionContext Connect() => Connect(connector => new PythonConnectionContext(connector));

        public T Connect<T>(Func<PythonConnector, T> contextFactory) where T: PythonConnectionContext
        {
            if (contextFactory == null)
                throw new ArgumentNullException(nameof(contextFactory));

            lock(SyncRoot)
            {
                bool isPlatformInitialization = PythonHost == null;
                if (isPlatformInitialization)
                    PythonHost = new PythonHost(PythonConfigurationReader.Read());

                var context = contextFactory(this);
                context.OnConnected(isPlatformInitialization);

                Connections.Add(context);
                return context;
            }
        }

        public void Disconnect(PythonConnectionContext pythonConnectionContext)
        {
            lock(SyncRoot)
            {
                if (pythonConnectionContext == null || !Connections.Contains(pythonConnectionContext))
                    return;

                Connections.Remove(pythonConnectionContext);
                var isPlatformDisposing = !HasActiveConnections && !KeepAlive;
                pythonConnectionContext.OnDisconnected(isPlatformDisposing);

                if (isPlatformDisposing)
                {
                    PythonHost.Dispose();
                    PythonHost = null;
                }
            }
        }

        private readonly ISet<PythonConnectionContext> Connections = new HashSet<PythonConnectionContext>();
        private static readonly object SyncRoot = new object();
        private static Lazy<PythonConnector> _Current = new Lazy<PythonConnector>(() => 
            new PythonConnector(
                new EnvPythonConfigurationReader(
                new XmlFilePythonConfigurationReader(appModuleResolver: new LocalResourceAppModuleResolver()))),
            true);
    }
}
