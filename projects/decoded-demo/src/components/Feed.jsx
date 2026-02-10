import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { products } from '../data/products'

const pad = n => String(n).padStart(2, '0')
const fmtK = n => n >= 1000 ? (n / 1000).toFixed(1) + 'K' : String(n)

function useCountdown(endTime) {
  const [now, setNow] = useState(Date.now())
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [])
  const d = Math.max(0, endTime - now)
  return {
    h: Math.floor(d / 3600000),
    m: Math.floor((d % 3600000) / 60000),
    s: Math.floor((d % 60000) / 1000),
    expired: d <= 0,
  }
}

/* ── DROP BANNER ── */

function DropBanner() {
  const end = useMemo(() => Date.now() + 3 * 86400000 + 14 * 3600000, [])
  const { h, m } = useCountdown(end)
  const days = Math.floor(Math.max(0, end - Date.now()) / 86400000)
  const text = `◈  NEXT DROP: DECODED NOIR — ${days}D ${pad(h % 24)}H ${pad(m)}M  ◈`

  return (
    <div className="fixed top-0 left-0 right-0 z-40 glass"
      style={{ borderBottom: '1px solid rgba(201,168,76,0.06)' }}>
      <div style={{ height: 44, overflow: 'hidden', display: 'flex', alignItems: 'center' }}>
        <div style={{ display: 'flex', whiteSpace: 'nowrap', animation: 'ticker 24s linear infinite' }}>
          {[...Array(6)].map((_, i) => (
            <span key={i} className="pulse-glow gold-shimmer-text"
              style={{
                fontFamily: "'Inter', sans-serif", fontWeight: 600,
                fontSize: 10, letterSpacing: '0.28em',
                textTransform: 'uppercase', padding: '0 32px',
              }}>{text}</span>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ── SPARKLES ── */

function Sparkles() {
  const [sparkles, setSparkles] = useState([])
  useEffect(() => {
    const id = setInterval(() => {
      setSparkles(prev => {
        const now = Date.now()
        const live = prev.filter(s => now - s.born < 1100)
        if (live.length < 3) {
          live.push({ id: now + Math.random(), born: now, x: Math.random() * 110 - 5, y: Math.random() * 110 - 5, sz: 2 + Math.random() * 2.5 })
        }
        return live
      })
    }, 350)
    return () => clearInterval(id)
  }, [])
  return <>
    {sparkles.map(s => (
      <span key={s.id} style={{
        position: 'absolute', left: `${s.x}%`, top: `${s.y}%`,
        width: s.sz, height: s.sz, borderRadius: '50%', background: '#C9A84C',
        boxShadow: '0 0 4px #C9A84C, 0 0 10px rgba(201,168,76,0.4)',
        animation: 'sparkle-float 1.1s ease-out forwards', pointerEvents: 'none',
      }} />
    ))}
  </>
}

/* ── FIRE BURST ── */

function FireBurst({ trigger }) {
  const [particles, setParticles] = useState([])
  useEffect(() => {
    if (!trigger) return
    const ps = Array.from({ length: 8 }, (_, i) => {
      const a = (i / 8) * 360, r = 18 + Math.random() * 18
      const rad = (a * Math.PI) / 180
      return { id: Date.now() + i, tx: Math.cos(rad) * r, ty: Math.sin(rad) * r, color: i % 2 === 0 ? '#FF6B35' : '#C9A84C', sz: 3 + Math.random() * 2 }
    })
    setParticles(ps)
    const t = setTimeout(() => setParticles([]), 550)
    return () => clearTimeout(t)
  }, [trigger])
  return <>
    {particles.map(p => (
      <span key={p.id} style={{
        position: 'absolute', left: '50%', top: '50%',
        width: p.sz, height: p.sz, marginLeft: -p.sz / 2, marginTop: -p.sz / 2,
        borderRadius: '50%', background: p.color, boxShadow: `0 0 6px ${p.color}`,
        '--burst-translate': `translate(${p.tx}px, ${p.ty}px)`,
        animation: 'fire-burst 0.5s ease-out forwards', pointerEvents: 'none',
      }} />
    ))}
  </>
}

/* ── AMBIENT SHAPES ── */

function AmbientShapes() {
  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none' }}>
      <div style={{
        position: 'absolute', width: '70vw', height: '70vw', maxWidth: 400, maxHeight: 400,
        bottom: '10%', left: '-15%', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(201,168,76,0.045) 0%, transparent 65%)',
        filter: 'blur(50px)', animation: 'ambient-float 18s ease-in-out infinite',
      }} />
      <div style={{
        position: 'absolute', width: '50vw', height: '50vw', maxWidth: 300, maxHeight: 300,
        top: '5%', right: '-10%', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(245,240,232,0.02) 0%, transparent 60%)',
        filter: 'blur(60px)', animation: 'ambient-float 22s ease-in-out infinite reverse',
        animationDelay: '-6s',
      }} />
    </div>
  )
}

/* ── SWIPE INDICATOR ── */

function SwipeUp() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, animation: 'bounce-up 2s ease-in-out infinite' }}>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F5F0E8" strokeWidth="1.5" strokeLinecap="round" opacity="0.5">
        <polyline points="18 15 12 9 6 15" />
      </svg>
      <span style={{ fontSize: 8, letterSpacing: '0.25em', color: 'rgba(245,240,232,0.25)', textTransform: 'uppercase', fontFamily: "'Inter', sans-serif", fontWeight: 400 }}>Swipe</span>
    </div>
  )
}

