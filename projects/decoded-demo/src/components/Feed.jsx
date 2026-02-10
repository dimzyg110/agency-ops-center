import { useState, useEffect, useRef } from 'react'
import { products, DROP_END_TIME } from '../data/products'

function formatCount(n) {
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

function useCountdown(endTime) {
  const [now, setNow] = useState(Date.now())
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [])
  const diff = Math.max(0, endTime - now)
  const h = Math.floor(diff / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  const s = Math.floor((diff % 60000) / 1000)
  return { h, m, s }
}

// Gold sparkle particles near countdown
function Sparkles() {
  const [sparkles, setSparkles] = useState([])

  useEffect(() => {
    const id = setInterval(() => {
      setSparkles(prev => {
        const now = Date.now()
        const filtered = prev.filter(s => now - s.born < 1200)
        if (filtered.length < 3) {
          filtered.push({
            id: now + Math.random(),
            born: now,
            x: Math.random() * 100,
            y: Math.random() * 100,
            size: 2 + Math.random() * 3,
          })
        }
        return filtered
      })
    }, 400)
    return () => clearInterval(id)
  }, [])

  return (
    <>
      {sparkles.map(s => (
        <span
          key={s.id}
          style={{
            position: 'absolute',
            left: `${s.x}%`,
            top: `${s.y}%`,
            width: s.size,
            height: s.size,
            borderRadius: '50%',
            background: '#C9A84C',
            boxShadow: '0 0 4px #C9A84C, 0 0 8px rgba(201,168,76,0.5)',
            animation: 'sparkle-float 1.2s ease-out forwards',
            pointerEvents: 'none',
          }}
        />
      ))}
    </>
  )
}

// Fire burst particles on tap
function FireBurst({ trigger }) {
  const [particles, setParticles] = useState([])

  useEffect(() => {
    if (!trigger) return
    const newParticles = Array.from({ length: 6 }, (_, i) => ({
      id: Date.now() + i,
      angle: (i / 6) * 360,
      distance: 20 + Math.random() * 20,
    }))
    setParticles(newParticles)
    const timer = setTimeout(() => setParticles([]), 600)
    return () => clearTimeout(timer)
  }, [trigger])

  return (
    <>
      {particles.map(p => {
        const rad = (p.angle * Math.PI) / 180
        const tx = Math.cos(rad) * p.distance
        const ty = Math.sin(rad) * p.distance
        return (
          <span
            key={p.id}
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              width: 4,
              height: 4,
              marginLeft: -2,
              marginTop: -2,
              borderRadius: '50%',
              background: '#FF6B35',
              animation: 'fire-burst 0.5s ease-out forwards',
              transform: `translate(${tx}px, ${ty}px) scale(0)`,
              pointerEvents: 'none',
            }}
          />
        )
      })}
    </>
  )
}

function CheckIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0D0D0D" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline
        points="4 12 10 18 20 6"
        style={{
          strokeDasharray: 30,
          strokeDashoffset: 0,
          animation: 'draw-check 0.4s ease forwards',
        }}
      />
    </svg>
  )
}

function ChevronDown() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 2,
      animation: 'bounce-up 1.8s ease-in-out infinite',
    }}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F5F0E8" strokeWidth="1.5" strokeLinecap="round" opacity="0.5">
        <polyline points="6 9 12 15 18 9" />
      </svg>
      <span style={{
        fontSize: 9,
        letterSpacing: '0.2em',
        color: 'rgba(245,240,232,0.3)',
        textTransform: 'uppercase',
        fontFamily: "'Inter', sans-serif",
        fontWeight: 400,
      }}>
        Swipe
      </span>
    </div>
  )
}

