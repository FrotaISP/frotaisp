import React from 'react';
import { ActivityIndicator, Pressable, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useAuth } from '../context/AuthContext';
import { useDriverDashboard } from '../hooks/useDriverDashboard';
import { colors } from '../theme';
import { Card, EmptyState, ErrorBanner, Screen } from '../components/Common';

export default function DashboardScreen({ onOpenTab }) {
  const { driver, signOut } = useAuth();
  const { dashboard, loading, refreshing, error, refresh } = useDriverDashboard();

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={colors.primary} />}
    >
      <Screen
        title={driver?.name || 'Motorista'}
        subtitle={driver?.company_name || 'FleetISP'}
        right={
          <Pressable style={styles.outlineButton} onPress={signOut}>
            <Text style={styles.outlineButtonText}>Sair</Text>
          </Pressable>
        }
      >
        <ErrorBanner message={error} />

        <Card accent="primary">
          <Text style={styles.eyebrow}>Status de hoje</Text>
          <Text style={styles.metric}>{dashboard?.open_trip ? 'Viagem em andamento' : 'Pronto para sair'}</Text>
          <Text style={styles.helper}>
            {dashboard?.open_trip
              ? `Destino atual: ${dashboard.open_trip.destination}`
              : 'Faça o checklist, inicie a viagem e mantenha a localização atualizada.'}
          </Text>
        </Card>

        <View style={styles.grid}>
          <Pressable style={styles.quickCard} onPress={() => onOpenTab('trips')}>
            <Text style={styles.quickNumber}>{dashboard?.today_trips?.length || 0}</Text>
            <Text style={styles.quickLabel}>Viagens hoje</Text>
          </Pressable>
          <Pressable style={styles.quickCard} onPress={() => onOpenTab('checklist')}>
            <Text style={styles.quickNumber}>{dashboard?.recent_checklists?.length || 0}</Text>
            <Text style={styles.quickLabel}>Checklists</Text>
          </Pressable>
        </View>

        <Card>
          <Text style={styles.cardTitle}>Veículos vinculados</Text>
          {dashboard?.assigned_vehicles?.length ? dashboard.assigned_vehicles.map((vehicle) => (
            <View key={vehicle.id} style={styles.rowBlock}>
              <Text style={styles.rowTitle}>{vehicle.plate} · {vehicle.brand} {vehicle.model}</Text>
              <Text style={styles.rowText}>KM atual: {vehicle.current_odometer}</Text>
              <Text style={styles.rowText}>Rastreamento: {vehicle.tracking_status}</Text>
            </View>
          )) : <EmptyState>Nenhum veículo vinculado no momento.</EmptyState>}
        </Card>

        <Card>
          <Text style={styles.cardTitle}>Alertas de documento</Text>
          {dashboard?.expiring_documents?.length ? dashboard.expiring_documents.map((doc) => (
            <View key={doc.id} style={styles.rowBlock}>
              <Text style={styles.rowTitle}>{doc.title}</Text>
              <Text style={styles.rowText}>Vencimento: {doc.expiration_date}</Text>
              <Text style={styles.rowText}>Dias restantes: {doc.days_until_expiration}</Text>
            </View>
          )) : <EmptyState>Nenhum documento vencendo nos próximos 30 dias.</EmptyState>}
        </Card>
      </Screen>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    paddingBottom: 24,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background,
  },
  outlineButton: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  outlineButtonText: {
    color: colors.text,
    fontWeight: '700',
  },
  eyebrow: {
    color: colors.primary,
    fontWeight: '800',
    textTransform: 'uppercase',
    fontSize: 12,
    letterSpacing: 1,
  },
  metric: {
    color: colors.text,
    fontSize: 24,
    fontWeight: '800',
  },
  helper: {
    color: colors.textMuted,
    lineHeight: 20,
  },
  grid: {
    flexDirection: 'row',
    gap: 12,
  },
  quickCard: {
    flex: 1,
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 20,
    padding: 16,
    gap: 6,
  },
  quickNumber: {
    color: colors.primary,
    fontSize: 26,
    fontWeight: '800',
  },
  quickLabel: {
    color: colors.textMuted,
    fontWeight: '700',
  },
  cardTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: '800',
    marginBottom: 4,
  },
  rowBlock: {
    paddingVertical: 6,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  rowTitle: {
    color: colors.text,
    fontWeight: '700',
    marginBottom: 2,
  },
  rowText: {
    color: colors.textMuted,
  },
});
