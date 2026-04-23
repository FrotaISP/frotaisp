import React, { useState } from 'react';
import { RefreshControl, ScrollView, StyleSheet, Switch, Text, View } from 'react-native';

import { api } from '../api/client';
import { Button, Card, EmptyState, ErrorBanner, Input, Label, Screen } from '../components/Common';
import { useAuth } from '../context/AuthContext';
import { useDriverDashboard } from '../hooks/useDriverDashboard';
import { colors } from '../theme';

function Toggle({ label, value, onChange }) {
  return (
    <View style={styles.toggleRow}>
      <Text style={styles.toggleText}>{label}</Text>
      <Switch value={value} onValueChange={onChange} trackColor={{ true: colors.primary, false: '#334155' }} />
    </View>
  );
}

export default function ChecklistScreen() {
  const { token } = useAuth();
  const { dashboard, error, setError, refresh, refreshing, reload } = useDriverDashboard();
  const [form, setForm] = useState({
    odometer: '',
    tires_ok: true,
    oil_ok: true,
    brakes_ok: true,
    lights_ok: true,
    safety_items_ok: true,
    cleanliness_ok: true,
    notes: '',
  });
  const [sending, setSending] = useState(false);

  async function handleSubmit() {
    try {
      setSending(true);
      setError('');
      await api.createChecklist(token, {
        ...form,
        odometer: form.odometer ? Number(form.odometer) : null,
      });
      setForm({
        odometer: '',
        tires_ok: true,
        oil_ok: true,
        brakes_ok: true,
        lights_ok: true,
        safety_items_ok: true,
        cleanliness_ok: true,
        notes: '',
      });
      await reload();
    } catch (err) {
      setError(err.message || 'Não foi possível enviar o checklist.');
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
      <Screen title="Checklist" subtitle="Checklist rápido antes da saída do veículo.">
        <ErrorBanner message={error} />

        <Card accent="primary">
          <Text style={styles.title}>Novo checklist</Text>
          <Label>Hodômetro</Label>
          <Input value={form.odometer} onChangeText={(value) => setForm((current) => ({ ...current, odometer: value }))} keyboardType="numeric" placeholder="154010" />
          <Toggle label="Pneus ok" value={form.tires_ok} onChange={(value) => setForm((current) => ({ ...current, tires_ok: value }))} />
          <Toggle label="Óleo e fluídos ok" value={form.oil_ok} onChange={(value) => setForm((current) => ({ ...current, oil_ok: value }))} />
          <Toggle label="Freios ok" value={form.brakes_ok} onChange={(value) => setForm((current) => ({ ...current, brakes_ok: value }))} />
          <Toggle label="Luzes ok" value={form.lights_ok} onChange={(value) => setForm((current) => ({ ...current, lights_ok: value }))} />
          <Toggle label="Itens de segurança ok" value={form.safety_items_ok} onChange={(value) => setForm((current) => ({ ...current, safety_items_ok: value }))} />
          <Toggle label="Limpeza ok" value={form.cleanliness_ok} onChange={(value) => setForm((current) => ({ ...current, cleanliness_ok: value }))} />
          <Label>Observações</Label>
          <Input value={form.notes} onChangeText={(value) => setForm((current) => ({ ...current, notes: value }))} placeholder="Observações úteis do veículo" />
          <Button title="Enviar checklist" onPress={handleSubmit} loading={sending} />
        </Card>

        <Card>
          <Text style={styles.title}>Últimos checklists</Text>
          {dashboard?.recent_checklists?.length ? dashboard.recent_checklists.map((item) => (
            <View key={item.id} style={styles.historyRow}>
              <Text style={styles.rowTitle}>{item.vehicle.plate}</Text>
              <Text style={styles.rowText}>Status: {item.status}</Text>
              <Text style={styles.rowText}>Data: {item.inspected_at}</Text>
            </View>
          )) : <EmptyState>Nenhum checklist recente encontrado.</EmptyState>}
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
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  toggleText: {
    color: colors.text,
    flex: 1,
    marginRight: 12,
  },
  historyRow: {
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 2,
  },
  rowTitle: {
    color: colors.text,
    fontWeight: '700',
  },
  rowText: {
    color: colors.textMuted,
  },
});
