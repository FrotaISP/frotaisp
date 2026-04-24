import AsyncStorage from '@react-native-async-storage/async-storage';

import { api, createMultipartFormData } from '../api/client';

const OFFLINE_QUEUE_KEY = 'fleetisp_driver_offline_queue';

function isOfflineError(error) {
  const message = String(error?.message || '').toLowerCase();
  return (
    message.includes('network request failed') ||
    message.includes('failed to fetch') ||
    message.includes('networkerror') ||
    message.includes('load failed')
  );
}

export function canQueueOffline(error) {
  return isOfflineError(error);
}

export async function readQueue() {
  const raw = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
  if (!raw) {
    return [];
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    return [];
  }
}

async function writeQueue(items) {
  await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(items));
}

export async function enqueueOfflineAction(type, payload) {
  const items = await readQueue();
  const next = [
    ...items,
    {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      type,
      payload,
      createdAt: new Date().toISOString(),
    },
  ];
  await writeQueue(next);
  return next.length;
}

async function replayItem(token, item) {
  switch (item.type) {
    case 'checklist':
      await api.createChecklist(token, createMultipartFormData(item.payload.fields || {}, { photo: item.payload.photo }));
      return;
    case 'fuel':
      await api.createFuelRecord(token, createMultipartFormData(item.payload.fields || {}, { photo: item.payload.photo, receipt: item.payload.receipt }));
      return;
    case 'occurrence':
      await api.createOccurrence(token, createMultipartFormData(item.payload.fields || {}, { attachment: item.payload.attachment }));
      return;
    case 'location':
      await api.updateLocation(token, item.payload);
      return;
    default:
      return;
  }
}

export async function flushOfflineQueue(token) {
  if (!token) {
    return { sent: 0, remaining: (await readQueue()).length };
  }

  const items = await readQueue();
  if (!items.length) {
    return { sent: 0, remaining: 0 };
  }

  const remaining = [];
  let sent = 0;

  for (const item of items) {
    try {
      await replayItem(token, item);
      sent += 1;
    } catch (error) {
      remaining.push({
        ...item,
        lastError: String(error?.message || 'Falha ao sincronizar item offline.'),
        lastTriedAt: new Date().toISOString(),
      });
    }
  }

  await writeQueue(remaining);
  return { sent, remaining: remaining.length };
}
