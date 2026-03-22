import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getAppointments, getProfile, verifyEmail, resendVerification } from '../api'
import SecurityBadge from '../components/SecurityBadge'
import { Clock, CheckCircle, AlertCircle, Loader, FileText, Stamp } from 'lucide-react'

const STATUS_CONFIG = {
  pending: { label: 'Pending', class: 'badge-warning', icon: <Clock size={12} /> },
  in_progress: { label: 'In Progress', class: 'badge-info', icon: <Loader size={12} /> },
  booked: { label: 'Booked', class: 'badge-success', icon: <CheckCircle size={12} /> },
  failed: { label: 'Failed', class: 'badge-error', icon: <AlertCircle size={12} /> },
}

export default function Dashboard({ user }) {
  const [appointments, setAppointments] = useState([])
  const [profile, setProfile] = useState(null)
  const [verifyCode, setVerifyCode] = useState('')
  const [verifyMsg, setVerifyMsg] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getAppointments(), getProfile()])
      .then(([appts, prof]) => {
        setAppointments(appts)
        setProfile(prof)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  async function handleVerify(e) {
    e.preventDefault()
    try {
      await verifyEmail(verifyCode)
      setVerifyMsg('Email verified!')
      window.location.reload()
    } catch (err) {
      setVerifyMsg(err.message)
    }
  }

  if (loading) return <div className="container" style={{ padding: '40px 20px' }}>Loading...</div>

  return (
    <div className="container" style={{ padding: '40px 20px' }}>
      <h1 style={{ fontSize: '1.6rem', marginBottom: 24 }}>
        Welcome{user?.full_name ? `, ${user.full_name}` : ''}
      </h1>

      {/* Email verification banner */}
      {user && !user.email_verified && (
        <div className="alert alert-info" style={{ marginBottom: 24 }}>
          <strong>Verify your email</strong> to start booking appointments.
          <form onSubmit={handleVerify} style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <input
              type="text"
              placeholder="Enter 6-digit code"
              value={verifyCode}
              onChange={e => setVerifyCode(e.target.value)}
              style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border)', width: 160 }}
            />
            <button type="submit" className="btn btn-primary" style={{ padding: '6px 16px', fontSize: '0.85rem' }}>
              Verify
            </button>
            <button
              type="button"
              onClick={() => resendVerification().then(() => setVerifyMsg('Code resent!'))}
              className="btn btn-secondary"
              style={{ padding: '6px 16px', fontSize: '0.85rem' }}
            >
              Resend
            </button>
          </form>
          {verifyMsg && <p style={{ marginTop: 8, fontSize: '0.85rem' }}>{verifyMsg}</p>}
        </div>
      )}

      <SecurityBadge />

      {/* Profile completion */}
      {profile && profile.completion_pct < 100 && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontWeight: 600 }}>Profile completion</span>
            <span style={{ fontWeight: 700, color: 'var(--primary)' }}>{profile.completion_pct}%</span>
          </div>
          <div style={{ height: 8, background: '#e5e7eb', borderRadius: 4, overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${profile.completion_pct}%`,
              background: 'var(--primary)',
              borderRadius: 4,
              transition: 'width 0.3s',
            }} />
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 8 }}>
            Complete your profile to enable one-click booking.{' '}
            <Link to="/profile">Complete profile</Link>
          </p>
        </div>
      )}

      {/* Quick actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16, marginBottom: 32 }}>
        <Link to="/book/inm" className="card" style={{
          textDecoration: 'none', color: 'inherit',
          display: 'flex', alignItems: 'center', gap: 16,
          transition: 'box-shadow 0.15s',
        }}>
          <div style={{
            width: 48, height: 48, borderRadius: 12, background: '#ecfdf5',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <FileText size={24} color="var(--primary)" />
          </div>
          <div>
            <div style={{ fontWeight: 600 }}>Book INM Appointment</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Immigration procedures</div>
          </div>
        </Link>

        <Link to="/book/sre" className="card" style={{
          textDecoration: 'none', color: 'inherit',
          display: 'flex', alignItems: 'center', gap: 16,
          transition: 'box-shadow 0.15s',
        }}>
          <div style={{
            width: 48, height: 48, borderRadius: 12, background: '#fef2f2',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Stamp size={24} color="var(--accent)" />
          </div>
          <div>
            <div style={{ fontWeight: 600 }}>Book SRE Appointment</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Passports & visas</div>
          </div>
        </Link>
      </div>

      {/* Appointments list */}
      <h2 style={{ fontSize: '1.2rem', marginBottom: 16 }}>Recent Appointments</h2>
      {appointments.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
          <p>No appointments yet.</p>
          <p style={{ fontSize: '0.9rem', marginTop: 8 }}>
            Book your first appointment above to get started.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {appointments.map(a => {
            const st = STATUS_CONFIG[a.status] || STATUS_CONFIG.pending
            return (
              <div key={a.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: 4 }}>
                    {a.service.toUpperCase()} — {a.procedure_type.replace(/_/g, ' ')}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {a.office_location || 'Office TBD'} &middot; {new Date(a.created_at).toLocaleDateString()}
                  </div>
                  {a.confirmation_code && (
                    <div style={{ fontSize: '0.85rem', marginTop: 4 }}>
                      Confirmation: <strong>{a.confirmation_code}</strong>
                    </div>
                  )}
                  {a.error_message && (
                    <div style={{ fontSize: '0.85rem', color: '#991b1b', marginTop: 4 }}>
                      {a.error_message}
                    </div>
                  )}
                </div>
                <span className={`badge ${st.class}`}>
                  {st.icon} {st.label}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
