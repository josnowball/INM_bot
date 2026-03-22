import { Link } from 'react-router-dom'
import { Shield, Zap, Clock, CheckCircle, Lock, Users } from 'lucide-react'
import SecurityBadge from '../components/SecurityBadge'

export default function Landing() {
  return (
    <div>
      {/* Hero */}
      <section style={{
        background: 'linear-gradient(135deg, var(--bg-dark) 0%, #1a2744 100%)',
        color: 'white',
        padding: '80px 20px',
        textAlign: 'center',
      }}>
        <div className="container">
          <h1 style={{ fontSize: '2.8rem', fontWeight: 700, marginBottom: 16, lineHeight: 1.2 }}>
            Book INM & SRE Appointments<br />
            <span style={{ color: '#00e68a' }}>In One Click</span>
          </h1>
          <p style={{ fontSize: '1.2rem', color: '#94a3b8', maxWidth: 600, margin: '0 auto 32px' }}>
            Stop wasting hours navigating government websites.
            Fill in your profile once, and we handle the rest.
          </p>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/register" className="btn btn-primary btn-lg" style={{ background: '#00e68a', color: '#0f1629' }}>
              <Zap size={20} />
              Get Started Free
            </Link>
            <a href="#how-it-works" className="btn btn-secondary btn-lg" style={{ borderColor: '#94a3b8', color: '#94a3b8' }}>
              How it works
            </a>
          </div>

          {/* Stats */}
          <div style={{
            display: 'flex', justifyContent: 'center', gap: 48,
            marginTop: 48, flexWrap: 'wrap',
          }}>
            {[
              { num: '2 min', label: 'Average booking time' },
              { num: '30+', label: 'INM & SRE procedures' },
              { num: '14', label: 'Office locations' },
            ].map(s => (
              <div key={s.label}>
                <div style={{ fontSize: '2rem', fontWeight: 700, color: '#00e68a' }}>{s.num}</div>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Services */}
      <section style={{ padding: '64px 20px' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: 8 }}>Services</h2>
          <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: 40 }}>
            Two government systems, one simple interface
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24 }}>
            <div className="card" style={{ borderLeft: '4px solid var(--primary)' }}>
              <h3 style={{ marginBottom: 8 }}>INM — Immigration</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 16 }}>
                Residencia temporal/permanente, cambio de condicion, regularization, and more.
                We auto-fill the solicitud de estancia correctly.
              </p>
              <ul style={{ listStyle: 'none', fontSize: '0.9rem' }}>
                {['Residencia Temporal', 'Residencia Permanente', 'Cambio de Condicion', 'Renovacion', 'Regularizacion'].map(p => (
                  <li key={p} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <CheckCircle size={16} color="var(--primary)" /> {p}
                  </li>
                ))}
              </ul>
              <Link to="/book/inm" className="btn btn-primary" style={{ marginTop: 16 }}>
                Book INM Appointment
              </Link>
            </div>

            <div className="card" style={{ borderLeft: '4px solid var(--accent)' }}>
              <h3 style={{ marginBottom: 8 }}>SRE — Passports & Visas</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 16 }}>
                Passport applications, renewals, visa exchanges, apostille,
                and more via MiConsulado. You provide your own login.
              </p>
              <ul style={{ listStyle: 'none', fontSize: '0.9rem' }}>
                {['Pasaporte (nuevo)', 'Pasaporte (renovacion)', 'Canje de Visa', 'Apostilla', 'Legalizacion'].map(p => (
                  <li key={p} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <CheckCircle size={16} color="var(--accent)" /> {p}
                  </li>
                ))}
              </ul>
              <Link to="/book/sre" className="btn btn-accent" style={{ marginTop: 16 }}>
                Book SRE Appointment
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" style={{ padding: '64px 20px', background: '#f8fafc' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: 40 }}>How it works</h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 32 }}>
            {[
              { icon: <Users size={32} color="var(--primary)" />, title: '1. Create your profile', desc: 'Fill in your personal data once. We encrypt and save it so you never have to re-enter it.' },
              { icon: <Zap size={32} color="var(--primary)" />, title: '2. Choose your service', desc: 'Pick INM or SRE, select your procedure type, and your preferred office location.' },
              { icon: <Clock size={32} color="var(--primary)" />, title: '3. We book it for you', desc: 'We auto-fill all the forms and find available appointment slots. You get a confirmation.' },
            ].map(step => (
              <div key={step.title} style={{ textAlign: 'center' }}>
                <div style={{
                  width: 64, height: 64, borderRadius: '50%', background: '#ecfdf5',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 16px',
                }}>
                  {step.icon}
                </div>
                <h3 style={{ marginBottom: 8 }}>{step.title}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security */}
      <section style={{ padding: '64px 20px' }}>
        <div className="container" style={{ maxWidth: 700 }}>
          <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: 8 }}>Your data is safe</h2>
          <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: 32 }}>
            We handle sensitive immigration data with bank-level security
          </p>

          <div style={{ display: 'grid', gap: 16 }}>
            {[
              { icon: <Lock size={20} />, title: 'AES-256-GCM Encryption', desc: 'Every personal field is encrypted at rest with a unique nonce. Even if the database were breached, your data is unreadable without the encryption key.' },
              { icon: <Shield size={20} />, title: 'Credentials never stored', desc: 'MiConsulado passwords are used once during the booking session and immediately discarded. We never write them to disk.' },
              { icon: <CheckCircle size={20} />, title: 'Minimal data collection', desc: 'We only collect what\'s needed for the appointment forms. No tracking, no analytics, no selling data.' },
            ].map(item => (
              <div key={item.title} className="card" style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 8, background: '#ecfdf5',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                  color: '#166534',
                }}>
                  {item.icon}
                </div>
                <div>
                  <h4 style={{ marginBottom: 4 }}>{item.title}</h4>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{
        background: 'var(--primary)',
        color: 'white',
        padding: '48px 20px',
        textAlign: 'center',
      }}>
        <div className="container">
          <h2 style={{ fontSize: '1.8rem', marginBottom: 12 }}>
            Ready to skip the bureaucracy?
          </h2>
          <p style={{ opacity: 0.8, marginBottom: 24 }}>
            Create your profile in 5 minutes, book appointments in seconds.
          </p>
          <Link to="/register" className="btn btn-lg" style={{ background: 'white', color: 'var(--primary)' }}>
            Sign up free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: '32px 20px', borderTop: '1px solid var(--border)', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          CitaFacil is not affiliated with INM or SRE. We are an independent service that helps you book appointments.
        </p>
      </footer>
    </div>
  )
}
