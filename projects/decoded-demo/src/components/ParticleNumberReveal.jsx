import { useRef, useEffect, useCallback, useState } from 'react'

/**
 * Effect 2: Particle Number Reveal
 * Silver/white particles start scattered, then swarm together to form "0001".
 * After forming, particles gently breathe/drift in position.
 */
export default function ParticleNumberReveal({ active, width, height }) {
  const canvasRef = useRef(null)
  const rafRef = useRef(null)
  const particlesRef = useRef([])
  const targetPointsRef = useRef([])
  const startTimeRef = useRef(null)
  const [ready, setReady] = useState(false)

  // Build target points from text "0001"
  const buildTargets = useCallback(() => {
    const canvas = document.createElement('canvas')
    const textW = width || 240
    const textH = height || 60
    canvas.width = textW
    canvas.height = textH
    const ctx = canvas.getContext('2d')
    if (!ctx) return []

    ctx.fillStyle = '#fff'
    ctx.font = `bold ${Math.floor(textH * 0.7)}px "Bebas Neue", sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('0001', textW / 2, textH / 2)

    const imageData = ctx.getImageData(0, 0, textW, textH)
    const points = []
    const step = 3 // Sample every 3 pixels
    for (let y = 0; y < textH; y += step) {
      for (let x = 0; x < textW; x += step) {
        const idx = (y * textW + x) * 4
        if (imageData.data[idx + 3] > 128) {
          points.push({ x, y })
        }
      }
    }
    return points
  }, [width, height])

  useEffect(() => {
    if (!active) {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
      particlesRef.current = []
      setReady(false)
      return
    }

    const targets = buildTargets()
    targetPointsRef.current = targets

    if (targets.length === 0) return

    // Create particles, scattered randomly
    const cW = width || 240
    const cH = height || 60
    const particles = targets.map((target) => ({
      x: Math.random() * cW,
      y: Math.random() * cH,
      targetX: target.x,
      targetY: target.y,
      size: 1.2 + Math.random() * 1.4,
      speed: 0.02 + Math.random() * 0.03,
      settled: false,
      breatheOffset: Math.random() * Math.PI * 2,
      breatheAmp: 0.4 + Math.random() * 0.8,
    }))
    particlesRef.current = particles
    startTimeRef.current = null
    setReady(true)

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
    }
  }, [active, buildTargets, width, height])

  const render = useCallback((timestamp) => {
    if (!canvasRef.current || !ready) return

    if (!startTimeRef.current) startTimeRef.current = timestamp
    const elapsed = (timestamp - startTimeRef.current) / 1000

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const cW = canvas.width
    const cH = canvas.height
    ctx.clearRect(0, 0, cW, cH)

    const particles = particlesRef.current
    const swarmDuration = 2.0 // seconds to converge

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]

      if (elapsed < swarmDuration) {
        // Lerp toward target with easing
        const t = Math.min(elapsed / swarmDuration, 1)
        const ease = 1 - Math.pow(1 - t, 3) // easeOutCubic
        // Add some individual variation in timing
        const individualT = Math.min(elapsed / (swarmDuration * (1 + (1 - p.speed / 0.05) * 0.3)), 1)
        const individualEase = 1 - Math.pow(1 - individualT, 3)

        p.x = p.x + (p.targetX - p.x) * (individualEase * 0.08 + p.speed)
        p.y = p.y + (p.targetY - p.y) * (individualEase * 0.08 + p.speed)
      } else {
        // Breathe in position
        p.x = p.targetX + Math.sin(elapsed * 1.5 + p.breatheOffset) * p.breatheAmp
        p.y = p.targetY + Math.cos(elapsed * 1.2 + p.breatheOffset * 1.3) * p.breatheAmp * 0.7
      }

      // White/silver color with glow
      const alpha = Math.min(elapsed * 2, 1)
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)

      // Glow effect
      ctx.shadowColor = 'rgba(201,168,76,0.6)'
      ctx.shadowBlur = 4
      ctx.fillStyle = `rgba(232,212,139,${alpha * 0.9})`
      ctx.fill()

      // Core bright dot
      ctx.shadowBlur = 0
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.size * 0.5, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(255,255,255,${alpha * 0.7})`
      ctx.fill()
    }

    rafRef.current = requestAnimationFrame(render)
  }, [ready])

  useEffect(() => {
    if (!ready) return
    rafRef.current = requestAnimationFrame(render)
    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
    }
  }, [ready, render])

  if (!active) return null

  return (
    <canvas
      ref={canvasRef}
      width={width || 240}
      height={height || 60}
      style={{
        position: 'absolute',
        pointerEvents: 'none',
        zIndex: 5,
      }}
    />
  )
}
