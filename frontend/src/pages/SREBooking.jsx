import { useState, useEffect } from 'react'
import { getSREProcedures, getSREOffices, bookSRE, getProfile } from '../api'
import SecurityBadge from '../components/SecurityBadge'
import { CheckCircle, AlertCircle, Loader, ArrowRight, Lock } from 'lucide-react'

export default function SREBooking() {
  const [procedures, setProcedures] = useState({})
  const [offices, setOffices] = useState({})
  const [profile, setProfile] = useState(null)
  const [selectedProc, setSelectedProc] = useState('')
  const [selectedOffice, setSelectedOffice] = useState('')
  const [mcEmail, setMcEmail] = useState('')
  const [mcPassword, setMcPassword] = useState('')
  const [step, setStep] = useState(1) // 1=procedure, 2=credentials, 3=office, 4=confirm, 5=result
  const [booking, setBooking] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getSREProcedures(), getSREOffices(), getProfile()])
      .then(([procs, offs, prof]) => {
        setProcedures(procs)
        setOffices(offs)
        setProfile(prof)
      })
      .catch(err => setError(err.message))
  }, [])

  async function handleBook() {
    setBooking(true)
    setError('')
    try {
      const res = await bookSRE({
        procedure_type: selectedProc,
        mi_consulado_email: mcEmail,
        mi_consulado_password: mcPassword,
        preferred_office: selectedOffice || null,
      })
      setResult(res)
      setStep(5)
      // Clear credentials from state
      setMcPassword('')
    } catch (err) {
      setError(err.message)
    } finally {
      setBooking(false)
    }
  }

  return (
    <div className="container" style={{ padding: '40px 20px', maxWidth: 700 }}>
      <h1 style={{ fontSize: '1.6rem', marginBottom: 8 }}>Book SRE Appointment</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
        Passport, visa, and other SRE services via MiConsulado.
        You provide your own login — we never store your credentials.
      </p>

      <SecurityBadge />

      {error && <div className="alert alert-error">{error}</div>}

      {/* Steps */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 32 }}>
        {['Service', 'Login', 'Office', 'Confirm'].map((label, i) => (
          <div key={label} style={{
            flex: 1, textAlign: 'center', padding: '8px 0',
            borderBottom: `3px solid ${step > i ? 'var(--accent)' : 'var(--border)'}`,
            color: step > i ? 'var(--accent)' : 'var(--text-muted)',
            fontWeight: step === i + 1 ? 600 : 400,
            fontSize: '0.85rem',
          }}>
            {label}
          </div>
        ))}
      </div>

      {/* Step 1: Select procedure */}
      {step === 1 && (
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 16 }}>Select SRE service</h2>
          <div style={{ display: 'grid', gap: 12 }}>
            {Object.entries(procedures).map(([key, proc]) => (
              <button
                key={key}
                onClick={() => { setSelectedProc(key); setStep(2) }}
                className="card"
                style={{
                  width: '100%', textAlign: 'left', cursor: 'pointer',
                  border: '1px solid var(--border)',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600 }}>{proc.name}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{proc.description}</div>
                </div>
                <ArrowRight size={18} color="var(--text-muted)" />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: MiConsulado credentials */}
      {step === 2 && (
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 8 }}>MiConsulado Login</h2>

          <div style={{
            background: '#fef3c7', border: '1px solid #fde68a', borderRadius: 8,
            padding: 12, marginBottom: 20, fontSize: '0.85rem', color: '#92400e',
            display: 'flex', gap: 8, alignItems: 'flex-start',
          }}>
            <Lock size={16} style={{ flexShrink: 0, marginTop: 2 }} />
            <div>
              <strong>Your credentials are never stored.</strong> They are used once for this booking
              session and immediately discarded. We cannot access your MiConsulado account later.
              You must already have a MiConsulado account — we do not create accounts on your behalf.
            </div>
          </div>

          <div className="form-group">
            <label>MiConsulado Email</label>
            <input
              type="email"
              value={mcEmail}
              onChange={e => setMcEmail(e.target.value)}
              placeholder="Your MiConsulado email"
            />
          </div>
          <div className="form-group">
            <label>MiConsulado Password</label>
            <input
              type="password"
              value={mcPassword}
              onChange={e => setMcPassword(e.target.value)}
              placeholder="Your MiConsulado password"
            />
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
            <button
              onClick={() => setStep(3)}
              disabled={!mcEmail || !mcPassword}
              className="btn btn-accent"
            >
              Continue
            </button>
            <button onClick={() => setStep(1)} className="btn btn-secondary">
              Back
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Select office */}
      {step === 3 && (
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 16 }}>Select preferred office</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10 }}>
            {Object.entries(offices).map(([key, name]) => (
              <button
                key={key}
                onClick={() => { setSelectedOffice(key); setStep(4) }}
                className="card"
                style={{
                  cursor: 'pointer', textAlign: 'center', padding: '14px 16px',
                  border: '1px solid var(--border)', fontSize: '0.9rem', fontWeight: 500,
                }}
              >
                {name}
              </button>
            ))}
          </div>
          <button onClick={() => setStep(2)} style={{
            marginTop: 16, background: 'none', border: 'none',
            color: 'var(--text-muted)', fontSize: '0.9rem', cursor: 'pointer',
          }}>
            Back
          </button>
        </div>
      )}

      {/* Step 4: Confirm */}
      {step === 4 && (
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 16 }}>Confirm your booking</h2>
          <div className="card" style={{ marginBottom: 24 }}>
            <div style={{ display: 'grid', gap: 12 }}>
              <div>
                <span style={{ fontWeight: 600 }}>Service:</span>{' '}
                {procedures[selectedProc]?.name}
              </div>
              <div>
                <span style={{ fontWeight: 600 }}>Office:</span>{' '}
                {offices[selectedOffice]}
              </div>
              <div>
                <span style={{ fontWeight: 600 }}>MiConsulado:</span>{' '}
                {mcEmail}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                We'll log into MiConsulado with your credentials, fill the forms
                with your profile data, and book the next available slot.
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <button
              onClick={handleBook}
              disabled={booking}
              className="btn btn-accent btn-lg"
            >
              {booking ? (
                <><Loader size={18} /> Booking...</>
              ) : (
                <><CheckCircle size={18} /> Book Appointment</>
              )}
            </button>
            <button onClick={() => setStep(3)} className="btn btn-secondary">
              Back
            </button>
          </div>
        </div>
      )}

      {/* Step 5: Result */}
      {step === 5 && result && (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <Loader size={48} color="var(--accent)" style={{ margin: '0 auto 16px' }} />
          <h2>Booking in progress</h2>
          <p style={{ color: 'var(--text-muted)', marginTop: 8 }}>
            We're logging into MiConsulado and searching for available slots.
            Check your dashboard for updates.
          </p>
          <a href="/dashboard" className="btn btn-accent" style={{ marginTop: 24 }}>
            Go to Dashboard
          </a>
        </div>
      )}
    </div>
  )
}
