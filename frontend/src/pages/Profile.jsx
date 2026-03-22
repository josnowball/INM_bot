import { useState, useEffect } from 'react'
import { getProfile, updateProfile } from '../api'
import SecurityBadge from '../components/SecurityBadge'
import { Save, CheckCircle } from 'lucide-react'

const SECTIONS = [
  {
    title: 'Personal Information',
    fields: [
      { key: 'first_name', label: 'Nombre(s)', required: true },
      { key: 'last_name', label: 'Apellido Paterno', required: true },
      { key: 'middle_name', label: 'Apellido Materno' },
      { key: 'nationality', label: 'Nationality', required: true },
      { key: 'birth_date', label: 'Date of Birth', type: 'date', required: true },
      { key: 'birth_country', label: 'Country of Birth', required: true },
      { key: 'birth_state', label: 'State of Birth' },
      { key: 'gender', label: 'Gender', type: 'select', options: ['', 'Masculino', 'Femenino'], required: true },
      { key: 'marital_status', label: 'Marital Status', type: 'select',
        options: ['', 'Soltero(a)', 'Casado(a)', 'Divorciado(a)', 'Viudo(a)', 'Union Libre'], required: true },
    ],
  },
  {
    title: 'Documents',
    fields: [
      { key: 'passport_number', label: 'Passport Number', required: true },
      { key: 'passport_country', label: 'Passport Country', required: true },
      { key: 'passport_expiry', label: 'Passport Expiry', type: 'date', required: true },
      { key: 'curp', label: 'CURP (if applicable)' },
    ],
  },
  {
    title: 'Contact Information',
    fields: [
      { key: 'phone', label: 'Phone Number', required: true },
      { key: 'address_street', label: 'Street Address', required: true },
      { key: 'address_city', label: 'City', required: true },
      { key: 'address_state', label: 'State', required: true },
      { key: 'address_zip', label: 'Postal Code', required: true },
      { key: 'address_country', label: 'Country', required: true },
    ],
  },
  {
    title: 'Immigration Information',
    fields: [
      { key: 'immigration_status', label: 'Current Immigration Status' },
      { key: 'entry_date', label: 'Date of Entry to Mexico', type: 'date' },
      { key: 'permit_number', label: 'Permit / Card Number' },
    ],
  },
]

export default function Profile() {
  const [data, setData] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getProfile()
      .then(p => {
        const clean = {}
        for (const [k, v] of Object.entries(p)) {
          if (k !== 'completion_pct') clean[k] = v || ''
        }
        setData(clean)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  function handleChange(key, value) {
    setData(prev => ({ ...prev, [key]: value }))
    setSaved(false)
  }

  async function handleSave() {
    setSaving(true)
    setError('')
    try {
      const result = await updateProfile(data)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="container" style={{ padding: '40px 20px' }}>Loading...</div>

  return (
    <div className="container" style={{ padding: '40px 20px', maxWidth: 700 }}>
      <h1 style={{ fontSize: '1.6rem', marginBottom: 8 }}>Your Profile</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
        This data is used to auto-fill appointment forms. All fields are encrypted at rest.
      </p>

      <SecurityBadge />

      {error && <div className="alert alert-error">{error}</div>}

      {SECTIONS.map(section => (
        <div key={section.title} style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 16, paddingBottom: 8, borderBottom: '1px solid var(--border)' }}>
            {section.title}
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px 20px' }}>
            {section.fields.map(f => (
              <div key={f.key} className="form-group" style={{ marginBottom: 0 }}>
                <label>
                  {f.label}
                  {f.required && <span style={{ color: 'var(--accent)' }}> *</span>}
                </label>
                {f.type === 'select' ? (
                  <select
                    value={data[f.key] || ''}
                    onChange={e => handleChange(f.key, e.target.value)}
                  >
                    {f.options.map(o => (
                      <option key={o} value={o}>{o || '— Select —'}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={f.type || 'text'}
                    value={data[f.key] || ''}
                    onChange={e => handleChange(f.key, e.target.value)}
                    placeholder={f.label}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      <div style={{ position: 'sticky', bottom: 20, display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn btn-primary btn-lg"
          style={{ boxShadow: 'var(--shadow-lg)' }}
        >
          {saving ? 'Saving...' : saved ? (
            <><CheckCircle size={18} /> Saved</>
          ) : (
            <><Save size={18} /> Save Profile</>
          )}
        </button>
      </div>
    </div>
  )
}
