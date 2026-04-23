import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

import { api } from '../api/client';

const TOKEN_KEY = 'fleetisp_driver_token';
const DRIVER_KEY = 'fleetisp_driver_profile';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [driver, setDriver] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      try {
        const [storedToken, storedDriver] = await Promise.all([
          AsyncStorage.getItem(TOKEN_KEY),
          AsyncStorage.getItem(DRIVER_KEY),
        ]);
        if (storedToken) {
          setToken(storedToken);
        }
        if (storedDriver) {
          setDriver(JSON.parse(storedDriver));
        }
      } finally {
        setIsLoading(false);
      }
    }

    bootstrap();
  }, []);

  const value = useMemo(() => ({
    token,
    driver,
    isLoading,
    async signIn(username, password) {
      const data = await api.login({ username, password });
      setToken(data.token);
      setDriver(data.driver || null);
      await AsyncStorage.multiSet([
        [TOKEN_KEY, data.token],
        [DRIVER_KEY, JSON.stringify(data.driver || null)],
      ]);
      return data;
    },
    async signOut() {
      try {
        if (token) {
          await api.logout(token);
        }
      } catch (error) {
        // Ignora falhas de logout remoto para não travar a saída local.
      } finally {
        setToken(null);
        setDriver(null);
        await AsyncStorage.multiRemove([TOKEN_KEY, DRIVER_KEY]);
      }
    },
    async refreshDriver() {
      if (!token) {
        return null;
      }
      const profile = await api.me(token);
      setDriver(profile);
      await AsyncStorage.setItem(DRIVER_KEY, JSON.stringify(profile));
      return profile;
    },
  }), [driver, isLoading, token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return context;
}
