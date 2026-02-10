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
    <div className="fixed top-0 left-0 right-0 z-40"
      style={{ paddingTop: 'env(safe-area-inset-top, 0px)' }}>
      <div style={{ height: 36, overflow: 'hidden', display: 'flex', alignItems: 'center', background: 'linear-gradient(180deg, rgba(13,13,13,0.85) 0%, rgba(13,13,13,0) 100%)' }}>
        <div style={{ display: 'flex', whiteSpace: 'nowrap', animation: 'ticker 24s linear infinite' }}>
          {[...Array(6)].map((_, i) => (
            <span key={i} className="pulse-glow gold-shimmer-text"
              style={{
                fontFamily: "'Inter', sans-serif", fontWeight: 600,
                fontSize: 9, letterSpacing: '0.3em',
                textTransform: 'uppercase', padding: '0 32px',
              }}>{text}</span>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ── GOLD DUST PARTICLES ── */

function GoldDust() {
  const particles = useMemo(() =>
    Array.from({ length: 6 }, (_, i) => ({
      id: i,
      left: 10 + Math.random() * 80,
      delay: Math.random() * 8,
      duration: 10 + Math.random() * 8,
      size: 1 + Math.random() * 1.5,
      opacity: 0.15 + Math.random() * 0.2,
    })), [])

  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 3 }}>
      {particles.map(p => (
        <div key={p.id} style={{
          position: 'absolute',
          left: `${p.left}%`,
          bottom: '-5%',
          width: p.size,
          height: p.size,
          borderRadius: '50%',
          background: '#C9A84C',
          boxShadow: `0 0 ${p.size * 3}px rgba(201,168,76,0.4)`,
          opacity: p.opacity,
          animation: `gold-float ${p.duration}s ease-in-out ${p.delay}s infinite`,
        }} />
      ))}
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
    const ps = Array.from({ length: 10 }, (_, i) => {
      const a = (i / 10) * 360, r = 18 + Math.random() * 22
      const rad = (a * Math.PI) / 180
      return { id: Date.now() + i, tx: Math.cos(rad) * r, ty: Math.sin(rad) * r, color: i % 3 === 0 ? '#FF6B35' : i % 3 === 1 ? '#C9A84C' : '#E8D48B', sz: 2.5 + Math.random() * 2.5 }
    })
    setParticles(ps)
    const t = setTimeout(() => setParticles([]), 600)
    return () => clearTimeout(t)
  }, [trigger])
  return <>
    {particles.map(p => (
      <span key={p.id} style={{
        position: 'absolute', left: '50%', top: '50%',
        width: p.sz, height: p.sz, marginLeft: -p.sz / 2, marginTop: -p.sz / 2,
        borderRadius: '50%', background: p.color, boxShadow: `0 0 8px ${p.color}`,
        '--burst-translate': `translate(${p.tx}px, ${p.ty}px)`,
        animation: 'fire-burst 0.55s ease-out forwards', pointerEvents: 'none',
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
        background: 'radial-gradient(circle, rgba(201,168,76,0.04) 0%, transparent 65%)',
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
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" strokeWidth="1.2" strokeLinecap="round" opacity="0.4" style={{ animation: 'chevron-fade 2.5s ease-in-out infinite' }}>
        <polyline points="18 15 12 9 6 15" />
      </svg>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" strokeWidth="1.2" strokeLinecap="round" opacity="0.25" style={{ animation: 'chevron-fade 2.5s ease-in-out infinite', animationDelay: '0.15s' }}>
        <polyline points="18 15 12 9 6 15" />
      </svg>
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
  const [videoLoaded, setVideoLoaded] = useState(false)

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
    setTimeout(() => setVaultState('idle'), 2800)
  }, [vaultState])

  const reveal = (delay) => ({
    opacity: isActive ? 1 : 0,
    transform: isActive ? 'translateY(0)' : 'translateY(22px)',
    transition: `opacity 0.6s cubic-bezier(0.16,1,0.3,1) ${delay}s, transform 0.6s cubic-bezier(0.16,1,0.3,1) ${delay}s`,
  })

  return (
    <div className="feed-card relative w-full flex flex-col justify-end" style={{ background: product.gradient }}>
      {/* Video background with Ken Burns */}
      {product.video && (
        <video
          autoPlay
          loop
          muted
          playsInline
          onLoadedData={() => setVideoLoaded(true)}
          className={videoLoaded && isActive ? 'video-zoom' : ''}
          style={{
            position: 'absolute', inset: 0, width: '100%', height: '100%',
            objectFit: 'cover', zIndex: 0,
            opacity: videoLoaded ? 0.9 : 0,
            transition: 'opacity 1.2s ease-in-out',
          }}
        >
          <source src={product.video} type="video/mp4" />
        </video>
      )}

      <AmbientShapes />
      <GoldDust />

      {/* Vignette */}
      <div className="vignette absolute inset-0 z-[1]" />
      {/* Gradient overlay */}
      <div className="gradient-overlay absolute inset-0 z-[2]" />

      {/* Brand mark — breathing animation */}
      <div className="brand-breathe" style={{
        position: 'absolute', top: 'calc(42px + env(safe-area-inset-top, 0px))', left: 22, zIndex: 5,
        fontFamily: "'Inter', sans-serif", fontWeight: 800, fontSize: 9,
        letterSpacing: '0.4em', color: 'rgba(201,168,76,0.18)', textTransform: 'uppercase',
      }}>DECODED</div>

      {/* ── RIGHT SIDE ACTIONS ── */}
      <div style={{
        position: 'absolute', right: 14, zIndex: 10,
        bottom: isLast ? '34%' : '30%',
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22,
        ...reveal(0.5),
      }}>
        {/* Fire */}
        <button onClick={handleFire} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, background: 'none', border: 'none', cursor: 'pointer', position: 'relative', padding: 0 }}>
          <div style={{
            width: 46, height: 46, borderRadius: '50%',
            background: fireActive ? 'rgba(201,168,76,0.15)' : 'rgba(245,240,232,0.05)',
            border: `1px solid ${fireActive ? 'rgba(201,168,76,0.3)' : 'rgba(245,240,232,0.08)'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'all 0.3s ease',
            backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)',
          }}>
            <span style={{ fontSize: 22, display: 'block', lineHeight: 1, animation: fireActive ? 'fire-pop 0.5s ease forwards' : 'none', filter: fireActive ? 'brightness(1.4) drop-shadow(0 0 8px rgba(201,168,76,0.5))' : 'none', transition: 'filter 0.2s' }}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill={fireActive ? '#C9A84C' : 'none'} stroke={fireActive ? '#C9A84C' : '#F5F0E8'} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ transition: 'all 0.3s' }}>
                <path d="M12 22c4.97 0 8-3.58 8-8 0-6-8-14-8-14S4 8 4 14c0 4.42 3.03 8 8 8z" />
                <path d="M12 22c2.21 0 4-1.79 4-4 0-3-4-7-4-7s-4 4-4 7c0 2.21 1.79 4 4 4z" opacity="0.5" />
              </svg>
            </span>
          </div>
          {/* Ring expand on tap */}
          {fireActive && <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '2px solid rgba(201,168,76,0.4)', animation: 'ring-expand 0.5s ease-out forwards', pointerEvents: 'none' }} />}
          <FireBurst trigger={fireTrigger} />
          <span style={{ fontSize: 10, color: fireActive ? '#C9A84C' : 'rgba(245,240,232,0.6)', fontFamily: "'Inter', sans-serif", fontWeight: 600, fontVariantNumeric: 'tabular-nums', transition: 'color 0.2s', textShadow: '0 1px 4px rgba(0,0,0,0.5)' }}>{fmtK(fireCount)}</span>
        </button>

        {/* Skull */}
        <button onClick={handleSkull} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, background: 'none', border: 'none', cursor: 'pointer', padding: 0, position: 'relative' }}>
          <div style={{
            width: 46, height: 46, borderRadius: '50%',
            background: skullActive ? 'rgba(245,240,232,0.1)' : 'rgba(245,240,232,0.05)',
            border: `1px solid ${skullActive ? 'rgba(245,240,232,0.2)' : 'rgba(245,240,232,0.08)'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'all 0.3s ease',
            backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)',
          }}>
            <span style={{ fontSize: 20, display: 'block', lineHeight: 1, animation: skullActive ? 'fire-pop 0.5s ease forwards' : 'none' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill={skullActive ? '#F5F0E8' : 'none'} stroke="#F5F0E8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ transition: 'all 0.3s' }}>
                <circle cx="12" cy="10" r="8" />
                <path d="M8 16v4h2l1-1 1 1h2v-4" />
                <circle cx="9" cy="10" r="1.5" fill="#F5F0E8" />
                <circle cx="15" cy="10" r="1.5" fill="#F5F0E8" />
              </svg>
            </span>
          </div>
          {skullActive && <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '2px solid rgba(245,240,232,0.2)', animation: 'ring-expand 0.5s ease-out forwards', pointerEvents: 'none' }} />}
          <span style={{ fontSize: 10, color: 'rgba(245,240,232,0.6)', fontFamily: "'Inter', sans-serif", fontWeight: 600, fontVariantNumeric: 'tabular-nums', textShadow: '0 1px 4px rgba(0,0,0,0.5)' }}>{fmtK(skullCount)}</span>
        </button>

        {/* Share */}
        <button style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
          <div style={{
            width: 46, height: 46, borderRadius: '50%',
            background: 'rgba(245,240,232,0.05)',
            border: '1px solid rgba(245,240,232,0.08)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F5F0E8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.7">
              <path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8" />
              <polyline points="16 6 12 2 8 6" />
              <line x1="12" y1="2" x2="12" y2="15" />
            </svg>
          </div>
          <span style={{ fontSize: 10, color: 'rgba(245,240,232,0.4)', fontFamily: "'Inter', sans-serif", fontWeight: 500, textShadow: '0 1px 4px rgba(0,0,0,0.5)' }}>Share</span>
        </button>
      </div>

      {/* ── BOTTOM CONTENT ── */}
      <div style={{ position: 'relative', zIndex: 5, padding: '0 22px 28px', maxWidth: 380 }}>

        {/* Scarcity tag */}
        <div style={{ ...reveal(0.08), marginBottom: 14 }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 7,
            background: 'rgba(201,168,76,0.06)', border: '1px solid rgba(201,168,76,0.12)',
            borderRadius: 100, padding: '5px 14px 5px 10px',
            backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)',
            animation: 'tag-border-shimmer 3s ease-in-out infinite',
          }}>
            <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#C9A84C', animation: 'dot-pulse 2s ease-in-out infinite', flexShrink: 0 }} />
            <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 500, fontSize: 9, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#C9A84C' }}>{product.tag}</span>
          </span>
        </div>

        {/* Product name */}
        <h2 style={{
          ...reveal(0.16),
          fontFamily: "'Inter', sans-serif", fontWeight: 900,
          fontSize: 'clamp(38px, 11vw, 56px)', lineHeight: 0.92,
          letterSpacing: '-0.035em', color: '#F5F0E8',
          textShadow: '0 2px 30px rgba(0,0,0,0.6), 0 0 60px rgba(0,0,0,0.3)',
          whiteSpace: 'pre-line', marginBottom: product.subtitle ? 4 : 6,
        }}>{product.name}</h2>

        {/* Subtitle */}
        {product.subtitle && (
          <div style={{
            ...reveal(0.2),
            fontFamily: "'Inter', sans-serif", fontWeight: 300, fontSize: 13,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            color: 'rgba(245,240,232,0.35)', marginBottom: 6,
          }}>{product.subtitle}</div>
        )}

        {/* Gold divider */}
        <div className="gold-divider" style={{ ...reveal(0.22), width: 60, marginBottom: 12 }} />

        {/* Price */}
        <div style={{
          ...reveal(0.26),
          fontFamily: "'Inter', sans-serif", fontWeight: 200, fontSize: 30,
          color: '#F5F0E8', letterSpacing: '0.02em', marginBottom: 16,
          textShadow: '0 1px 20px rgba(0,0,0,0.4)',
        }}>
          <span style={{ fontSize: 16, opacity: 0.4, marginRight: 2, fontWeight: 300 }}>$</span>{product.price}
          <span style={{ fontSize: 12, opacity: 0.25, marginLeft: 6, fontWeight: 400, letterSpacing: '0.1em' }}>USD</span>
        </div>

        {/* Countdown */}
        <div style={{ ...reveal(0.32), marginBottom: 22, display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ display: 'flex', gap: 4, position: 'relative' }}>
            <Sparkles />
            {[{ val: pad(h), label: 'HR' }, { val: pad(m), label: 'MIN' }, { val: pad(s), label: 'SEC' }].map((unit, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                {i > 0 && <span style={{ color: 'rgba(201,168,76,0.25)', fontSize: 16, fontFamily: "'Inter', sans-serif", fontWeight: 200 }}>:</span>}
                <div style={{
                  background: 'rgba(201,168,76,0.06)', border: '1px solid rgba(201,168,76,0.1)',
                  borderRadius: 6, padding: '4px 8px', minWidth: 38, textAlign: 'center',
                  backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)',
                }}>
                  <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 700, fontSize: 14, color: '#C9A84C', fontVariantNumeric: 'tabular-nums', letterSpacing: '0.06em' }}>{unit.val}</span>
                </div>
              </div>
            ))}
          </div>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400, fontSize: 8, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'rgba(245,240,232,0.2)' }}>{expired ? 'EXPIRED' : 'LEFT'}</span>
        </div>

        {/* ADD TO VAULT — 3D Glass */}
        <div style={reveal(0.38)}>
          <button onClick={handleVault} style={{
            position: 'relative', width: '100%', maxWidth: 340, height: 54,
            border: vaultState === 'done' ? '1px solid rgba(201,168,76,0.35)' : '1px solid rgba(245,240,232,0.12)',
            borderRadius: 14, cursor: 'pointer',
            fontFamily: "'Inter', sans-serif", fontWeight: 700, fontSize: 12,
            letterSpacing: '0.24em', textTransform: 'uppercase',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
            transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)', overflow: 'hidden',
            background: vaultState === 'done'
              ? 'rgba(201,168,76,0.15)'
              : 'rgba(245,240,232,0.06)',
            backdropFilter: 'blur(20px) saturate(1.3)',
            WebkitBackdropFilter: 'blur(20px) saturate(1.3)',
            color: vaultState === 'done' ? '#C9A84C' : '#F5F0E8',
            animation: vaultState === 'pulse' ? 'glass-vault-press 0.55s ease forwards'
              : vaultState === 'done' ? 'glass-confirmed-glow 2s ease-in-out infinite'
              : 'glass-glow-breathe 3.5s ease-in-out infinite',
            transform: vaultState === 'pulse' ? 'scale(0.96) translateY(1px)' : 'scale(1)',
          }}>
            {/* Top highlight edge — polished glass catch */}
            <span style={{
              position: 'absolute', top: 0, left: '10%', right: '10%', height: 1,
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.25), rgba(255,255,255,0.35), rgba(255,255,255,0.25), transparent)',
              borderRadius: '0 0 50% 50%',
              pointerEvents: 'none',
            }} />
            {/* Inner top glow — glass depth */}
            <span style={{
              position: 'absolute', top: 0, left: 0, right: 0, height: '50%',
              background: 'linear-gradient(180deg, rgba(255,255,255,0.08) 0%, transparent 100%)',
              borderRadius: '14px 14px 50% 50%',
              pointerEvents: 'none',
            }} />
            {/* Refraction drift */}
            <span style={{
              position: 'absolute', top: '8%', left: '15%', width: '40%', height: '35%',
              background: 'radial-gradient(ellipse, rgba(255,255,255,0.06) 0%, transparent 70%)',
              borderRadius: '50%', filter: 'blur(6px)',
              animation: 'glass-refraction-drift 6s ease-in-out infinite',
              pointerEvents: 'none',
            }} />
            {/* Glass shine sweep */}
            <span style={{
              position: 'absolute', top: 0, left: 0, width: '35%', height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), rgba(255,255,255,0.06), transparent)',
              animation: 'glass-shine-sweep 4s ease-in-out infinite', animationDelay: '1.5s',
              pointerEvents: 'none',
            }} />
            {/* Content */}
            <span style={{ position: 'relative', zIndex: 2, display: 'flex', alignItems: 'center', gap: 10 }}>
              {vaultState === 'done' ? (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="4 12 10 18 20 6" style={{ strokeDasharray: 30, strokeDashoffset: 0, animation: 'draw-check 0.35s ease forwards' }} />
                  </svg>
                  <span>In Your Vault</span>
                </>
              ) : (
                <span>Add to Vault</span>
              )}
            </span>
          </button>
        </div>

        {/* Swipe / Roviq */}
        <div style={{ ...reveal(0.44), display: 'flex', justifyContent: 'center', marginTop: 16 }}>
          {isLast ? (
            <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 300, fontSize: 8, letterSpacing: '0.25em', color: 'rgba(201,168,76,0.12)', textTransform: 'uppercase' }}>Built by Roviq</span>
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
      <div ref={scrollRef} className="feed-scroll no-scrollbar">
        {products.map((product, i) => (
          <ProductCard key={product.id} product={product} isActive={activeIndex === i} isLast={i === products.length - 1} />
        ))}
      </div>
    </>
  )
}
