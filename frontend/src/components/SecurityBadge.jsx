import { Shield, Lock, Eye } from 'lucide-react'

export default function SecurityBadge() {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #f0fdf4, #ecfdf5)',
      border: '1px solid #bbf7d0',
      borderRadius: 'var(--radius)',
      padding: '20px 24px',
      marginBottom: 24,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <Shield size={20} color="#166534" />
        <span style={{ fontWeight: 600, color: '#166534' }}>Your data is protected</span>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.85rem', color: '#166534' }}>
          <Lock size={14} />
          AES-256 encryption at rest
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.85rem', color: '#166534' }}>
          <Eye size={14} />
          Credentials never stored
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.85rem', color: '#166534' }}>
          <Shield size={14} />
          HTTPS only
        </div>
      </div>
    </div>
  )
}