/* ══════════════════════════════════════════════
   PRODUCT CARD
   ══════════════════════════════════════════════ */

function ProductCard({ product, isActive, isLast }) {
  const { h, m, s, expired } = useCountdown(product.dropEnd)
  const [fireCount, setFireCount] = useState(product.fireCount)
  const [skullCount, setSkullCount] = useState(product.skullCount)
  const [fireTrigger, setFireTrigger] = useState(0)
  const [fireActive, setFireActive] = useState(false)
  const [skullActive, setSkullActive] = useState(false)
  const [vaultState, setVaultState] = useState('idle')

  const handleFire = useCallback(() => {
    if (fireActive) return
    setFireActive(true); setFireCount(c => c + 1); setFireTrigger(t => t + 1)
    setTimeout(() => setFireActive(false), 500)
  }, [fireActive])

  const handleSkull = useCallback(() => {
    if (skullActive) return
    setSkullActive(true); setSkullCount(c => c + 1)
    setTimeout(() => setSkullActive(false), 500)
  }, [skullActive])

  const handleVault = useCallback(() => {
    if (vaultState !== 'idle') return
    setVaultState('pulse')
    setTimeout(() => setVaultState('done'), 350)
    setTimeout(() => setVaultState('idle'), 2200)
  }, [vaultState])

  const reveal = (delay) => ({
    opacity: isActive ? 1 : 0,
    transform: isActive ? 'translateY(0)' : 'translateY(18px)',
    transition: `opacity 0.5s cubic-bezier(0.16,1,0.3,1) ${delay}s, transform 0.5s cubic-bezier(0.16,1,0.3,1) ${delay}s`,
  })

  return (
    <div className="feed-card relative w-full flex flex-col justify-end" style={{ background: product.gradient }}>
      {/* Video background */}
      {product.video && (
        <video
          autoPlay
          loop
          muted
          playsInline
          style={{
            position: 'absolute', inset: 0, width: '100%', height: '100%',
            objectFit: 'cover', zIndex: 0, opacity: 0.85,
          }}
        >
          <source src={product.video} type="video/mp4" />
        </video>
      )}
      <AmbientShapes />
      <div className="gradient-overlay absolute inset-0 z-[1]" />

      {/* Brand mark */}
      <div style={{
        position: 'absolute', top: 20, left: 22, zIndex: 5,
        fontFamily: "'Inter', sans-serif", fontWeight: 800, fontSize: 10,
        letterSpacing: '0.4em', color: 'rgba(201,168,76,0.18)', textTransform: 'uppercase',
      }}>DECODED</div>

      {/* ── RIGHT SIDE ACTIONS ── */}
      <div style={{
        position: 'absolute', right: 14, zIndex: 10,
        bottom: isLast ? '34%' : '30%',
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22,
        ...reveal(0.45),
      }}>
        {/* Fire */}
        <button onClick={handleFire} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, background: 'none', border: 'none', cursor: 'pointer', position: 'relative', padding: 0 }}>
          <div style={{
            width: 44, height: 44, borderRadius: '50%',
            background: fireActive ? 'rgba(201,168,76,0.12)' : 'rgba(245,240,232,0.06)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'background 0.25s',
          }}>
            <span style={{ fontSize: 24, display: 'block', lineHeight: 1, animation: fireActive ? 'fire-pop 0.5s ease forwards' : 'none', filter: fireActive ? 'brightness(1.4)' : 'none', transition: 'filter 0.2s' }}>🔥</span>
          </div>
          <FireBurst trigger={fireTrigger} />
          <span style={{ fontSize: 10, color: fireActive ? '#C9A84C' : 'rgba(245,240,232,0.7)', fontFamily: "'Inter', sans-serif", fontWeight: 600, fontVariantNumeric: 'tabular-nums', transition: 'color 0.2s' }}>{fmtK(fireCount)}</span>
        </button>

        {/* Skull */}
        <button onClick={handleSkull} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
          <div style={{
            width: 44, height: 44, borderRadius: '50%',
            background: skullActive ? 'rgba(245,240,232,0.1)' : 'rgba(245,240,232,0.06)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'background 0.25s',
          }}>
            <span style={{ fontSize: 22, display: 'block', lineHeight: 1, animation: skullActive ? 'fire-pop 0.5s ease forwards' : 'none' }}>💀</span>
          </div>
          <span style={{ fontSize: 10, color: 'rgba(245,240,232,0.7)', fontFamily: "'Inter', sans-serif", fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>{fmtK(skullCount)}</span>
        </button>

        {/* Share */}
        <button style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
          <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'rgba(245,240,232,0.06)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F5F0E8" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" opacity="0.8">
              <path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8" />
              <polyline points="16 6 12 2 8 6" />
              <line x1="12" y1="2" x2="12" y2="15" />
            </svg>
          </div>
          <span style={{ fontSize: 10, color: 'rgba(245,240,232,0.5)', fontFamily: "'Inter', sans-serif", fontWeight: 500 }}>Share</span>
        </button>
      </div>

      {/* ── BOTTOM CONTENT ── */}
      <div style={{ position: 'relative', zIndex: 5, padding: '0 22px 28px', maxWidth: 380 }}>

        {/* Scarcity tag */}
        <div style={{ ...reveal(0.08), marginBottom: 14 }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 7,
            background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.12)',
            borderRadius: 100, padding: '5px 14px 5px 10px',
          }}>
            <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#C9A84C', animation: 'dot-pulse 2s ease-in-out infinite', flexShrink: 0 }} />
            <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 500, fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: '#C9A84C' }}>{product.tag}</span>
          </span>
        </div>

        {/* Product name */}
        <h2 style={{
          ...reveal(0.16),
          fontFamily: "'Inter', sans-serif", fontWeight: 900,
          fontSize: 'clamp(36px, 10vw, 52px)', lineHeight: 0.95,
          letterSpacing: '-0.03em', color: '#F5F0E8',
          textShadow: '0 2px 30px rgba(0,0,0,0.6)',
          whiteSpace: 'pre-line', marginBottom: product.subtitle ? 4 : 10,
        }}>{product.name}</h2>

        {/* Subtitle */}
        {product.subtitle && (
          <div style={{
            ...reveal(0.2),
            fontFamily: "'Inter', sans-serif", fontWeight: 300, fontSize: 14,
            letterSpacing: '0.2em', textTransform: 'uppercase',
            color: 'rgba(245,240,232,0.4)', marginBottom: 10,
          }}>{product.subtitle}</div>
        )}

        {/* Price */}
        <div style={{
          ...reveal(0.24),
          fontFamily: "'Inter', sans-serif", fontWeight: 300, fontSize: 28,
          color: '#F5F0E8', letterSpacing: '0.01em', marginBottom: 16,
        }}>
          <span style={{ fontSize: 18, opacity: 0.5, marginRight: 2 }}>$</span>{product.price}
        </div>

        {/* Countdown */}
        <div style={{ ...reveal(0.3), marginBottom: 22, display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ display: 'flex', gap: 4, position: 'relative' }}>
            <Sparkles />
            {[{ val: pad(h), label: 'HR' }, { val: pad(m), label: 'MIN' }, { val: pad(s), label: 'SEC' }].map((unit, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                {i > 0 && <span style={{ color: 'rgba(201,168,76,0.35)', fontSize: 16, fontFamily: "'Inter', sans-serif", fontWeight: 300 }}>:</span>}
                <div style={{
                  background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.1)',
                  borderRadius: 6, padding: '4px 8px', minWidth: 38, textAlign: 'center',
                }}>
                  <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 700, fontSize: 15, color: '#C9A84C', fontVariantNumeric: 'tabular-nums', letterSpacing: '0.05em' }}>{unit.val}</span>
                </div>
              </div>
            ))}
          </div>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400, fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'rgba(245,240,232,0.3)' }}>{expired ? 'EXPIRED' : 'LEFT'}</span>
        </div>

        {/* ADD TO VAULT */}
        <div style={reveal(0.36)}>
          <button onClick={handleVault} style={{
            position: 'relative', width: '100%', maxWidth: 340, height: 54,
            border: 'none', borderRadius: 8, cursor: 'pointer',
            fontFamily: "'Inter', sans-serif", fontWeight: 700, fontSize: 13,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)', overflow: 'hidden',
            background: vaultState === 'done' ? 'linear-gradient(135deg, #A8893B, #C9A84C)' : 'linear-gradient(135deg, #C9A84C 0%, #D4B96A 100%)',
            color: '#0D0D0D',
            boxShadow: '0 4px 24px rgba(201,168,76,0.2), 0 1px 4px rgba(201,168,76,0.15)',
            animation: vaultState === 'pulse' ? 'vault-pulse 0.65s ease forwards' : 'none',
            transform: vaultState === 'pulse' ? 'scale(0.97)' : 'scale(1)',
          }}>
            <span style={{
              position: 'absolute', top: 0, left: 0, width: '40%', height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent)',
              animation: 'btn-shine 3s ease-in-out infinite', animationDelay: '1s', pointerEvents: 'none',
            }} />
            {vaultState === 'done' ? (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0D0D0D" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="4 12 10 18 20 6" style={{ strokeDasharray: 30, strokeDashoffset: 0, animation: 'draw-check 0.35s ease forwards' }} />
                </svg>
                <span>Added to Vault</span>
              </>
            ) : (
              <span>Add to Vault</span>
            )}
          </button>
        </div>

        {/* Swipe / Roviq */}
        <div style={{ ...reveal(0.42), display: 'flex', justifyContent: 'center', marginTop: 18 }}>
          {isLast ? (
            <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 300, fontSize: 9, letterSpacing: '0.2em', color: 'rgba(201,168,76,0.15)', textTransform: 'uppercase' }}>Built by Roviq</span>
          ) : (
            <SwipeUp />
          )}
        </div>
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════
   FEED — the single exported screen
   ══════════════════════════════════════════════ */

export default function Feed() {
  const scrollRef = useRef(null)
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    const onScroll = () => {
      const cardH = el.firstElementChild?.offsetHeight || el.clientHeight
      setActiveIndex(Math.round(el.scrollTop / cardH))
    }
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => el.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <>
      <DropBanner />
      <div ref={scrollRef} className="feed-scroll no-scrollbar" style={{ paddingTop: 44 }}>
        {products.map((product, i) => (
          <ProductCard key={product.id} product={product} isActive={activeIndex === i} isLast={i === products.length - 1} />
        ))}
      </div>
    </>
  )
}
