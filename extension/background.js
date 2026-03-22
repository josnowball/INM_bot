/**
 * CitaFacil Chrome Extension — Service Worker
 * Handles auth token storage and API communication.
 */

const DEFAULT_API_URL = 'https://citafacil.app/api';

// Get API base URL from storage or default
async function getApiUrl() {
  const { apiUrl } = await chrome.storage.local.get('apiUrl');
  return apiUrl || DEFAULT_API_URL;
}

// Get stored auth token
async function getToken() {
  const { authToken } = await chrome.storage.local.get('authToken');
  return authToken;
}

// Store auth token
async function setToken(token) {
  await chrome.storage.local.set({ authToken: token });
}

// Get stored profile
async function getProfile() {
  const { profile } = await chrome.storage.local.get('profile');
  return profile;
}

// API call helper
async function apiCall(endpoint, options = {}) {
  const baseUrl = await getApiUrl();
  const token = await getToken();

  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const resp = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || `API error ${resp.status}`);
  }

  return resp.json();
}

// Login and sync profile
async function login(email, password) {
  const result = await apiCall('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  await setToken(result.access_token);
  // Sync profile
  const profile = await apiCall('/profile/');
  await chrome.storage.local.set({ profile });
  return { token: result.access_token, profile };
}

// Message handler for popup and content scripts
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'login') {
    login(msg.email, msg.password)
      .then(result => sendResponse({ success: true, profile: result.profile }))
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true; // async
  }

  if (msg.action === 'getProfile') {
    getProfile()
      .then(profile => sendResponse({ profile }))
      .catch(() => sendResponse({ profile: null }));
    return true;
  }

  if (msg.action === 'syncProfile') {
    apiCall('/profile/')
      .then(profile => {
        chrome.storage.local.set({ profile });
        sendResponse({ success: true, profile });
      })
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true;
  }

  if (msg.action === 'logout') {
    chrome.storage.local.remove(['authToken', 'profile']);
    sendResponse({ success: true });
    return true;
  }

  if (msg.action === 'getToken') {
    getToken().then(token => sendResponse({ token }));
    return true;
  }
});
