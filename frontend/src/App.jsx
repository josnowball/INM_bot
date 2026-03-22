import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { isLoggedIn, getMe } from './api'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import INMBooking from './pages/INMBooking'
import SREBooking from './pages/SREBooking'

function ProtectedRoute({ children, user }) {
  if (!isLoggedIn()) return <Navigate to="/login" />
  return children
}

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isLoggedIn()) {
      getMe()
        .then(setUser)
        .catch(() => {})
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <>
      <Navbar user={user} />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register setUser={setUser} />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute user={user}>
              <Dashboard user={user} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute user={user}>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/book/inm"
          element={
            <ProtectedRoute user={user}>
              <INMBooking />
            </ProtectedRoute>
          }
        />
        <Route
          path="/book/sre"
          element={
            <ProtectedRoute user={user}>
              <SREBooking />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  )
}
