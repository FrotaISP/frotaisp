import React, { useMemo, useState } from 'react';
import { RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';

import { api } from '../api/client';
import { Button, Card, EmptyState, ErrorBanner, Input, Label, Screen } from '../components/Common';
import { useAuth } from '../context/AuthContext';
import { useDriverDashboard } from '../hooks/useDriverDashboard';
import { colors } from '../theme';

export default function TripsScreen() {
  const { token } = useAuth();
  const { dashboard, error, setError, refresh, refreshing, reload } = useDriverDashboard();
  const [tripForm, setTripForm] = useState({ destination: '', purpose: '', start_odometer: '' });
  const [finishOdometer, setFinishOdometer] = useState('');
  const [loadingAction, setLoadingAction] = useState('');

  const openTrip = dashboard?.open_trip || null;
  const trips = useMemo(() => dashboard?.today_trips || [], [dashboard]);

  async function handleStartTrip() {
    if (!tripForm.destination || !tripForm.purpose || !tripForm.start_odometer) {
      setError('Preencha destino, objetivo e hodômetro inicial.');
      return;
    }

    try {
      setLoadingAction('start');
      setError('');
      await api.startTrip(token, {
        destination: tripForm.destination,
        purpose: tripForm.purpose,
        start_odometer: Number(tripForm.start_odometer),
      });
      setTripForm({ destination: '', purpose: '', start_odometer: '' });
      await reload();
    } catch (err) {
      setError(err.message || 'Não foi possível iniciar a viagem.');
    } finally {
      setLoadingAction('');
    }
  }

  async function handleFinishTrip() {
    if (!openTrip) {
      return;
    }
    if (!finishOdometer) {
      setError('Informe o hodômetro final.');
      return;
    }

    try {
      setLoadingAction('finish');
      setError('');
      await api.finishTrip(token, openTrip.id, { end_odometer: Number(finishOdometer) });
      setFinishOdometer('');
      await reload();
    } catch (err) {
      setError(err.message || 'Não foi possível finalizar a viagem.');
    } finally {
      setLoadingAction('');
    }
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={colors.primary} />}
    >
      <Screen title="Viagens" subtitle="Controle da jornada e histórico do dia.">
        <ErrorBanner message={error} />

        {openTrip ? (
          <Card accent="primary">
            <Text style={styles.title}>Viagem em andamento</Text>
            <Text style={styles.text}>Destino: {openTrip.destination}</Text>
            <Text style={styles.text}>Veículo: {openTrip.vehicle.plate}</Text>
            <Text style={styles.text}>Saída: {openTrip.start_time}</Text>
            <Label>Hodômetro final</Label>
            <Input value={finishOdometer} onChangeText={setFinishOdometer} keyboardType="numeric" placeholder="154320" />
            <Button title="Finalizar viagem" onPress={handleFinishTrip} loading={loadingAction === 'finish'} />
          </Card>
        ) : (
          <Card>
            <Text style={styles.title}>Nova viagem</Text>
            <Label>Destino</Label>
            <Input value={tripForm.destination} onChangeText={(value) => setTripForm((current) => ({ ...current, destination: value }))} placeholder="Cliente Centro" />
            <Label>Objetivo</Label>
            <Input value={tripForm.purpose} onChangeText={(value) => setTripForm((current) => ({ ...current, purpose: value }))} placeholder="Atendimento técnico" />
            <Label>Hodômetro inicial</Label>
            <Input value={tripForm.start_odometer} onChangeText={(value) => setTripForm((current) => ({ ...current, start_odometer: value }))} keyboardType="numeric" placeholder="154000" />
            <Button title="Iniciar viagem" onPress={handleStartTrip} loading={loadingAction === 'start'} />
          </Card>
        )}

        <Card>
          <Text style={styles.title}>Viagens de hoje</Text>
          {trips.length ? trips.map((trip) => (
            <View key={trip.id} style={styles.tripRow}>
              <Text style={styles.tripTitle}>{trip.destination}</Text>
              <Text style={styles.text}>{trip.vehicle.plate} · {trip.status === 'in_progress' ? 'Em andamento' : 'Finalizada'}</Text>
              <Text style={styles.text}>KM rodados: {trip.distance_km}</Text>
            </View>
          )) : <EmptyState>Nenhuma viagem registrada hoje.</EmptyState>}
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
  title: {
    color: colors.text,
    fontSize: 18,
    fontWeight: '800',
  },
  text: {
    color: colors.textMuted,
  },
  tripRow: {
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 2,
  },
  tripTitle: {
    color: colors.text,
    fontWeight: '700',
  },
});
