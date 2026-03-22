import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register, getMe } from '../api'
import { Shield } from 'lucide-react'

export default function Register({ setUser }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      await register(email, password, fullName || null)
      const user = await getMe()
      setUser(user)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: '60px auto', padding: '0 20px' }}>
      <h1 style={{ fontSize: '1.8rem', marginBottom: 8 }}>Create your account</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
        Fill in your profile once, book appointments forever
      </p>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Full name (optional)</label>
          <input
            type="text"
            value={fullName}
            onChange={e => setFullName(e.target.value)}
            placeholder="Juan Perez"
          />
        </div>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
            autoFocus
            placeholder="you@example.com"
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            minLength={8}
            placeholder="Min 8 characters"
          />
        </div>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
          style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}
        >
          {loading ? 'Creating account...' : 'Sign up'}
        </button>
      </form>

      <div style={{
        display: 'flex', alignItems: 'center', gap: 6,
        justifyContent: 'center', marginTop: 16,
        fontSize: '0.8rem', color: 'var(--text-muted)',
      }}>
        <Shield size={14} />
        Your data is encrypted with AES-256
      </div>

      <p style={{ textAlign: 'center', marginTop: 16, fontSize: '0.9rem', color: 'var(--text-muted)' }}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  )
}