function ProductCard({ product, isActive, isLast, onAddToVault }) {
  const { h, m, s } = useCountdown(DROP_END_TIME)
  const [fireCount, setFireCount] = useState(product.fireCount)
  const [skullCount, setSkullCount] = useState(product.skullCount)
  const [fireTrigger, setFireTrigger] = useState(0)
  const [skullActive, setSkullActive] = useState(false)
  const [fireActive, setFireActive] = useState(false)
  const [vaultState, setVaultState] = useState('idle')

  const handleFire = () => {
    if (fireActive) return
    setFireActive(true)
    setFireCount(c => c + 1)
    setFireTrigger(t => t + 1)
    setTimeout(() => setFireActive(false), 500)
  }

  const handleSkull = () => {
    if (skullActive) return
    setSkullActive(true)
    setSkullCount(c => c + 1)
    setTimeout(() => setSkullActive(false), 500)
  }

  const handleVault = () => {
    if (vaultState !== 'idle') return
    setVaultState('adding')
    onAddToVault?.(product)
    setTimeout(() => setVaultState('added'), 300)
    setTimeout(() => setVaultState('idle'), 1800)
  }

  return (
    <div
      className="feed-card relative w-full flex flex-col justify-end"
      style={{ background: product.gradient }}
    >
      <div className="gradient-overlay absolute inset-0 z-[1]" />

      {/* DECODED watermark */}
      <div style={{
        position: 'absolute',
        top: 56,
        left: 20,
        zIndex: 5,
        fontFamily: "'Inter', sans-serif",
        fontWeight: 900,
        fontSize: 11,
        letterSpacing: '0.35em',
        color: 'rgba(201,168,76,0.2)',
        textTransform: 'uppercase',
      }}>
        DECODED
      </div>

      {/* Right side actions */}
      <div style={{
        position: 'absolute',
        right: 16,
        bottom: '28%',
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 24,
      }}>
        {/* Fire */}
        <button
          onClick={handleFire}
          style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
            background: 'none', border: 'none', cursor: 'pointer', position: 'relative', padding: 0,
          }}
        >
          <span style={{
            fontSize: 28, display: 'block',
            animation: fireActive ? 'fire-pop 0.5s ease forwards' : 'none',
            filter: fireActive ? 'brightness(1.5)' : 'none',
            transition: 'filter 0.2s',
          }}>🔥</span>
          <FireBurst trigger={fireTrigger} />
          <span style={{
            fontSize: 11, color: '#F5F0E8',
            fontFamily: "'Inter', sans-serif", fontWeight: 600, letterSpacing: '0.02em',
          }}>{formatCount(fireCount)}</span>
        </button>

        {/* Skull */}
        <button
          onClick={handleSkull}
          style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
            background: 'none', border: 'none', cursor: 'pointer', padding: 0,
          }}
        >
          <span style={{
            fontSize: 26, display: 'block',
            animation: skullActive ? 'fire-pop 0.5s ease forwards' : 'none',
          }}>💀</span>
          <span style={{
            fontSize: 11, color: '#F5F0E8',
            fontFamily: "'Inter', sans-serif", fontWeight: 600, letterSpacing: '0.02em',
          }}>{formatCount(skullCount)}</span>
        </button>

        {/* Share */}
        <button style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
          background: 'none', border: 'none', cursor: 'pointer', padding: 0, opacity: 0.8,
        }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F5F0E8" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8" />
            <polyline points="16 6 12 2 8 6" />
            <line x1="12" y1="2" x2="12" y2="15" />
          </svg>
          <span style={{
            fontSize: 10, color: '#F5F0E8',
            fontFamily: "'Inter', sans-serif", fontWeight: 500, letterSpacing: '0.02em',
          }}>Share</span>
        </button>
      </div>

      {/* Bottom content */}
      <div
        className={isActive ? 'card-enter' : ''}
        style={{
          position: 'relative', zIndex: 5,
          padding: '0 24px 32px',
          display: 'flex', flexDirection: 'column',
        }}
      >
        {/* Tag */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
          <div style={{
            width: 6, height: 6, borderRadius: '50%', background: '#C9A84C',
            boxShadow: '0 0 6px rgba(201,168,76,0.6)',
          }} />
          <span style={{
            fontFamily: "'Inter', sans-serif", fontWeight: 500, fontSize: 11,
            letterSpacing: '0.2em', textTransform: 'uppercase', color: '#C9A84C',
          }}>{product.tag}</span>
        </div>

        {/* Name */}
        <h2 style={{
          fontFamily: "'Inter', sans-serif", fontWeight: 900,
          fontSize: 'clamp(32px, 9vw, 48px)', lineHeight: 1.0,
          letterSpacing: '-0.02em', color: '#F5F0E8', marginBottom: 8,
          textShadow: '0 2px 20px rgba(0,0,0,0.5)',
        }}>{product.name}</h2>

        {/* Price */}
        <div style={{
          fontFamily: "'Inter', sans-serif", fontWeight: 300,
          fontSize: 24, color: '#F5F0E8', letterSpacing: '0.02em', marginBottom: 16,
        }}>${product.price}</div>

        {/* Countdown */}
        <div style={{
          fontFamily: "'Inter', sans-serif", fontWeight: 600,
          fontSize: 14, color: '#C9A84C', letterSpacing: '0.15em',
          marginBottom: 20, display: 'flex', alignItems: 'center', gap: 4,
          position: 'relative', width: 'fit-content',
        }}>
          <Sparkles />
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>
            {String(h).padStart(2, '0')}:{String(m).padStart(2, '0')}:{String(s).padStart(2, '0')}
          </span>
          <span style={{ fontSize: 10, opacity: 0.6, marginLeft: 6, letterSpacing: '0.15em' }}>REMAINING</span>
        </div>

        {/* Add to Vault */}
        <button
          onClick={handleVault}
          style={{
            width: '100%', maxWidth: 320, height: 52,
            border: 'none', borderRadius: 6, cursor: 'pointer',
            fontFamily: "'Inter', sans-serif", fontWeight: 700,
            fontSize: 13, letterSpacing: '0.25em', textTransform: 'uppercase',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            background: '#C9A84C', color: '#0D0D0D',
            boxShadow: vaultState === 'adding'
              ? '0 0 0 0 rgba(201,168,76,0.6)'
              : '0 0 20px rgba(201,168,76,0.15), 0 0 60px rgba(201,168,76,0.05)',
            animation: vaultState === 'adding' ? 'vault-pulse 0.6s ease forwards' : 'none',
          }}
        >
          {vaultState === 'added' ? (
            <><CheckIcon /> <span>ADDED</span></>
          ) : (
            <span>ADD TO VAULT</span>
          )}
        </button>

        {/* Swipe or Roviq watermark */}
        {!isLast ? (
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: 20 }}>
            <ChevronDown />
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: 24 }}>
            <span style={{
              fontFamily: "'Inter', sans-serif", fontWeight: 300,
              fontSize: 10, letterSpacing: '0.15em',
              color: 'rgba(201,168,76,0.2)', textTransform: 'uppercase',
            }}>Built by Roviq</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Feed({ onAddToVault }) {
  const scrollRef = useRef(null)
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    const handleScroll = () => {
      const index = Math.round(el.scrollTop / el.clientHeight)
      setActiveIndex(index)
    }
    el.addEventListener('scroll', handleScroll, { passive: true })
    return () => el.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div
      ref={scrollRef}
      className="feed-scroll no-scrollbar"
      style={{ paddingTop: 40, paddingBottom: 68 }}
    >
      {products.map((product, index) => (
        <ProductCard
          key={product.id}
          product={product}
          isActive={activeIndex === index}
          isLast={index === products.length - 1}
          onAddToVault={onAddToVault}
        />
      ))}
    </div>
  )
}
