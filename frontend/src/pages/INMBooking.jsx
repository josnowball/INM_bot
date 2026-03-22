import { useState, useEffect } from 'react'
import { getINMProcedures, getINMOffices, bookINM, getProfile } from '../api'
import SecurityBadge from '../components/SecurityBadge'
import { CheckCircle, AlertCircle, Loader, ArrowRight } from 'lucide-react'

export default function INMBooking() {
  const [procedures, setProcedures] = useState({})
  const [offices, setOffices] = useState({})
  const [profile, setProfile] = useState(null)
  const [selectedProc, setSelectedProc] = useState('')
  const [selectedOffice, setSelectedOffice] = useState('')
  const [step, setStep] = useState(1) // 1=procedure, 2=office, 3=confirm, 4=result
  const [booking, setBooking] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getINMProcedures(), getINMOffices(), getProfile()])
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
      const res = await bookINM({
        procedure_type: selectedProc,
        preferred_office: selectedOffice || null,
      })
      setResult(res)
      setStep(4)
    } catch (err) {
      setError(err.message)
    } finally {
      setBooking(false)
    }
  }

  return (
    <div className="container" style={{ padding: '40px 20px', maxWidth: 700 }}>
      <h1 style={{ fontSize: '1.6rem', marginBottom: 8 }}>Book INM Appointment</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
        We'll fill out the solicitud de estancia and book your appointment automatically.
      </p>

      <SecurityBadge />

      {/* Profile check */}
      {profile && profile.completion_pct < 50 && (
        <div className="alert alert-info" style={{ marginBottom: 24 }}>
          <strong>Complete your profile first.</strong> We need your personal data to fill out the INM forms.
          Your profile is {profile.completion_pct}% complete.{' '}
          <a href="/profile">Complete profile</a>
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      {/* Step indicator */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 32 }}>
        {['Procedure', 'Office', 'Confirm'].map((label, i) => (
          <div key={label} style={{
            flex: 1, textAlign: 'center', padding: '8px 0',
            borderBottom: `3px solid ${step > i ? 'var(--primary)' : 'var(--border)'}`,
            color: step > i ? 'var(--primary)' : 'var(--text-muted)',
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
          <h2 style={{ fontSize: '1.1rem', marginBottom: 16 }}>Select your procedure</h2>
          <div style={{ display: 'grid', gap: 12 }}>
            {Object.entries(procedures).map(([key, proc]) => (
              <button
                key={key}
                onClick={() => { setSelectedProc(key); setStep(2) }}
                className="card"
                style={{
                  width: '100%', textAlign: 'left', cursor: 'pointer',
                  border: selectedProc === key ? '2px solid var(--primary)' : '1px solid var(--border)',
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

      {/* Step 2: Select office */}
      {step === 2 && (
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 16 }}>Select preferred office</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10 }}>
            {Object.entries(offices).map(([key, name]) => (
              <button
                key={key}
                onClick={() => { setSelectedOffice(key); setStep(3) }}
                className="card"
                style={{
                  cursor: 'pointer', textAlign: 'center', padding: '14px 16px',
                  border: selectedOffice === key ? '2px solid var(--primary)' : '1px solid var(--border)',
                  fontSize: '0.9rem', fontWeight: 500,
                }}
              >
                {name}
              </button>
            ))}
          </div>
          <button onClick={() => setStep(1)} style={{
            marginTop: 16, background: 'none', border: 'none',
            color: 'var(--text-muted)', fontSize: '0.9rem', cursor: 'pointer',
          }}>
            Back
          </button>
        </div>
      )}

      {/* Step 3: Confirm */}
      {step === 3 && (
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 16 }}>Confirm your booking</h2>
          <div className="card" style={{ marginBottom: 24 }}>
            <div style={{ display: 'grid', gap: 12 }}>
              <div>
                <span style={{ fontWeight: 600 }}>Procedure:</span>{' '}
                {procedures[selectedProc]?.name}
              </div>
              <div>
                <span style={{ fontWeight: 600 }}>Office:</span>{' '}
                {offices[selectedOffice]}
              </div>
              <div>
                <span style={{ fontWeight: 600 }}>Profile:</span>{' '}
                {profile?.first_name} {profile?.last_name}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                We'll auto-fill the solicitud de estancia with your profile data
                and search for the next available appointment slot.
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <button
              onClick={handleBook}
              disabled={booking}
              className="btn btn-primary btn-lg"
            >
              {booking ? (
                <><Loader size={18} className="spin" /> Booking...</>
              ) : (
                <><CheckCircle size={18} /> Book Appointment</>
              )}
            </button>
            <button onClick={() => setStep(2)} className="btn btn-secondary">
              Back
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Result */}
      {step === 4 && result && (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          {result.status === 'pending' || result.status === 'in_progress' ? (
            <>
              <Loader size={48} color="var(--primary)" style={{ margin: '0 auto 16px' }} />
              <h2>Booking in progress</h2>
              <p style={{ color: 'var(--text-muted)', marginTop: 8 }}>
                We're filling out your forms and searching for available slots.
                This usually takes 1-2 minutes. Check your dashboard for updates.
              </p>
            </>
          ) : result.status === 'booked' ? (
            <>
              <CheckCircle size={48} color="var(--primary)" style={{ margin: '0 auto 16px' }} />
              <h2>Appointment Booked!</h2>
              {result.confirmation_code && (
                <p style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: 12 }}>
                  Confirmation: {result.confirmation_code}
                </p>
              )}
              <p style={{ color: 'var(--text-muted)', marginTop: 8 }}>
                {result.appointment_date} {result.appointment_time}
                {result.office_location && ` at ${result.office_location}`}
              </p>
            </>
          ) : (
            <>
              <AlertCircle size={48} color="var(--accent)" style={{ margin: '0 auto 16px' }} />
              <h2>Booking submitted</h2>
              <p style={{ color: 'var(--text-muted)', marginTop: 8 }}>
                Your request has been queued. Check the dashboard for status updates.
              </p>
            </>
          )}

          <a href="/dashboard" className="btn btn-primary" style={{ marginTop: 24 }}>
            Go to Dashboard
          </a>
        </div>
      )}
    </div>
  )
}
