import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { products } from '../data/products'
import FilmNoise from './FilmNoise'
import GoldLiquidFill from './GoldLiquidFill'
import HolographicCard from './HolographicCard'

const pad = n => String(n).padStart(2, '0')
const fmtK = n => n >= 1000 ? (n / 1000).toFixed(1) + 'K' : String(n)

const CIPHER_CHARS = '▓█░▒◆◇▲△●○■□╳⬡⬢'

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

  return (
    <div className="fixed top-0 left-0 right-0 z-40"
      style={{ paddingTop: 'env(safe-area-inset-top, 0px)' }}>
      <div style={{
        height: 36,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#0D0D0D',
      }}>
        <span style={{
          fontFamily: "'Inter', sans-serif",
          fontWeight: 500,
          fontSize: 10,
          letterSpacing: '0.25em',
          color: '#C9A84C',
          opacity: 0.5,
          textTransform: 'uppercase',
        }}>
          DECODED NOIR — DROPS IN {days}D {pad(h % 24)}H
        </span>
      </div>
    </div>
  )
}

/* ── FIRE BURST ── */

function FireBurst({ trigger }) {
  const [particles, setParticles] = useState([])
  useEffect(() => {
    if (!trigger) return
    const ps = Array.from({ length: 10 }, (_, i) => {
      const a = (i / 10) * 360, r = 18 + Math.random() * 22
      const rad = (a * Math.PI) / 180
      return { id: Date.now() + i, tx: Math.cos(rad) * r, ty: Math.sin(rad) * r, color: i % 3 === 0 ? '#D4A03C' : i % 3 === 1 ? '#C9A84C' : '#E8D48B', sz: 2.5 + Math.random() * 2.5 }
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

/* ── SIZE SELECTOR ── */

function SizeSelector({ selectedSize, onSelectSize }) {
  const sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
  return (
    <div style={{ display: 'flex', gap: 6, marginBottom: 14 }}>
      {sizes.map(size => (
        <button
          key={size}
          onClick={() => onSelectSize(size)}
          style={{
            background: 'rgba(245,240,232,0.06)',
            border: `1px solid ${selectedSize === size ? 'rgba(245,240,232,0.4)' : 'rgba(245,240,232,0.1)'}`,
            borderRadius: 6,
            padding: '4px 10px',
            fontFamily: "'Inter', sans-serif",
            fontWeight: 500,
            fontSize: 10,
            letterSpacing: '0.06em',
            color: selectedSize === size ? 'rgba(245,240,232,0.9)' : 'rgba(245,240,232,0.5)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
          }}
        >
          {size}
        </button>
      ))}
    </div>
  )
}

/* ── CIPHER TEXT HOOK ── */

function useCipherReveal(originalText) {
  const [cipherActive, setCipherActive] = useState(false)
  const [cipherText, setCipherText] = useState(null)
  const [cipherFlash, setCipherFlash] = useState(false)
  const [goldPulse, setGoldPulse] = useState(false)
  const [resolvedGoldIndices, setResolvedGoldIndices] = useState(new Set())
  const lastTapRef = useRef(0)
  const cooldownRef = useRef(false)
  const intervalRef = useRef(null)

  const cleanText = originalText.replace(/\n/g, '\n')
  const chars = [...cleanText]

  const triggerCipher = useCallback(() => {
    if (cooldownRef.current || cipherActive) return
    cooldownRef.current = true
    setCipherActive(true)
    setCipherFlash(true)
    setTimeout(() => setCipherFlash(false), 200)

    const resolved = new Set()
    const goldSet = new Set()
    setResolvedGoldIndices(new Set())

    // Phase 1: All characters scramble (0-600ms)
    intervalRef.current = setInterval(() => {
      const scrambled = chars.map((ch, i) => {
        if (ch === '\n' || ch === ' ') return ch
        if (resolved.has(i)) return chars[i]
        return CIPHER_CHARS[Math.floor(Math.random() * CIPHER_CHARS.length)]
      })
      setCipherText(scrambled.join(''))
    }, 50)

    // Phase 2: Decode left-to-right starting at 600ms
    const nonSpaceIndices = chars.map((ch, i) => (ch !== '\n' && ch !== ' ') ? i : -1).filter(i => i >= 0)
    let decodeIdx = 0

    const decodeInterval = setInterval(() => {
      if (decodeIdx >= nonSpaceIndices.length) {
        clearInterval(decodeInterval)
        // Phase 3: All resolved — gold pulse
        setGoldPulse(true)
        setTimeout(() => {
          setGoldPulse(false)
          setCipherActive(false)
          setCipherText(null)
          setResolvedGoldIndices(new Set())
          if (intervalRef.current) clearInterval(intervalRef.current)
        }, 400)
        setTimeout(() => { cooldownRef.current = false }, 2000)
        return
      }
      const charIdx = nonSpaceIndices[decodeIdx]
      resolved.add(charIdx)
      goldSet.add(charIdx)
      setResolvedGoldIndices(new Set(goldSet))
      // Remove gold flash after 200ms
      setTimeout(() => {
        goldSet.delete(charIdx)
        setResolvedGoldIndices(new Set(goldSet))
      }, 200)
      decodeIdx++
    }, 80)

    // Start decode after 600ms
    const startDecode = setTimeout(() => {
      // decodeInterval already running, but we delay its start
    }, 0)

    // Actually: we need to delay the decode start
    // Clear the premature decode interval and restart after 600ms
    clearInterval(decodeInterval)

    const decodeTimeout = setTimeout(() => {
      let idx2 = 0
      const di2 = setInterval(() => {
        if (idx2 >= nonSpaceIndices.length) {
          clearInterval(di2)
          setGoldPulse(true)
          setTimeout(() => {
            setGoldPulse(false)
            setCipherActive(false)
            setCipherText(null)
            setResolvedGoldIndices(new Set())
            if (intervalRef.current) clearInterval(intervalRef.current)
          }, 400)
          setTimeout(() => { cooldownRef.current = false }, 2000)
          return
        }
        const charIdx = nonSpaceIndices[idx2]
        resolved.add(charIdx)
        goldSet.add(charIdx)
        setResolvedGoldIndices(new Set(goldSet))
        setTimeout(() => {
          goldSet.delete(charIdx)
          setResolvedGoldIndices(new Set(goldSet))
        }, 200)
        idx2++
      }, 80)
    }, 600)

    return () => {
      clearTimeout(startDecode)
      clearTimeout(decodeTimeout)
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [cipherActive, chars])

  const handleDoubleTap = useCallback((e) => {
    // Don't trigger on buttons
    if (e.target.closest('button')) return
    const now = Date.now()
    if (now - lastTapRef.current < 300) {
      triggerCipher()
      lastTapRef.current = 0
    } else {
      lastTapRef.current = now
    }
  }, [triggerCipher])

  return { cipherActive, cipherText, cipherFlash, goldPulse, resolvedGoldIndices, handleDoubleTap }
}

/* ── FINGERPRINT SCAN COMPONENT ── */

function FingerprintScan({ phase }) {
  if (phase !== 'scanning') return null
  return (
    <div style={{
      position: 'absolute',
      left: '50%',
      top: '50%',
      transform: 'translate(-50%, -50%)',
      width: 36,
      height: 36,
      pointerEvents: 'none',
    }}>
      {/* Outer spinning dashed ring */}
      <div className="fingerprint-ring" style={{
        position: 'absolute',
        inset: 0,
        borderRadius: '50%',
        border: '2px dashed rgba(201,168,76,0.6)',
        animation: 'fingerprint-spin 0.8s linear infinite, fingerprint-expand 0.75s ease-out forwards',
      }} />
      {/* Concentric fingerprint rings */}
      <svg width="36" height="36" viewBox="0 0 36 36" style={{ position: 'absolute', inset: 0 }}>
        <circle cx="18" cy="18" r="4" fill="none" stroke="rgba(201,168,76,0.3)" strokeWidth="1"
          style={{ animation: 'fingerprint-ring-pulse 0.75s ease-out 0.1s forwards', opacity: 0, transformOrigin: 'center' }} />
        <circle cx="18" cy="18" r="8" fill="none" stroke="rgba(201,168,76,0.2)" strokeWidth="0.8"
          style={{ animation: 'fingerprint-ring-pulse 0.75s ease-out 0.25s forwards', opacity: 0, transformOrigin: 'center' }} />
        <circle cx="18" cy="18" r="12" fill="none" stroke="rgba(201,168,76,0.1)" strokeWidth="0.6"
          style={{ animation: 'fingerprint-ring-pulse 0.75s ease-out 0.4s forwards', opacity: 0, transformOrigin: 'center' }} />
      </svg>
    </div>
  )
}

/* ══════════════════════════════════════════════
   HIDDEN 6TH CARD — SECRET MEMBERSHIP
   ══════════════════════════════════════════════ */

function SecretCard({ isActive }) {
  const [phase, setPhase] = useState(0) // 0=black, 1=line, 2=decoded, 3=subtitle, 4=liquidFill, 5=card, 6=claim, 7=claimed
  const [claimed, setClaimed] = useState(false)
  const [claimFlash, setClaimFlash] = useState(false)
  const [showLiquid, setShowLiquid] = useState(false)
  const [showCard, setShowCard] = useState(false)
  const [flipping, setFlipping] = useState(false)
  const [goldBurst, setGoldBurst] = useState(false)
  const [goldRing, setGoldRing] = useState(false)
  const timerRefs = useRef([])

  // Reset and run animation sequence when card becomes active
  useEffect(() => {
    // Clear any existing timers
    timerRefs.current.forEach(t => clearTimeout(t))
    timerRefs.current = []

    if (!isActive) {
      setPhase(0)
      setShowLiquid(false)
      setShowCard(false)
      return
    }
    if (claimed) {
      setPhase(7)
      setShowCard(true)
      return
    }

    // Animation sequence
    const t1 = setTimeout(() => setPhase(1), 1500)   // Gold line
    const t2 = setTimeout(() => setPhase(2), 3000)   // DECODED
    const t3 = setTimeout(() => setPhase(3), 4000)   // YOU'VE BEEN DECODED
    const t4 = setTimeout(() => {                      // Gold liquid fill
      setPhase(4)
      setShowLiquid(true)
    }, 5500)
    const t5 = setTimeout(() => {                      // Show holographic card
      setPhase(5)
      setShowCard(true)
    }, 8000)
    const t6 = setTimeout(() => setPhase(6), 9500)    // TAP TO CLAIM

    timerRefs.current = [t1, t2, t3, t4, t5, t6]
    return () => timerRefs.current.forEach(t => clearTimeout(t))
  }, [isActive, claimed])

  const handleLiquidComplete = useCallback(() => {
    setShowLiquid(false)
  }, [])

  const handleClaim = useCallback(() => {
    if (phase !== 6 || claimed || flipping) return
    // Start dramatic claim sequence
    setClaimFlash(true)
    setFlipping(true)
    setGoldBurst(true)
    setGoldRing(true)

    // Clear burst after animation
    setTimeout(() => setGoldBurst(false), 800)
    setTimeout(() => setGoldRing(false), 1000)

    // After flip completes, settle into claimed state
    setTimeout(() => {
      setClaimFlash(false)
      setFlipping(false)
      setClaimed(true)
      setPhase(7)
    }, 900)
  }, [phase, claimed, flipping])

  return (
    <div
      className="feed-card relative w-full flex flex-col items-center justify-center"
      style={{ background: '#0D0D0D', position: 'relative', overflow: 'hidden' }}
    >
      {/* Film grain overlay */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 50, opacity: 0.035,
        backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
        mixBlendMode: 'overlay',
      }} />

      {/* Gold Liquid Fill (Effect 3) */}
      <GoldLiquidFill active={showLiquid} onComplete={handleLiquidComplete} />

      {/* Claim flash overlay — bright gold burst */}
      {claimFlash && (
        <div style={{
          position: 'absolute', inset: 0, zIndex: 40,
          background: 'radial-gradient(circle at 50% 50%, rgba(232,212,139,0.35) 0%, rgba(201,168,76,0.15) 40%, rgba(201,168,76,0) 70%)',
          animation: 'claim-gold-flash 0.9s ease-out forwards',
          pointerEvents: 'none',
        }} />
      )}

      {/* Content container — absolutely centered to prevent layout shift */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        zIndex: 10,
        width: '100%',
      }}>
        {/* "DECODED" text */}
        <div style={{
          fontFamily: "'Bebas Neue', sans-serif",
          fontSize: 48,
          letterSpacing: '0.3em',
          color: '#C9A84C',
          opacity: phase >= 2 && phase < 5 ? 1 : 0,
          transition: 'opacity 1.2s ease',
          marginBottom: 16,
          textAlign: 'center',
          textShadow: '0 0 40px rgba(201,168,76,0.2)',
        }}>
          DECODED
        </div>

        {/* Gold line */}
        <div style={{
          width: phase >= 1 && phase < 5 ? 120 : 0,
          height: 1,
          background: 'linear-gradient(90deg, transparent, #C9A84C, transparent)',
          boxShadow: '0 0 20px rgba(201,168,76,0.3)',
          transition: 'width 1.5s cubic-bezier(0.16, 1, 0.3, 1)',
          marginBottom: 16,
        }} />

        {/* "YOU'VE BEEN DECODED" */}
        <div style={{
          fontFamily: "'Inter', sans-serif",
          fontWeight: 300,
          fontSize: 11,
          letterSpacing: '0.35em',
          color: 'rgba(245,240,232,0.5)',
          textTransform: 'uppercase',
          opacity: phase >= 3 && phase < 5 ? 1 : 0,
          transition: 'opacity 1.2s ease',
          marginBottom: 40,
          textAlign: 'center',
        }}>
          YOU'VE BEEN DECODED
        </div>

        {/* Card wrapper with flip animation and gold ring */}
        <div style={{ position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          {/* Expanding gold ring pulse */}
          {goldRing && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              width: 0,
              height: 0,
              transform: 'translate(-50%, -50%)',
              borderRadius: '50%',
              border: '2px solid rgba(232,212,139,0.7)',
              animation: 'claim-ring-expand 1s ease-out forwards',
              pointerEvents: 'none',
              zIndex: 20,
            }} />
          )}
          {/* Gold burst particles */}
          {goldBurst && (
            <div style={{ position: 'absolute', top: '50%', left: '50%', width: 0, height: 0, zIndex: 20, pointerEvents: 'none' }}>
              {Array.from({ length: 16 }, (_, i) => {
                const angle = (i / 16) * 360
                const rad = (angle * Math.PI) / 180
                const dist = 60 + Math.random() * 50
                return (
                  <span key={i} style={{
                    position: 'absolute',
                    width: 3 + Math.random() * 3,
                    height: 3 + Math.random() * 3,
                    borderRadius: '50%',
                    background: i % 3 === 0 ? '#E8D48B' : i % 3 === 1 ? '#C9A84C' : '#FFF0C8',
                    boxShadow: `0 0 6px ${i % 2 === 0 ? '#E8D48B' : '#C9A84C'}`,
                    left: 0, top: 0,
                    '--burst-tx': `${Math.cos(rad) * dist}px`,
                    '--burst-ty': `${Math.sin(rad) * dist}px`,
                    animation: 'claim-burst-particle 0.7s ease-out forwards',
                  }} />
                )
              })}
            </div>
          )}

          {/* Holographic Card — with flip wrapper */}
          <div style={{
            animation: flipping ? 'claim-card-flip 0.9s ease-in-out forwards' : 'none',
            transformStyle: 'preserve-3d',
            perspective: 800,
          }}>
            <HolographicCard
              visible={showCard}
              claimed={phase === 7}
              onClaim={phase === 6 ? handleClaim : null}
            />
          </div>
        </div>

        {/* TAP TO CLAIM — absolutely positioned so it doesn't shift the card */}
        <div style={{
          position: 'absolute',
          bottom: -44,
          left: '50%',
          transform: 'translateX(-50%)',
          opacity: phase === 6 && !claimed ? 1 : 0,
          transition: 'opacity 0.4s ease',
          pointerEvents: phase === 6 && !claimed ? 'auto' : 'none',
        }}>
          <div style={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 400,
            fontSize: 10,
            letterSpacing: '0.3em',
            color: 'rgba(201,168,76,0.6)',
            textTransform: 'uppercase',
            animation: 'claim-pulse 2s ease-in-out infinite',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
          }}
          onClick={handleClaim}
          >
            TAP TO CLAIM
          </div>
        </div>
      </div>

      {/* Brand mark */}
      <div style={{
        position: 'absolute', bottom: 30, left: '50%', transform: 'translateX(-50%)',
        fontFamily: "'Inter', sans-serif", fontWeight: 300, fontSize: 8,
        letterSpacing: '0.25em', color: 'rgba(201,168,76,0.12)', textTransform: 'uppercase',
      }}>
        Built by Roviq
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════
   PRODUCT CARD
   ══════════════════════════════════════════════ */

function ProductCard({ product, isActive, isNear, isLast, audioEnabled }) {
  const { h, m, s, expired } = useCountdown(product.dropEnd)
  const [fireCount, setFireCount] = useState(product.fireCount)
  const [skullCount, setSkullCount] = useState(product.skullCount)
  const [fireTrigger, setFireTrigger] = useState(0)
  const [fireActive, setFireActive] = useState(false)
  const [skullActive, setSkullActive] = useState(false)
  const [vaultState, setVaultState] = useState('idle') // idle | authenticating | scanning | verified | done
  const [videoLoaded, setVideoLoaded] = useState(false)
  const videoRef = useRef(null)

  // Control video playback — only play active card
  useEffect(() => {
    const v = videoRef.current
    if (!v) return
    if (isActive) {
      v.muted = true // Always muted to prevent iOS play button
      v.play().catch(() => {})
    } else {
      v.pause()
    }
  }, [isActive])

  // Video stays muted — music handles all audio
  useEffect(() => {
    const v = videoRef.current
    if (!v) return
    v.muted = true
  }, [audioEnabled, isActive])
  const [selectedSize, setSelectedSize] = useState('M')
  const [vignetteIntensify, setVignetteIntensify] = useState(false)

  // Cipher reveal
  const { cipherActive, cipherText, cipherFlash, goldPulse, resolvedGoldIndices, handleDoubleTap } = useCipherReveal(product.name)

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

  /* ── FINGERPRINT VAULT HANDLER ── */
  const handleVault = useCallback(() => {
    if (vaultState !== 'idle') return

    // Phase 1: Authenticating
    setVaultState('authenticating')
    setVignetteIntensify(true)

    // Phase 2: Scanning
    setTimeout(() => setVaultState('scanning'), 150)

    // Phase 3: Verified flash
    setTimeout(() => {
      setVaultState('verified')
      setVignetteIntensify(false)
    }, 900)

    // Phase 4: Done state with VERIFIED text
    setTimeout(() => setVaultState('done'), 1100)

    // Reset to idle after 2 seconds
    setTimeout(() => setVaultState('idle'), 3100)
  }, [vaultState])

  const reveal = (delay) => ({
    opacity: isActive ? 1 : 0,
    transform: isActive ? 'translateY(0)' : 'translateY(22px)',
    transition: `opacity 0.6s cubic-bezier(0.16,1,0.3,1) ${delay}s, transform 0.6s cubic-bezier(0.16,1,0.3,1) ${delay}s`,
  })

  // Render the product name with cipher effect
  const renderProductName = () => {
    if (cipherText !== null) {
      // Render character by character for gold flash
      const displayChars = [...cipherText]
      const originalChars = [...product.name.replace(/\n/g, '\n')]
      return displayChars.map((ch, i) => {
        if (ch === '\n') return <br key={i} />
        const isResolved = resolvedGoldIndices.has(i)
        return (
          <span
            key={i}
            style={{
              color: isResolved ? '#E8D48B' : '#F5F0E8',
              transition: 'color 0.2s ease',
              display: 'inline',
            }}
          >
            {ch}
          </span>
        )
      })
    }
    return product.name
  }

  // Determine vault button content
  const renderVaultContent = () => {
    switch (vaultState) {
      case 'authenticating':
        return (
          <span style={{
            fontSize: 10,
            letterSpacing: '0.2em',
            opacity: 0.8,
            animation: 'vault-text-fade 0.15s ease forwards',
          }}>
            AUTHENTICATING...
          </span>
        )
      case 'scanning':
        return (
          <>
            <span style={{ fontSize: 10, letterSpacing: '0.2em', opacity: 0.6 }}>
              AUTHENTICATING...
            </span>
            <FingerprintScan phase="scanning" />
          </>
        )
      case 'verified':
        return (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E8D48B" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="4 12 10 18 20 6" style={{ strokeDasharray: 30, strokeDashoffset: 0, animation: 'draw-check 0.35s ease forwards' }} />
            </svg>
            <span style={{ color: '#E8D48B' }}>VERIFIED</span>
          </>
        )
      case 'done':
        return (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E8D48B" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="4 12 10 18 20 6" style={{ strokeDasharray: 30, strokeDashoffset: 0 }} />
            </svg>
            <span style={{ color: '#E8D48B' }}>VERIFIED</span>
          </>
        )
      default:
        return <span>Add to Vault</span>
    }
  }

  const isVaultActive = vaultState !== 'idle'
  const isVaultDone = vaultState === 'done' || vaultState === 'verified'

  return (
    <div
      className="feed-card relative w-full flex flex-col justify-end"
      style={{ background: product.gradient }}
      onClick={handleDoubleTap}
    >
      {/* Cipher flash overlay */}
      {cipherFlash && (
        <div style={{
          position: 'absolute', inset: 0, zIndex: 30,
          background: 'rgba(201,168,76,0.06)',
          animation: 'cipher-flash 0.2s ease-out forwards',
          pointerEvents: 'none',
        }} />
      )}

      {/* Gold pulse shockwave */}
      {goldPulse && (
        <div className="cipher-shockwave" style={{
          position: 'absolute',
          left: 22,
          bottom: '35%',
          width: 0,
          height: 0,
          zIndex: 30,
          pointerEvents: 'none',
        }} />
      )}

      {/* Loading shimmer while video loads */}
      {product.video && !videoLoaded && (
        <div style={{
          position: 'absolute', inset: 0, zIndex: 0,
          background: 'linear-gradient(135deg, #0D0D0D 0%, #1a1a1a 50%, #0D0D0D 100%)',
          backgroundSize: '200% 200%',
          animation: 'shimmer 2s ease-in-out infinite',
        }}>
          <div style={{
            position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
          }}>
            <div style={{
              width: 32, height: 32, border: '2px solid rgba(201,168,76,0.15)',
              borderTopColor: 'rgba(201,168,76,0.5)', borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
            }} />
            <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 9, letterSpacing: '0.2em', color: 'rgba(201,168,76,0.3)', textTransform: 'uppercase' }}>Loading</span>
          </div>
        </div>
      )}

      {/* Video background with Ken Burns */}
      {product.video && isNear && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}>
          <video
            ref={videoRef}
            src={product.video}
            autoPlay
            loop
            muted
            playsInline
            webkit-playsinline=""
            preload="auto"
            controls={false}
            onLoadedData={() => { setVideoLoaded(true); if (isActive && videoRef.current) videoRef.current.play().catch(() => {}) }}
            className={videoLoaded && isActive ? 'video-zoom' : ''}
            style={{
              width: '100%', height: '100%',
              objectFit: 'cover',
              opacity: videoLoaded ? 0.9 : 0,
              transition: 'opacity 1.2s ease-in-out',
              pointerEvents: 'none',
            }}
          />
        </div>
      )}

      {/* Film Noise overlay on video (Effect 5) */}
      <FilmNoise isActive={isActive && videoLoaded} />

      {/* Vignette */}
      <div
        className="vignette absolute inset-0 z-[1]"
        style={{
          transition: 'opacity 0.3s ease',
          opacity: vignetteIntensify ? 1.5 : 1,
        }}
      />
      {/* Gradient overlay */}
      <div className="gradient-overlay absolute inset-0 z-[2]" />

      {/* Brand mark — static */}
      <div style={{
        position: 'absolute', top: 'calc(57px + env(safe-area-inset-top, 0px))', left: 22, zIndex: 5,
        fontFamily: "'Inter', sans-serif", fontWeight: 800, fontSize: 9,
        letterSpacing: '0.4em', color: 'rgba(201,168,76,0.15)', textTransform: 'uppercase',
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
            background: fireActive ? 'rgba(201,168,76,0.15)' : 'rgba(245,240,232,0.07)',
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
            background: skullActive ? 'rgba(245,240,232,0.1)' : 'rgba(245,240,232,0.07)',
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
            background: 'rgba(245,240,232,0.07)',
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

      {/* Music ticker — TikTok style */}
      {product.songName && (
        <div style={{
          position: 'absolute', bottom: 'calc(env(safe-area-inset-bottom, 0px) + 10px)',
          left: 22, zIndex: 15,
          display: 'flex', alignItems: 'center', gap: 8,
          maxWidth: 200, overflow: 'hidden',
        }}>
          {/* Spinning disc */}
          <div style={{
            width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
            background: 'radial-gradient(circle at 50% 50%, #333 30%, #1a1a1a 32%, #222 60%, #111 100%)',
            border: '2px solid rgba(201,168,76,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            animation: isActive ? 'spin 3s linear infinite' : 'none',
          }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#C9A84C' }} />
          </div>
          {/* Scrolling song name */}
          <div style={{ overflow: 'hidden', flex: 1 }}>
            <div style={{
              fontFamily: "'Inter', sans-serif", fontWeight: 400, fontSize: 10,
              color: 'rgba(245,240,232,0.6)', whiteSpace: 'nowrap',
              animation: isActive ? 'music-marquee 8s linear infinite' : 'none',
            }}>
              {product.songName}
            </div>
          </div>
        </div>
      )}

      {/* ── BOTTOM CONTENT ── */}
      <div style={{ position: 'relative', zIndex: 5, padding: '0 22px 16px' }}>

        {/* Scarcity tag */}
        <div style={{ ...reveal(0.08), marginBottom: 10 }}>
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

        {/* Product name — with cipher effect */}
        <h2 style={{
          ...reveal(0.16),
          fontFamily: "'Bebas Neue', 'Inter', sans-serif",
          fontWeight: 400,
          fontSize: 'clamp(44px, 13vw, 64px)',
          lineHeight: 0.92,
          letterSpacing: '0.04em',
          color: '#F5F0E8',
          textShadow: cipherActive
            ? '2px 0 #ff000018, -2px 0 #00ffff18, 0 2px 30px rgba(0,0,0,0.6), 0 0 60px rgba(0,0,0,0.3)'
            : '0 2px 30px rgba(0,0,0,0.6), 0 0 60px rgba(0,0,0,0.3)',
          whiteSpace: 'pre-line',
          marginBottom: product.subtitle ? 4 : 6,
          animation: cipherActive ? 'cipher-glitch 0.1s ease infinite' : 'none',
        }}>{renderProductName()}</h2>

        {/* Subtitle */}
        {product.subtitle && (
          <div style={{
            ...reveal(0.2),
            fontFamily: "'Inter', sans-serif", fontWeight: 300, fontSize: 13,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            color: 'rgba(245,240,232,0.45)', marginBottom: 6,
          }}>{product.subtitle}</div>
        )}

        {/* Gold divider */}
        <div className="gold-divider" style={{ ...reveal(0.22), width: 60, marginBottom: 8 }} />

        {/* Price */}
        <div style={{
          ...reveal(0.26),
          fontFamily: "'Inter', sans-serif", fontWeight: 350, fontSize: 30,
          color: '#F5F0E8', letterSpacing: '0.02em', marginBottom: 4,
          textShadow: '0 1px 20px rgba(0,0,0,0.4)',
        }}>
          <span style={{ fontSize: 16, opacity: 0.4, marginRight: 2, fontWeight: 300 }}>$</span>{product.price}
        </div>

        {/* Materials & Edition */}
        <div style={{
          ...reveal(0.28),
          fontFamily: "'Inter', sans-serif",
          fontSize: 10,
          letterSpacing: '0.1em',
          color: 'rgba(245,240,232,0.3)',
          marginBottom: 10,
          textTransform: 'uppercase',
        }}>
          {product.materials} · Edition of {product.edition}
        </div>

        {/* Countdown */}
        <div style={{ ...reveal(0.32), marginBottom: 14, display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ display: 'flex', gap: 4, position: 'relative' }}>
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
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400, fontSize: 8, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'rgba(245,240,232,0.2)' }}>{expired ? 'EXPIRED' : 'REMAINING'}</span>
        </div>

        {/* Size Selector */}
        <div style={reveal(0.36)}>
          <SizeSelector selectedSize={selectedSize} onSelectSize={setSelectedSize} />
        </div>

        {/* ADD TO VAULT — 3D Glass with Fingerprint Scan */}
        <div style={reveal(0.38)}>
          <button onClick={handleVault} style={{
            position: 'relative', width: '100%', height: 48,
            border: isVaultDone ? '1px solid rgba(212,185,106,0.5)' : '1px solid rgba(201,168,76,0.25)',
            borderRadius: 14, cursor: 'pointer',
            fontFamily: "'Inter', sans-serif", fontWeight: 700, fontSize: 12,
            letterSpacing: '0.14em', textTransform: 'uppercase',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
            transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)', overflow: 'hidden',
            background: isVaultDone
              ? 'linear-gradient(135deg, rgba(212,185,106,0.22) 0%, rgba(168,137,59,0.18) 100%)'
              : vaultState === 'scanning'
                ? 'linear-gradient(135deg, rgba(212,185,106,0.18) 0%, rgba(201,168,76,0.12) 50%, rgba(168,137,59,0.18) 100%)'
                : 'linear-gradient(135deg, rgba(212,185,106,0.12) 0%, rgba(201,168,76,0.08) 50%, rgba(168,137,59,0.12) 100%)',
            backdropFilter: 'blur(24px) saturate(1.4)',
            WebkitBackdropFilter: 'blur(24px) saturate(1.4)',
            color: isVaultDone ? '#E8D48B' : '#D4B96A',
            animation: vaultState === 'verified' ? 'vault-fingerprint-flash 0.2s ease forwards'
              : isVaultDone ? 'glass-confirmed-glow 2s ease-in-out infinite'
              : vaultState === 'scanning' ? 'glass-glow-breathe 3.5s ease-in-out infinite'
              : 'glass-glow-breathe 3.5s ease-in-out infinite',
            transform: vaultState === 'authenticating' ? 'scale(0.98)' : 'scale(1)',
          }}>
            {/* Top highlight edge — warm gold light catch */}
            <span style={{
              position: 'absolute', top: 0, left: '8%', right: '8%', height: 1,
              background: 'linear-gradient(90deg, transparent, rgba(232,212,139,0.3), rgba(212,185,106,0.5), rgba(232,212,139,0.3), transparent)',
              borderRadius: '0 0 50% 50%',
              pointerEvents: 'none',
            }} />
            {/* Inner top glow — gold glass depth */}
            <span style={{
              position: 'absolute', top: 0, left: 0, right: 0, height: '50%',
              background: 'linear-gradient(180deg, rgba(212,185,106,0.1) 0%, rgba(201,168,76,0.03) 40%, transparent 100%)',
              borderRadius: '14px 14px 50% 50%',
              pointerEvents: 'none',
            }} />
            {/* Refraction drift */}
            <span style={{
              position: 'absolute', top: '8%', left: '15%', width: '40%', height: '35%',
              background: 'radial-gradient(ellipse, rgba(232,212,139,0.08) 0%, transparent 70%)',
              borderRadius: '50%', filter: 'blur(6px)',
              animation: 'glass-refraction-drift 6s ease-in-out infinite',
              pointerEvents: 'none',
            }} />
            {/* Glass shine sweep — warm gold */}
            <span style={{
              position: 'absolute', top: 0, left: 0, width: '35%', height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(232,212,139,0.12), rgba(212,185,106,0.08), transparent)',
              animation: 'glass-shine-sweep 6s ease-in-out infinite', animationDelay: '1.5s',
              pointerEvents: 'none',
            }} />
            {/* Content */}
            <span style={{ position: 'relative', zIndex: 2, display: 'flex', alignItems: 'center', gap: 10, textShadow: '0 0 20px rgba(201,168,76,0.3)' }}>
              {renderVaultContent()}
            </span>
          </button>
        </div>

        {/* Swipe / Roviq */}
        <div style={{ ...reveal(0.44), display: 'flex', justifyContent: 'center', marginTop: 10 }}>
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
  const [audioEnabled, setAudioEnabled] = useState(false)
  const [muted, setMuted] = useState(false)
  const musicRefs = useRef({})
  const totalCards = products.length + 1 // +1 for secret card

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

  // Enable audio on first user interaction + preload all tracks
  useEffect(() => {
    const enable = () => {
      setAudioEnabled(true)
      // Force-load all music tracks into buffer
      Object.values(musicRefs.current).forEach(audio => {
        audio.load()
      })
      document.removeEventListener('touchstart', enable)
      document.removeEventListener('click', enable)
    }
    document.addEventListener('touchstart', enable, { once: true })
    document.addEventListener('click', enable, { once: true })
    return () => { document.removeEventListener('touchstart', enable); document.removeEventListener('click', enable) }
  }, [])

  // Manage music playback — crossfade between tracks
  useEffect(() => {
    if (!audioEnabled) return
    products.forEach((product, i) => {
      const audio = musicRefs.current[product.id]
      if (!audio) return
      if (i === activeIndex && !muted) {
        audio.currentTime = audio.currentTime || 0
        audio.volume = 0.4
        const p = audio.play()
        if (p) p.catch(() => {})
      } else {
        audio.pause()
      }
    })
  }, [activeIndex, audioEnabled, muted])

  const toggleMute = useCallback(() => setMuted(m => !m), [])

  return (
    <>
      <DropBanner />

      {/* Audio elements for music tracks */}
      {products.map(product => (
        <audio
          key={`music-${product.id}`}
          ref={el => { if (el) musicRefs.current[product.id] = el }}
          src={product.music}
          loop
          preload="auto"
          onEnded={e => { e.target.currentTime = 0; e.target.play().catch(() => {}) }}
        />
      ))}

      {/* Mute toggle */}
      <button onClick={toggleMute} style={{
        position: 'fixed', top: 'calc(env(safe-area-inset-top, 0px) + 6px)', right: 14, zIndex: 50,
        width: 32, height: 32, borderRadius: '50%',
        background: 'rgba(245,240,232,0.07)', border: '1px solid rgba(245,240,232,0.1)',
        backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'pointer', padding: 0,
      }}>
        {muted ? (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#F5F0E8" strokeWidth="1.5" strokeLinecap="round" opacity="0.5">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <line x1="23" y1="9" x2="17" y2="15" />
            <line x1="17" y1="9" x2="23" y2="15" />
          </svg>
        ) : (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" strokeWidth="1.5" strokeLinecap="round" opacity="0.7">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <path d="M15.54 8.46a5 5 0 010 7.07" />
            <path d="M19.07 4.93a10 10 0 010 14.14" />
          </svg>
        )}
      </button>

      <div ref={scrollRef} className="feed-scroll no-scrollbar">
        {products.map((product, i) => (
          <ProductCard
            key={product.id}
            product={product}
            isActive={activeIndex === i}
            isNear={Math.abs(activeIndex - i) <= 2}
            isLast={false}
            audioEnabled={audioEnabled && !muted}
          />
        ))}
        <SecretCard isActive={activeIndex === products.length} />
      </div>
    </>
  )
}
