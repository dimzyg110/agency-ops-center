import { useRef, useEffect, useState, useCallback } from 'react'
import ParticleNumberReveal from './ParticleNumberReveal'

/**
 * Effect 1: 3D Holographic Membership Card
 * Dark matte card with holographic rainbow shimmer that tracks device tilt or mouse position.
 * Includes idle bobbing animation, silver/white accents, and the particle number reveal.
 */
export default function HolographicCard({ visible, claimed, onClaim }) {
  const cardRef = useRef(null)
  const containerRef = useRef(null)
  const [tilt, setTilt] = useState({ x: 0, y: 0 })
  const [isOrienting, setIsOrienting] = useState(false)
  const [showNumber, setShowNumber] = useState(false)
  const orientPermRef = useRef(false)
  const mouseTrackingRef = useRef(false)

  // Show number after card is visible for a beat
  useEffect(() => {
    if (!visible) {
      setShowNumber(false)
      return
    }
    const t = setTimeout(() => setShowNumber(true), 800)
    return () => clearTimeout(t)
  }, [visible])

  // DeviceOrientation for mobile tilt
  const handleOrientation = useCallback((e) => {
    if (!visible) return
    const beta = e.beta || 0
    const gamma = e.gamma || 0
    const x = Math.max(-1, Math.min(1, gamma / 30))
    const y = Math.max(-1, Math.min(1, (beta - 45) / 30))
    setTilt({ x, y })
    setIsOrienting(true)
  }, [visible])

  // Request permission for iOS 13+ DeviceOrientation
  const requestOrientationPermission = useCallback(async () => {
    if (orientPermRef.current) return
    if (typeof DeviceOrientationEvent !== 'undefined' &&
        typeof DeviceOrientationEvent.requestPermission === 'function') {
      try {
        const resp = await DeviceOrientationEvent.requestPermission()
        if (resp === 'granted') {
          orientPermRef.current = true
          window.addEventListener('deviceorientation', handleOrientation, true)
        }
      } catch (err) {
        // Permission denied or error, fall back to mouse
      }
    } else if (typeof DeviceOrientationEvent !== 'undefined') {
      orientPermRef.current = true
      window.addEventListener('deviceorientation', handleOrientation, true)
    }
  }, [handleOrientation])

  // Mouse/touch tracking for desktop fallback
  const handleMouseMove = useCallback((e) => {
    if (isOrienting || !containerRef.current || !visible) return
    const rect = containerRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    const x = (e.clientX - centerX) / (rect.width / 2)
    const y = (e.clientY - centerY) / (rect.height / 2)
    setTilt({
      x: Math.max(-1, Math.min(1, x)),
      y: Math.max(-1, Math.min(1, y)),
    })
  }, [isOrienting, visible])

  useEffect(() => {
    if (!visible) return
    requestOrientationPermission()
    window.addEventListener('mousemove', handleMouseMove)
    return () => {
      window.removeEventListener('deviceorientation', handleOrientation, true)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [visible, handleOrientation, handleMouseMove, requestOrientationPermission])

  // Touch handler to request orientation permission (iOS needs user gesture)
  const handleTouchStart = useCallback(() => {
    if (!orientPermRef.current) {
      requestOrientationPermission()
    }
  }, [requestOrientationPermission])

  if (!visible) return null

  const rotateY = tilt.x * 15
  const rotateX = -tilt.y * 12

  // Holographic shimmer position based on tilt
  const shimmerX = 50 + tilt.x * 40
  const shimmerY = 50 + tilt.y * 40

  return (
    <div
      ref={containerRef}
      onTouchStart={handleTouchStart}
      style={{
        perspective: 800,
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        ref={cardRef}
        onClick={onClaim}
        className="holo-card-bob"
        style={{
          width: 280,
          height: 176,
          borderRadius: 14,
          position: 'relative',
          transformStyle: 'preserve-3d',
          transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
          transition: 'transform 0.15s ease-out',
          cursor: onClaim ? 'pointer' : 'default',
          animation: visible ? 'holo-card-entrance 0.8s ease-out forwards' : 'none',
        }}
      >
        {/* Card background - dark matte surface */}
        <div style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 14,
          background: 'linear-gradient(145deg, #1a1a1a 0%, #111 40%, #0d0d0d 100%)',
          border: claimed ? '1px solid rgba(232,212,139,0.5)' : '1px solid rgba(201,168,76,0.25)',
          boxShadow: claimed
            ? `0 20px 60px rgba(0,0,0,0.6), 0 0 30px rgba(201,168,76,0.25), 0 0 1px rgba(201,168,76,0.5), inset 0 1px 0 rgba(255,255,255,0.06)`
            : `0 20px 60px rgba(0,0,0,0.6), 0 0 1px rgba(201,168,76,0.3), inset 0 1px 0 rgba(255,255,255,0.04)`,
          transition: 'box-shadow 0.6s ease',
          overflow: 'hidden',
        }}>
          {/* Holographic rainbow shimmer overlay */}
          <div style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 14,
            background: `
              radial-gradient(
                ellipse 60% 70% at ${shimmerX}% ${shimmerY}%,
                rgba(255,255,255,0.07) 0%,
                rgba(220,220,220,0.06) 20%,
                rgba(201,168,76,0.05) 40%,
                rgba(180,180,180,0.06) 60%,
                rgba(160,160,160,0.05) 80%,
                transparent 100%
              )
            `,
            mixBlendMode: 'screen',
            transition: 'background 0.1s ease-out',
            pointerEvents: 'none',
          }} />

          {/* Subtle shimmer sweep line */}
          <div style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 14,
            background: `linear-gradient(
              ${120 + tilt.x * 40}deg,
              transparent 0%,
              transparent ${40 + tilt.x * 10}%,
              rgba(255,255,255,0.04) ${48 + tilt.x * 10}%,
              rgba(255,255,255,0.07) ${50 + tilt.x * 10}%,
              rgba(255,255,255,0.04) ${52 + tilt.x * 10}%,
              transparent ${60 + tilt.x * 10}%,
              transparent 100%
            )`,
            pointerEvents: 'none',
          }} />

          {/* Silver edge highlight on top */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: '10%',
            right: '10%',
            height: 1,
            background: 'linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent)',
            borderRadius: '0 0 50% 50%',
          }} />

          {/* Card content */}
          <div style={{
            position: 'relative',
            zIndex: 2,
            padding: '20px 24px',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}>
            {/* Top section */}
            <div>
              <div style={{
                fontFamily: "'Bebas Neue', sans-serif",
                fontSize: 22,
                letterSpacing: '0.3em',
                color: '#C9A84C',
                lineHeight: 1,
                textShadow: '0 0 20px rgba(201,168,76,0.15)',
              }}>
                DECODED
              </div>
            </div>

            {/* Middle - founding member label */}
            <div style={{
              fontFamily: "'Inter', sans-serif",
              fontWeight: 300,
              fontSize: 9,
              letterSpacing: '0.3em',
              color: 'rgba(245,240,232,0.35)',
              textTransform: 'uppercase',
            }}>
              {claimed ? 'CLAIMED' : 'FOUNDING MEMBER'}
            </div>

            {/* Bottom - member number */}
            <div style={{
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'space-between',
            }}>
              <div style={{ position: 'relative' }}>
                {/* Static fallback number (visible after particles settle) */}
                <div style={{
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: 300,
                  fontSize: 18,
                  letterSpacing: '0.15em',
                  color: '#C9A84C',
                  opacity: showNumber ? 0 : 0, // Hidden, particles handle display
                }}>
                  {'№ '}0001
                </div>
                {/* Particle canvas overlay for number */}
                <div style={{
                  position: 'relative',
                  width: 120,
                  height: 30,
                }}>
                  <ParticleNumberReveal
                    active={showNumber}
                    width={120}
                    height={30}
                  />
                  {/* Static number underneath as backup after animation */}
                  <div style={{
                    position: 'absolute',
                    inset: 0,
                    display: 'flex',
                    alignItems: 'center',
                    fontFamily: "'Bebas Neue', sans-serif",
                    fontSize: 20,
                    letterSpacing: '0.15em',
                    color: 'rgba(201,168,76,0)',
                    pointerEvents: 'none',
                  }}>
                    {'№ 0001'}
                  </div>
                </div>
              </div>

              {claimed && (
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ filter: 'drop-shadow(0 0 8px rgba(201,168,76,0.4))' }}>
                  <polyline points="4 12 10 18 20 6" style={{ strokeDasharray: 30, strokeDashoffset: 30, animation: 'claim-draw-check 0.6s ease forwards 0.15s' }} />
                </svg>
              )}
            </div>
          </div>

          {/* Micro-texture overlay */}
          <div style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 14,
            opacity: 0.02,
            backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.5' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
            mixBlendMode: 'overlay',
            pointerEvents: 'none',
          }} />
        </div>
      </div>
    </div>
  )
}
