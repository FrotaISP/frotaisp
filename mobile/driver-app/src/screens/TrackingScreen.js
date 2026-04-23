import React, { useState } from 'react';
import { RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';

import { api } from '../api/client';
import { Button, Card, EmptyState, ErrorBanner, Input, Label, Screen } from '../components/Common';
import { useAuth } from '../context/AuthContext';
import { useDriverDashboard } from '../hooks/useDriverDashboard';
import { colors } from '../theme';

export default function TrackingScreen() {
  const { token } = useAuth();
  const { dashboard, error, setError, refresh, refreshing, reload } = useDriverDashboard();
  const vehicle = dashboard?.assigned_vehicles?.[0] || null;
  const [form, setForm] = useState({ latitude: '', longitude: '', speed_kmh: '' });
  const [sending, setSending] = useState(false);

  async function handleUpdate() {
    if (!form.latitude || !form.longitude) {
      setError('Informe latitude e longitude.');
      return;
    }

    try {
      setSending(true);
      setError('');
      await api.updateLocation(token, {
        latitude: Number(form.latitude),
        longitude: Number(form.longitude),
        speed_kmh: form.speed_kmh ? Number(form.speed_kmh) : null,
      });
      await reload();
    } catch (err) {
      setError(err.message || 'Não foi possível atualizar a localização.');
    } finally {
      setSending(false);
    }
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={colors.primary} />}
    >
      <Screen title="Mapa e rastreamento" subtitle="Atualização manual da posição do veículo para teste e operação assistida.">
        <ErrorBanner message={error} />

        <Card accent="primary">
          <Text style={styles.title}>Posição atual</Text>
          {vehicle ? (
            <>
              <Text style={styles.rowText}>Veículo: {vehicle.plate}</Text>
              <Text style={styles.rowText}>Status: {vehicle.tracking_status}</Text>
              <Text style={styles.rowText}>Última latitude: {vehicle.latitude || 'sem dado'}</Text>
              <Text style={styles.rowText}>Última longitude: {vehicle.longitude || 'sem dado'}</Text>
            </>
          ) : (
            <EmptyState>Nenhum veículo vinculado para rastreamento.</EmptyState>
          )}
        </Card>

        <Card>
          <Text style={styles.title}>Enviar nova posição</Text>
          <Label>Latitude</Label>
          <Input value={form.latitude} onChangeText={(value) => setForm((current) => ({ ...current, latitude: value }))} keyboardType="numeric" placeholder="-23.550520" />
          <Label>Longitude</Label>
          <Input value={form.longitude} onChangeText={(value) => setForm((current) => ({ ...current, longitude: value }))} keyboardType="numeric" placeholder="-46.633308" />
          <Label>Velocidade (km/h)</Label>
          <Input value={form.speed_kmh} onChangeText={(value) => setForm((current) => ({ ...current, speed_kmh: value }))} keyboardType="numeric" placeholder="0" />
          <Button title="Atualizar localização" onPress={handleUpdate} loading={sending} />
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
  rowText: {
    color: colors.textMuted,
  },
});
