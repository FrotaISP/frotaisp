import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

import { canQueueOffline, enqueueOfflineAction, flushOfflineQueue, readQueue } from '../offline/queue';
import { useAuth } from './AuthContext';

const SyncQueueContext = createContext(null);

export function SyncQueueProvider({ children }) {
  const { token } = useAuth();
  const [pendingCount, setPendingCount] = useState(0);
  const [lastSyncMessage, setLastSyncMessage] = useState('');

  useEffect(() => {
    readQueue().then((items) => setPendingCount(items.length));
  }, []);

  useEffect(() => {
    if (!token) {
      return undefined;
    }

    let active = true;

    async function flushNow() {
      try {
        const result = await flushOfflineQueue(token);
        if (!active) {
          return;
        }
        setPendingCount(result.remaining);
        if (result.sent > 0) {
          setLastSyncMessage(`${result.sent} envio(s) offline sincronizados.`);
        } else if (result.remaining > 0) {
          setLastSyncMessage('Ainda existem pendencias salvas aguardando correcao ou nova tentativa.');
        }
      } catch (error) {
        // segue em silencio; a fila continua local
      }
    }

    flushNow();
    const timer = setInterval(flushNow, 30000);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [token]);

  const value = useMemo(() => ({
    pendingCount,
    lastSyncMessage,
    async queueAction(type, payload) {
      const count = await enqueueOfflineAction(type, payload);
      setPendingCount(count);
      setLastSyncMessage('Sem internet no momento. O envio ficou salvo para sincronizar depois.');
      return count;
    },
    canQueueOffline,
  }), [lastSyncMessage, pendingCount]);

  return <SyncQueueContext.Provider value={value}>{children}</SyncQueueContext.Provider>;
}

export function useSyncQueue() {
  const context = useContext(SyncQueueContext);
  if (!context) {
    throw new Error('useSyncQueue deve ser usado dentro de SyncQueueProvider');
  }
  return context;
}
