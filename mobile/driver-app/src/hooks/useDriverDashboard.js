import { useCallback, useEffect, useState } from 'react';

import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export function useDriverDashboard() {
  const { token, refreshDriver } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const loadDashboard = useCallback(async () => {
    const data = await api.dashboard(token);
    setDashboard(data);
    await refreshDriver();
    return data;
  }, [refreshDriver, token]);

  useEffect(() => {
    async function bootstrap() {
      try {
        setError('');
        await loadDashboard();
      } catch (err) {
        setError(err.message || 'Não foi possível carregar os dados do motorista.');
      } finally {
        setLoading(false);
      }
    }

    if (token) {
      bootstrap();
    }
  }, [loadDashboard, token]);

  const refresh = useCallback(async () => {
    try {
      setRefreshing(true);
      setError('');
      await loadDashboard();
    } catch (err) {
      setError(err.message || 'Não foi possível atualizar os dados.');
    } finally {
      setRefreshing(false);
    }
  }, [loadDashboard]);

  return {
    dashboard,
    loading,
    refreshing,
    error,
    setError,
    reload: loadDashboard,
    refresh,
  };
}
