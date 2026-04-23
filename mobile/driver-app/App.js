import React from 'react';
import { ActivityIndicator, SafeAreaView, StatusBar, StyleSheet, View } from 'react-native';

import { AuthProvider, useAuth } from './src/context/AuthContext';
import HomeScreen from './src/screens/HomeScreen';
import LoginScreen from './src/screens/LoginScreen';

function Root() {
  const { isLoading, token } = useAuth();

  if (isLoading) {
    return (
      <SafeAreaView style={styles.centered}>
        <StatusBar barStyle="light-content" />
        <ActivityIndicator size="large" color="#38bdf8" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <View style={styles.content}>{token ? <HomeScreen /> : <LoginScreen />}</View>
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Root />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
  },
  content: {
    flex: 1,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#020617',
  },
});
