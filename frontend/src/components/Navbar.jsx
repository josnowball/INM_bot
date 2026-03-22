import { Link, useLocation } from 'react-router-dom'
import { logout, isLoggedIn } from '../api'
import { Shield, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Navbar({ user }) {
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const loggedIn = isLoggedIn()

  return (
    <nav style={{
      background: '#fff',
      borderBottom: '1px solid var(--border)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 64,
      }}>
        <Link to={loggedIn ? '/dashboard' : '/'} style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          fontWeight: 700,
          fontSize: '1.2rem',
          color: 'var(--primary)',
          textDecoration: 'none',
        }}>
          <span style={{ fontSize: '1.5rem' }}>🇲🇽</span>
          CitaFacil
        </Link>

        {/* Desktop nav */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}
          className="desktop-nav">
          {loggedIn ? (
            <>
              <Link to="/dashboard" style={{
                color: location.pathname === '/dashboard' ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: 500, fontSize: '0.9rem', textDecoration: 'none',
              }}>Dashboard</Link>
              <Link to="/profile" style={{
                color: location.pathname === '/profile' ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: 500, fontSize: '0.9rem', textDecoration: 'none',
              }}>Profile</Link>
              <Link to="/book/inm" style={{
                color: location.pathname === '/book/inm' ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: 500, fontSize: '0.9rem', textDecoration: 'none',
              }}>INM</Link>
              <Link to="/book/sre" style={{
                color: location.pathname === '/book/sre' ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: 500, fontSize: '0.9rem', textDecoration: 'none',
              }}>SRE</Link>
              <div style={{ width: 1, height: 24, background: 'var(--border)' }} />
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                {user?.email}
              </span>
              <button onClick={logout} className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: '0.85rem' }}>
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: '0.85rem' }}>
                Log in
              </Link>
              <Link to="/register" className="btn btn-primary" style={{ padding: '6px 14px', fontSize: '0.85rem' }}>
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
