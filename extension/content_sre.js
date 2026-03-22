/**
 * CitaFacil — SRE Content Script
 * Auto-fills forms on citas.sre.gob.mx with saved profile data.
 */

(function () {
  'use strict';

  let profile = null;
  let panelVisible = false;
  let filling = false;

  // Field mapping: profile key → possible form selectors
  const FIELD_MAP = {
    first_name: ['[name*="nombre" i]', '[id*="nombre" i]', '[placeholder*="nombre" i]'],
    last_name: ['[name*="paterno" i]', '[id*="paterno" i]', '[placeholder*="paterno" i]'],
    middle_name: ['[name*="materno" i]', '[id*="materno" i]'],
    birth_date: ['[name*="nacimiento" i]', '[id*="nacimiento" i]', '[name*="fecha" i]', '[type="date"]'],
    nationality: ['[name*="nacionalidad" i]', '[id*="nacionalidad" i]', 'select[name*="nacionalidad" i]'],
    gender: ['[name*="sexo" i]', '[name*="genero" i]', 'select[name*="sexo" i]'],
    curp: ['[name*="curp" i]', '[id*="curp" i]'],
    passport_number: ['[name*="pasaporte" i]', '[id*="pasaporte" i]'],
    phone: ['[name*="telefono" i]', '[id*="telefono" i]', '[name*="celular" i]', '[type="tel"]'],
    address_street: ['[name*="calle" i]', '[name*="direccion" i]', '[name*="domicilio" i]'],
    address_city: ['[name*="ciudad" i]', '[name*="municipio" i]'],
    address_state: ['[name*="estado" i]', 'select[name*="estado" i]'],
    address_zip: ['[name*="postal" i]', '[name*="cp" i]'],
  };

  // Load profile from extension storage
  function loadProfile() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'getProfile' }, (resp) => {
        if (resp && resp.profile) {
          profile = resp.profile;
          resolve(profile);
        } else {
          resolve(null);
        }
      });
    });
  }

  // Try to fill a form field
  function fillField(selectors, value) {
    if (!value) return false;
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (!el) continue;

      if (el.tagName === 'SELECT') {
        // Try to select by value or text
        const opts = Array.from(el.options);
        const match = opts.find(
          (o) => o.value.toLowerCase().includes(value.toLowerCase()) ||
                 o.text.toLowerCase().includes(value.toLowerCase())
        );
        if (match) {
          el.value = match.value;
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        }
      } else {
        el.focus();
        el.value = value;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
      }
    }
    return false;
  }

  // Fill all form fields
  async function autoFill() {
    if (!profile || filling) return;
    filling = true;
    updatePanel('Filling forms...');

    let filled = 0;
    let total = 0;

    for (const [key, selectors] of Object.entries(FIELD_MAP)) {
      const value = profile[key];
      if (value) {
        total++;
        if (fillField(selectors, value)) {
          filled++;
        }
        // Small delay between fields to mimic human input
        await new Promise((r) => setTimeout(r, 200));
      }
    }

    // Also try email field
    if (profile.email) {
      fillField(['[name*="correo" i]', '[type="email"]', '[name*="email" i]'], profile.email);
    }

    filling = false;
    updatePanel(`Filled ${filled}/${total} fields. Check and continue.`);
  }

  // Auto-advance to next page
  function clickNext() {
    const nextTexts = ['Siguiente', 'Continuar', 'Next', 'Continue', 'Guardar'];
    for (const text of nextTexts) {
      const btns = document.querySelectorAll('button, a.btn, input[type="submit"]');
      for (const btn of btns) {
        if (btn.textContent.trim().toLowerCase().includes(text.toLowerCase())) {
          btn.click();
          return true;
        }
      }
    }
    return false;
  }

  // Create floating panel
  function createPanel() {
    if (document.getElementById('citafacil-panel')) return;

    const panel = document.createElement('div');
    panel.id = 'citafacil-panel';
    panel.innerHTML = `
      <div class="cf-card" id="cf-card">
        <div class="cf-header">
          <span class="cf-title">🇲🇽 CitaFacil</span>
          <button class="cf-close" id="cf-minimize">—</button>
        </div>
        <div class="cf-status" id="cf-status">Ready to auto-fill your forms.</div>
        <button class="cf-btn cf-btn-primary" id="cf-fill">Auto-Fill Forms</button>
        <button class="cf-btn cf-btn-secondary" id="cf-next">Next Page →</button>
      </div>
      <div class="cf-minimized hidden" id="cf-mini" title="CitaFacil">🇲🇽</div>
    `;

    document.body.appendChild(panel);

    document.getElementById('cf-fill').addEventListener('click', autoFill);
    document.getElementById('cf-next').addEventListener('click', () => {
      if (!clickNext()) {
        updatePanel('No "Next" button found on this page.');
      }
    });
    document.getElementById('cf-minimize').addEventListener('click', () => {
      document.getElementById('cf-card').classList.add('hidden');
      document.getElementById('cf-mini').classList.remove('hidden');
    });
    document.getElementById('cf-mini').addEventListener('click', () => {
      document.getElementById('cf-card').classList.remove('hidden');
      document.getElementById('cf-mini').classList.add('hidden');
    });

    panelVisible = true;
  }

  function updatePanel(msg) {
    const el = document.getElementById('cf-status');
    if (el) el.textContent = msg;
  }

  // Initialize
  async function init() {
    const p = await loadProfile();
    if (p) {
      createPanel();
      updatePanel(`Profile loaded: ${p.first_name || ''} ${p.last_name || ''}`);
    } else {
      // Show minimal panel suggesting login
      createPanel();
      updatePanel('Log in via the CitaFacil extension popup to auto-fill.');
      const fillBtn = document.getElementById('cf-fill');
      if (fillBtn) fillBtn.disabled = true;
    }
  }

  // Wait for page to be ready, then init
  if (document.readyState === 'complete') {
    init();
  } else {
    window.addEventListener('load', init);
  }

  // Re-init on SPA navigation (URL change without full page load)
  let lastUrl = location.href;
  new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      setTimeout(init, 1000); // Wait for new page content
    }
  }).observe(document.body, { childList: true, subtree: true });
})();
