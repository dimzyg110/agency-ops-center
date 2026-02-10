import { useState, useEffect } from 'react'
import { DROP_END_TIME } from '../data/products'

export default function DropBanner() {
  const [now, setNow] = useState(Date.now())

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [])

  const diff = Math.max(0, DROP_END_TIME - now)
  const d = Math.floor(diff / 86400000)
  const h = Math.floor((diff % 86400000) / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)

  return (
    <div
      className="fixed top-0 left-0 right-0 z-40 glass"
      style={{ borderBottom: '1px solid rgba(201,168,76,0.08)' }}
    >
      <div
        className="pulse-glow"
        style={{
          height: 40,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: "'Inter', sans-serif",
          fontWeight: 500,
          fontSize: 10,
          letterSpacing: '0.25em',
          color: '#C9A84C',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}
      >
        <span>
          NEXT DROP: THE PHANTOM COLLECTION — {d}D {String(h).padStart(2, '0')}H {String(m).padStart(2, '0')}M
        </span>
      </div>
    </div>
  )
}
