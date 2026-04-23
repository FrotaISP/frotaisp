import Constants from 'expo-constants';

const API_BASE_URL =
  Constants.expoConfig?.extra?.apiBaseUrl ||
  'http://191.123.65.10:5000/api/mobile';

function extractErrorMessage(data) {
  if (!data) {
    return 'Não foi possível completar a requisição.';
  }

  if (typeof data.detail === 'string' && data.detail) {
    return data.detail;
  }

  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
    return data.non_field_errors[0];
  }

  const firstEntry = Object.entries(data).find(([, value]) => Array.isArray(value) && value.length);
  if (firstEntry) {
    const [field, messages] = firstEntry;
    return `${field}: ${messages[0]}`;
  }

  return 'Não foi possível completar a requisição.';
}

async function request(path, { method = 'GET', token, body } = {}) {
  const headers = {
    Accept: 'application/json',
  };

  if (body) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers.Authorization = `Token ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

export const api = {
  login: (payload) => request('/auth/login/', { method: 'POST', body: payload }),
  logout: (token) => request('/auth/logout/', { method: 'POST', token }),
  me: (token) => request('/me/', { token }),
  dashboard: (token) => request('/dashboard/', { token }),
  trips: (token) => request('/trips/', { token }),
  startTrip: (token, payload) => request('/trips/', { method: 'POST', token, body: payload }),
  finishTrip: (token, id, payload) => request(`/trips/${id}/finish/`, { method: 'POST', token, body: payload }),
  checklists: (token) => request('/checklists/', { token }),
  createChecklist: (token, payload) => request('/checklists/', { method: 'POST', token, body: payload }),
  updateLocation: (token, payload) => request('/location/', { method: 'POST', token, body: payload }),
};
