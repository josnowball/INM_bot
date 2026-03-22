/**
 * CitaFacil Extension — Popup Logic
 * Handles login, profile display, and sync.
 */

const TIP_URL = ''; // Set to Stripe/PayPal link when ready

document.addEventListener('DOMContentLoaded', async () => {
  const loginView = document.getElementById('login-view');
  const profileView = document.getElementById('profile-view');

  // Check if already logged in
  chrome.runtime.sendMessage({ action: 'getProfile' }, (resp) => {
    if (resp && resp.profile && resp.profile.first_name) {
      showProfile(resp.profile);
    } else {
      showLogin();
    }
  });

  // Login button
  document.getElementById('login-btn').addEventListener('click', async () => {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const status = document.getElementById('login-status');

    if (!email || !password) {
      status.textContent = 'Please enter email and password.';
      status.className = 'status error';
      status.classList.remove('hidden');
      return;
    }

    status.textContent = 'Logging in...';
    status.className = 'status';
    status.classList.remove('hidden');

    chrome.runtime.sendMessage(
      { action: 'login', email, password },
      (resp) => {
        if (resp && resp.success) {
          showProfile(resp.profile);
        } else {
          status.textContent = resp?.error || 'Login failed';
          status.className = 'status error';
        }
      }
    );
  });

  // Sync button
  document.getElementById('sync-btn').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'syncProfile' }, (resp) => {
      if (resp && resp.success) {
        showProfile(resp.profile);
      }
    });
  });

  // Logout button
  document.getElementById('logout-btn').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'logout' }, () => {
      showLogin();
    });
  });

  // Tip button
  document.getElementById('tip-btn').addEventListener('click', () => {
    if (TIP_URL) {
      chrome.tabs.create({ url: TIP_URL });
    } else {
      alert('Tip link coming soon! Thank you for your support.');
    }
  });

  function showLogin() {
    loginView.classList.remove('hidden');
    profileView.classList.add('hidden');
  }

  function showProfile(profile) {
    loginView.classList.add('hidden');
    profileView.classList.remove('hidden');

    const name = [profile.first_name, profile.last_name].filter(Boolean).join(' ') || '—';
    document.getElementById('profile-name').textContent = name;
    document.getElementById('profile-nationality').textContent = profile.nationality || '—';
    document.getElementById('profile-passport').textContent = profile.passport_number || '—';
    document.getElementById('profile-phone').textContent = profile.phone || '—';

    const pct = profile.completion_pct || 0;
    document.getElementById('profile-pct').style.width = `${pct}%`;
    document.getElementById('profile-pct-text').textContent = `${pct}%`;
  }
});
