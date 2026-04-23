import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import DashboardScreen from '../screens/DashboardScreen';
import ChecklistScreen from '../screens/ChecklistScreen';
import ProfileScreen from '../screens/ProfileScreen';
import TrackingScreen from '../screens/TrackingScreen';
import TripsScreen from '../screens/TripsScreen';
import { colors } from '../theme';

const TABS = [
  { key: 'dashboard', label: 'Início' },
  { key: 'trips', label: 'Viagens' },
  { key: 'checklist', label: 'Checklist' },
  { key: 'tracking', label: 'Mapa' },
  { key: 'profile', label: 'Perfil' },
];

export default function AppShell() {
  const [tab, setTab] = useState('dashboard');

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        {tab === 'dashboard' ? <DashboardScreen onOpenTab={setTab} /> : null}
        {tab === 'trips' ? <TripsScreen /> : null}
        {tab === 'checklist' ? <ChecklistScreen /> : null}
        {tab === 'tracking' ? <TrackingScreen /> : null}
        {tab === 'profile' ? <ProfileScreen /> : null}
      </View>

      <View style={styles.tabBar}>
        {TABS.map((item) => {
          const active = item.key === tab;
          return (
            <Pressable key={item.key} style={[styles.tabButton, active && styles.tabButtonActive]} onPress={() => setTab(item.key)}>
              <Text style={[styles.tabLabel, active && styles.tabLabelActive]}>{item.label}</Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
  },
  tabBar: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.surface,
    gap: 8,
  },
  tabButton: {
    flex: 1,
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: 'center',
  },
  tabButtonActive: {
    backgroundColor: colors.primary,
  },
  tabLabel: {
    color: colors.textMuted,
    fontWeight: '700',
    fontSize: 12,
  },
  tabLabelActive: {
    color: colors.primaryDark,
  },
});
