/**
 * CitaFacil — INM Content Script
 * Auto-fills solicitud de estancia forms on citas.inm.gob.mx.
 */

(function () {
  'use strict';

  let profile = null;
  let filling = false;

  // INM-specific field mapping (solicitud de estancia fields)
  const FIELD_MAP = {
    first_name: ['[name*="nombre" i]', '[id*="nombre" i]'],
    last_name: ['[name*="paterno" i]', '[id*="apellido_paterno" i]', '[id*="paterno" i]'],
    middle_name: ['[name*="materno" i]', '[id*="apellido_materno" i]', '[id*="materno" i]'],
    birth_date: ['[name*="nacimiento" i]', '[id*="fecha_nac" i]', '[type="date"]'],
    nationality: ['[name*="nacionalidad" i]', 'select[name*="nacionalidad" i]', 'select[id*="nacionalidad" i]'],
    gender: ['[name*="sexo" i]', 'select[name*="sexo" i]'],
    marital_status: ['[name*="civil" i]', 'select[name*="civil" i]', 'select[name*="estado_civil" i]'],
    curp: ['[name*="curp" i]', '[id*="curp" i]'],
    passport_number: ['[name*="pasaporte" i]', '[id*="pasaporte" i]', '[name*="documento" i]'],
    passport_country: ['[name*="pais_pasaporte" i]', 'select[name*="pais_doc" i]'],
    phone: ['[name*="telefono" i]', '[id*="telefono" i]', '[type="tel"]'],
    address_street: ['[name*="calle" i]', '[name*="domicilio" i]'],
    address_city: ['[name*="ciudad" i]', '[name*="municipio" i]'],
    address_state: ['[name*="estado" i]', 'select[name*="entidad" i]'],
    address_zip: ['[name*="postal" i]', '[name*="cp" i]'],
    address_country: ['[name*="pais" i]:not([name*="pasaporte"])', 'select[name*="pais_residencia" i]'],
    immigration_status: ['[name*="condicion" i]', 'select[name*="condicion" i]'],
    entry_date: ['[name*="ingreso" i]', '[name*="fecha_ingreso" i]'],
    permit_number: ['[name*="permiso" i]', '[name*="numero_permiso" i]'],
  };

  function loadProfile() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'getProfile' }, (resp) => {
        profile = resp?.profile || null;
        resolve(profile);
      });
    });
  }

  function fillField(selectors, value) {
    if (!value) return false;
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (!el) continue;

      if (el.tagName === 'SELECT') {
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

  async function autoFill() {
    if (!profile || filling) return;
    filling = true;
    updatePanel('Filling solicitud...');

    let filled = 0, total = 0;

    for (const [key, selectors] of Object.entries(FIELD_MAP)) {
      const value = profile[key];
      if (value) {
        total++;
        if (fillField(selectors, value)) filled++;
        await new Promise((r) => setTimeout(r, 200));
      }
    }

    if (profile.email) {
      fillField(['[name*="correo" i]', '[type="email"]'], profile.email);
    }

    filling = false;
    updatePanel(`Filled ${filled}/${total} fields. Review and submit.`);
  }

  function clickNext() {
    const texts = ['Siguiente', 'Continuar', 'Enviar', 'Next', 'Submit'];
    for (const text of texts) {
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
        <div class="cf-status" id="cf-status">Ready to fill your solicitud.</div>
        <button class="cf-btn cf-btn-primary" id="cf-fill">Auto-Fill Solicitud</button>
        <button class="cf-btn cf-btn-secondary" id="cf-next">Next Step →</button>
      </div>
      <div class="cf-minimized hidden" id="cf-mini" title="CitaFacil">🇲🇽</div>
    `;

    document.body.appendChild(panel);

    document.getElementById('cf-fill').addEventListener('click', autoFill);
    document.getElementById('cf-next').addEventListener('click', () => {
      if (!clickNext()) updatePanel('No "Next" button found.');
    });
    document.getElementById('cf-minimize').addEventListener('click', () => {
      document.getElementById('cf-card').classList.add('hidden');
      document.getElementById('cf-mini').classList.remove('hidden');
    });
    document.getElementById('cf-mini').addEventListener('click', () => {
      document.getElementById('cf-card').classList.remove('hidden');
      document.getElementById('cf-mini').classList.add('hidden');
    });
  }

  function updatePanel(msg) {
    const el = document.getElementById('cf-status');
    if (el) el.textContent = msg;
  }

  async function init() {
    const p = await loadProfile();
    createPanel();
    if (p) {
      updatePanel(`Profile: ${p.first_name || ''} ${p.last_name || ''}. Click Auto-Fill.`);
    } else {
      updatePanel('Log in via CitaFacil extension popup first.');
      const btn = document.getElementById('cf-fill');
      if (btn) btn.disabled = true;
    }
  }

  if (document.readyState === 'complete') init();
  else window.addEventListener('load', init);

  let lastUrl = location.href;
  new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      setTimeout(init, 1000);
    }
  }).observe(document.body, { childList: true, subtree: true });
})();
