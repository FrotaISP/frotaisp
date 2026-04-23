import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button, Card, Screen } from '../components/Common';
import { useAuth } from '../context/AuthContext';
import { colors } from '../theme';

function Info({ label, value }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value || '-'}</Text>
    </View>
  );
}

export default function ProfileScreen() {
  const { driver, signOut } = useAuth();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Screen title="Perfil" subtitle="Dados do motorista vinculados ao FleetISP.">
        <Card accent="primary">
          <Text style={styles.name}>{driver?.name || 'Motorista'}</Text>
          <Text style={styles.company}>{driver?.company_name || 'Empresa não informada'}</Text>
        </Card>

        <Card>
          <Info label="Usuário" value={driver?.username} />
          <Info label="E-mail" value={driver?.email} />
          <Info label="Telefone" value={driver?.phone} />
          <Info label="CNH" value={driver?.cnh} />
          <Info label="Validade CNH" value={driver?.cnh_expiration} />
          <Info label="Papel" value={driver?.role} />
        </Card>

        <Button title="Sair da conta" onPress={signOut} variant="secondary" />
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
  name: {
    color: colors.text,
    fontSize: 24,
    fontWeight: '800',
  },
  company: {
    color: colors.textMuted,
  },
  infoRow: {
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 2,
  },
  infoLabel: {
    color: colors.textMuted,
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  infoValue: {
    color: colors.text,
    fontSize: 15,
  },
});
