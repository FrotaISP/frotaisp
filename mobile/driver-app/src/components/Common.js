import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { colors } from '../theme';

export function Screen({ title, subtitle, children, right }) {
  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text style={styles.title}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </View>
        {right}
      </View>
      {children}
    </View>
  );
}

export function Card({ children, accent = 'default' }) {
  return <View style={[styles.card, accent === 'primary' && styles.cardPrimary]}>{children}</View>;
}

export function Label({ children }) {
  return <Text style={styles.label}>{children}</Text>;
}

export function Input(props) {
  return <TextInput placeholderTextColor={colors.textMuted} style={styles.input} {...props} />;
}

export function Button({ title, onPress, loading, variant = 'primary' }) {
  return (
    <Pressable style={[styles.button, variant === 'secondary' && styles.buttonSecondary]} onPress={onPress} disabled={loading}>
      {loading ? (
        <ActivityIndicator color={variant === 'secondary' ? colors.text : colors.primaryDark} />
      ) : (
        <Text style={[styles.buttonText, variant === 'secondary' && styles.buttonTextSecondary]}>{title}</Text>
      )}
    </Pressable>
  );
}

export function ErrorBanner({ message }) {
  if (!message) {
    return null;
  }
  return <Text style={styles.error}>{message}</Text>;
}

export function EmptyState({ children }) {
  return <Text style={styles.empty}>{children}</Text>;
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    padding: 20,
    backgroundColor: colors.background,
    gap: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 12,
  },
  headerText: {
    flex: 1,
    gap: 4,
  },
  title: {
    color: colors.text,
    fontSize: 28,
    fontWeight: '800',
  },
  subtitle: {
    color: colors.textMuted,
    fontSize: 14,
    lineHeight: 20,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    gap: 8,
  },
  cardPrimary: {
    backgroundColor: colors.surfaceSoft,
  },
  label: {
    color: colors.textMuted,
    fontSize: 13,
    fontWeight: '700',
  },
  input: {
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 14,
    color: colors.text,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonSecondary: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  buttonText: {
    color: colors.primaryDark,
    fontWeight: '800',
    fontSize: 15,
  },
  buttonTextSecondary: {
    color: colors.text,
  },
  error: {
    color: colors.danger,
    backgroundColor: 'rgba(127, 29, 29, 0.35)',
    borderRadius: 12,
    padding: 12,
  },
  empty: {
    color: colors.textMuted,
    lineHeight: 20,
  },
});
