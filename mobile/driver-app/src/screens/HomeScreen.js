import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';

import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

function Section({ title, children, right }) {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>{title}</Text>
        {right}
      </View>
      {children}
    </View>
  );
}

function Field({ label, value, onChangeText, keyboardType = 'default', placeholder }) {
  return (
    <View style={styles.fieldGroup}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        value={value}
        onChangeText={onChangeText}
        keyboardType={keyboardType}
        placeholder={placeholder}
        placeholderTextColor="#94a3b8"
        style={styles.input}
      />
    </View>
  );
}

function ToggleRow({ label, value, onValueChange }) {
  return (
    <View style={styles.toggleRow}>
      <Text style={styles.toggleLabel}>{label}</Text>
      <Switch value={value} onValueChange={onValueChange} trackColor={{ true: '#38bdf8', false: '#334155' }} />
    </View>
  );
}

export default function HomeScreen() {
  const { token, driver, signOut, refreshDriver } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [tripForm, setTripForm] = useState({ destination: '', purpose: '', start_odometer: '' });
  const [finishOdometer, setFinishOdometer] = useState('');
  const [locationForm, setLocationForm] = useState({ latitude: '', longitude: '', speed_kmh: '' });
  const [checklistForm, setChecklistForm] = useState({
    odometer: '',
    tires_ok: true,
    oil_ok: true,
    brakes_ok: true,
    lights_ok: true,
    safety_items_ok: true,
    cleanliness_ok: true,
    notes: '',
  });
  const [busyAction, setBusyAction] = useState('');

  async function loadDashboard() {
    const data = await api.dashboard(token);
    setDashboard(data);
    await refreshDriver();
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        setError('');
        await loadDashboard();
      } catch (err) {
        setError(err.message || 'Não foi possível carregar o painel do motorista.');
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, [token]);

  async function refresh() {
    try {
      setRefreshing(true);
      setError('');
      await loadDashboard();
    } catch (err) {
      setError(err.message || 'Não foi possível atualizar os dados.');
    } finally {
      setRefreshing(false);
    }
  }

  async function handleStartTrip() {
    if (!tripForm.destination || !tripForm.purpose || !tripForm.start_odometer) {
      setError('Preencha destino, objetivo e hodômetro inicial.');
      return;
    }

    try {
      setBusyAction('startTrip');
      setError('');
      await api.startTrip(token, {
        destination: tripForm.destination,
        purpose: tripForm.purpose,
        start_odometer: Number(tripForm.start_odometer),
      });
      setTripForm({ destination: '', purpose: '', start_odometer: '' });
      await loadDashboard();
    } catch (err) {
      setError(err.message || 'Não foi possível iniciar a viagem.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleFinishTrip() {
    if (!finishOdometer) {
      setError('Informe o hodômetro final da viagem.');
      return;
    }

    try {
      setBusyAction('finishTrip');
      setError('');
      await api.finishTrip(token, dashboard.open_trip.id, {
        end_odometer: Number(finishOdometer),
      });
      setFinishOdometer('');
      await loadDashboard();
    } catch (err) {
      setError(err.message || 'Não foi possível finalizar a viagem.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleChecklist() {
    try {
      setBusyAction('checklist');
      setError('');
      await api.createChecklist(token, {
        ...checklistForm,
        odometer: checklistForm.odometer ? Number(checklistForm.odometer) : null,
      });
      setChecklistForm({
        odometer: '',
        tires_ok: true,
        oil_ok: true,
        brakes_ok: true,
        lights_ok: true,
        safety_items_ok: true,
        cleanliness_ok: true,
        notes: '',
      });
      await loadDashboard();
    } catch (err) {
      setError(err.message || 'Não foi possível enviar o checklist.');
    } finally {
      setBusyAction('');
    }
  }

  async function handleLocation() {
    if (!locationForm.latitude || !locationForm.longitude) {
      setError('Informe latitude e longitude para enviar a localização.');
      return;
    }

    try {
      setBusyAction('location');
      setError('');
      await api.updateLocation(token, {
        latitude: Number(locationForm.latitude),
        longitude: Number(locationForm.longitude),
        speed_kmh: locationForm.speed_kmh ? Number(locationForm.speed_kmh) : null,
      });
      await loadDashboard();
    } catch (err) {
      setError(err.message || 'Não foi possível atualizar a localização.');
    } finally {
      setBusyAction('');
    }
  }

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#38bdf8" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#38bdf8" />}
    >
      <View style={styles.hero}>
        <View>
          <Text style={styles.heroEyebrow}>Motorista conectado</Text>
          <Text style={styles.heroTitle}>{driver?.name || 'Motorista'}</Text>
          <Text style={styles.heroSubtitle}>{driver?.company_name || 'FleetISP'}</Text>
        </View>
        <Pressable style={styles.outlineButton} onPress={signOut}>
          <Text style={styles.outlineButtonText}>Sair</Text>
        </Pressable>
      </View>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <Section title="Veículo atual">
        {dashboard?.assigned_vehicles?.length ? (
          dashboard.assigned_vehicles.map((vehicle) => (
            <View key={vehicle.id} style={styles.card}>
              <Text style={styles.cardTitle}>{vehicle.plate} · {vehicle.brand} {vehicle.model}</Text>
              <Text style={styles.cardText}>Hodômetro: {vehicle.current_odometer} km</Text>
              <Text style={styles.cardText}>Rastreamento: {vehicle.tracking_status}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.empty}>Nenhum veículo vinculado no momento.</Text>
        )}
      </Section>

      <Section title="Viagem em andamento">
        {dashboard?.open_trip ? (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{dashboard.open_trip.destination}</Text>
            <Text style={styles.cardText}>Saída: {dashboard.open_trip.start_time}</Text>
            <Text style={styles.cardText}>Veículo: {dashboard.open_trip.vehicle.plate}</Text>
            <Field
              label="Hodômetro final"
              value={finishOdometer}
              onChangeText={setFinishOdometer}
              keyboardType="numeric"
              placeholder="Ex.: 154320"
            />
            <Pressable style={styles.button} onPress={handleFinishTrip} disabled={busyAction === 'finishTrip'}>
              <Text style={styles.buttonText}>{busyAction === 'finishTrip' ? 'Finalizando...' : 'Finalizar viagem'}</Text>
            </Pressable>
          </View>
        ) : (
          <View style={styles.card}>
            <Field
              label="Destino"
              value={tripForm.destination}
              onChangeText={(value) => setTripForm((current) => ({ ...current, destination: value }))}
              placeholder="Ex.: Cliente Centro"
            />
            <Field
              label="Objetivo"
              value={tripForm.purpose}
              onChangeText={(value) => setTripForm((current) => ({ ...current, purpose: value }))}
              placeholder="Ex.: Atendimento técnico"
            />
            <Field
              label="Hodômetro inicial"
              value={tripForm.start_odometer}
              onChangeText={(value) => setTripForm((current) => ({ ...current, start_odometer: value }))}
              keyboardType="numeric"
              placeholder="Ex.: 154000"
            />
            <Pressable style={styles.button} onPress={handleStartTrip} disabled={busyAction === 'startTrip'}>
              <Text style={styles.buttonText}>{busyAction === 'startTrip' ? 'Iniciando...' : 'Iniciar viagem'}</Text>
            </Pressable>
          </View>
        )}
      </Section>

      <Section title="Checklist rápido">
        <View style={styles.card}>
          <Field
            label="Hodômetro"
            value={checklistForm.odometer}
            onChangeText={(value) => setChecklistForm((current) => ({ ...current, odometer: value }))}
            keyboardType="numeric"
            placeholder="Ex.: 154010"
          />
          <ToggleRow label="Pneus ok" value={checklistForm.tires_ok} onValueChange={(value) => setChecklistForm((current) => ({ ...current, tires_ok: value }))} />
          <ToggleRow label="Óleo e fluídos ok" value={checklistForm.oil_ok} onValueChange={(value) => setChecklistForm((current) => ({ ...current, oil_ok: value }))} />
          <ToggleRow label="Freios ok" value={checklistForm.brakes_ok} onValueChange={(value) => setChecklistForm((current) => ({ ...current, brakes_ok: value }))} />
          <ToggleRow label="Luzes ok" value={checklistForm.lights_ok} onValueChange={(value) => setChecklistForm((current) => ({ ...current, lights_ok: value }))} />
          <ToggleRow label="Itens de segurança ok" value={checklistForm.safety_items_ok} onValueChange={(value) => setChecklistForm((current) => ({ ...current, safety_items_ok: value }))} />
          <ToggleRow label="Limpeza ok" value={checklistForm.cleanliness_ok} onValueChange={(value) => setChecklistForm((current) => ({ ...current, cleanliness_ok: value }))} />
          <Field
            label="Observações"
            value={checklistForm.notes}
            onChangeText={(value) => setChecklistForm((current) => ({ ...current, notes: value }))}
            placeholder="Anote algo importante se necessário"
          />
          <Pressable style={styles.button} onPress={handleChecklist} disabled={busyAction === 'checklist'}>
            <Text style={styles.buttonText}>{busyAction === 'checklist' ? 'Enviando...' : 'Enviar checklist'}</Text>
          </Pressable>
        </View>
      </Section>

      <Section title="Localização manual">
        <View style={styles.card}>
          <Field
            label="Latitude"
            value={locationForm.latitude}
            onChangeText={(value) => setLocationForm((current) => ({ ...current, latitude: value }))}
            keyboardType="numeric"
            placeholder="-23.550520"
          />
          <Field
            label="Longitude"
            value={locationForm.longitude}
            onChangeText={(value) => setLocationForm((current) => ({ ...current, longitude: value }))}
            keyboardType="numeric"
            placeholder="-46.633308"
          />
          <Field
            label="Velocidade (km/h)"
            value={locationForm.speed_kmh}
            onChangeText={(value) => setLocationForm((current) => ({ ...current, speed_kmh: value }))}
            keyboardType="numeric"
            placeholder="0"
          />
          <Pressable style={styles.button} onPress={handleLocation} disabled={busyAction === 'location'}>
            <Text style={styles.buttonText}>{busyAction === 'location' ? 'Atualizando...' : 'Enviar localização'}</Text>
          </Pressable>
        </View>
      </Section>

      <Section title="Viagens de hoje">
        {dashboard?.today_trips?.length ? dashboard.today_trips.map((trip) => (
          <View key={trip.id} style={styles.card}>
            <Text style={styles.cardTitle}>{trip.destination}</Text>
            <Text style={styles.cardText}>{trip.vehicle.plate} · {trip.status === 'in_progress' ? 'Em andamento' : 'Finalizada'}</Text>
            <Text style={styles.cardText}>KM: {trip.distance_km}</Text>
          </View>
        )) : <Text style={styles.empty}>Nenhuma viagem registrada hoje.</Text>}
      </Section>

      <Section title="Documentos próximos do vencimento">
        {dashboard?.expiring_documents?.length ? dashboard.expiring_documents.map((doc) => (
          <View key={doc.id} style={styles.card}>
            <Text style={styles.cardTitle}>{doc.title}</Text>
            <Text style={styles.cardText}>Vence em {doc.expiration_date}</Text>
            <Text style={styles.cardText}>Dias restantes: {doc.days_until_expiration}</Text>
          </View>
        )) : <Text style={styles.empty}>Nenhum documento vencendo nos próximos 30 dias.</Text>}
      </Section>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
  },
  content: {
    padding: 20,
    paddingBottom: 40,
    gap: 16,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#020617',
  },
  hero: {
    backgroundColor: '#0f172a',
    borderRadius: 24,
    padding: 20,
    borderWidth: 1,
    borderColor: '#1e293b',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 12,
  },
  heroEyebrow: {
    color: '#38bdf8',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 6,
  },
  heroTitle: {
    color: '#f8fafc',
    fontSize: 24,
    fontWeight: '800',
  },
  heroSubtitle: {
    color: '#cbd5e1',
    marginTop: 6,
  },
  section: {
    gap: 10,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  sectionTitle: {
    color: '#f8fafc',
    fontWeight: '800',
    fontSize: 18,
  },
  card: {
    backgroundColor: '#0f172a',
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: '#1e293b',
    gap: 6,
  },
  cardTitle: {
    color: '#f8fafc',
    fontWeight: '700',
    fontSize: 16,
  },
  cardText: {
    color: '#cbd5e1',
  },
  fieldGroup: {
    gap: 6,
    marginBottom: 8,
  },
  fieldLabel: {
    color: '#cbd5e1',
    fontSize: 13,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#020617',
    borderWidth: 1,
    borderColor: '#334155',
    borderRadius: 14,
    color: '#f8fafc',
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  button: {
    marginTop: 8,
    backgroundColor: '#38bdf8',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
  },
  buttonText: {
    color: '#082f49',
    fontWeight: '800',
  },
  outlineButton: {
    borderWidth: 1,
    borderColor: '#334155',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
  },
  outlineButtonText: {
    color: '#cbd5e1',
    fontWeight: '700',
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  toggleLabel: {
    color: '#e2e8f0',
    flex: 1,
    marginRight: 12,
  },
  empty: {
    color: '#94a3b8',
  },
  error: {
    color: '#fda4af',
    backgroundColor: 'rgba(127, 29, 29, 0.35)',
    borderRadius: 12,
    padding: 12,
  },
});
