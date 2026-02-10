import { useRef, useEffect, useCallback } from 'react'

/**
 * Effect 3: Gold Liquid Fill — realistic semi-transparent gold liquid
 * with caustics, bubbles, organic wave motion, shimmer highlights,
 * and a natural drain (fast then clinging drips).
 */
export default function GoldLiquidFill({ active, onComplete }) {
  const canvasRef = useRef(null)
  const rafRef = useRef(null)
  const startRef = useRef(null)
  const completedRef = useRef(false)
  const bubblesRef = useRef([])
  const DURATION = 2800

  const animate = useCallback((timestamp) => {
    if (!canvasRef.current) return

    if (!startRef.current) startRef.current = timestamp
    const elapsed = timestamp - startRef.current
    const progress = Math.min(elapsed / DURATION, 1)

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const w = canvas.width
    const h = canvas.height

    ctx.clearRect(0, 0, w, h)

    const time = elapsed / 1000

    // Fill level: rise to 60% then drain with natural physics
    let fillLevel
    if (progress < 0.45) {
      // Rising phase — ease out
      const riseProgress = progress / 0.45
      fillLevel = 0.6 * (1 - Math.pow(1 - riseProgress, 3))
    } else if (progress < 0.55) {
      // Hold at top briefly
      fillLevel = 0.6
    } else {
      // Draining phase — fast start, slow clinging end
      const drainProgress = (progress - 0.55) / 0.45
      // Exponential drain: fast then slow
      fillLevel = 0.6 * Math.pow(1 - drainProgress, 3.5)
    }

    if (fillLevel <= 0.001) {
      if (progress >= 1 && !completedRef.current) {
        completedRef.current = true
        if (onComplete) onComplete()
      }
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate)
      }
      return
    }

    const fillY = h * (1 - fillLevel)

    // Organic wave amplitude — varies over time
    const baseAmplitude = 6 + fillLevel * 10
    const ampMod = 1 + 0.3 * Math.sin(time * 1.7) + 0.15 * Math.sin(time * 2.9)
    const waveAmplitude = baseAmplitude * ampMod

    // Wave function helper
    const getWaveY = (x) => {
      const w1 = Math.sin(x * 0.013 + time * 3.2) * waveAmplitude
      const w2 = Math.sin(x * 0.021 - time * 2.5) * (waveAmplitude * 0.45)
      const w3 = Math.sin(x * 0.037 + time * 4.8) * (waveAmplitude * 0.18)
      const w4 = Math.sin(x * 0.007 + time * 1.1) * (waveAmplitude * 0.6) // slow large swell
      return fillY + w1 + w2 + w3 + w4
    }

    // ── MAIN LIQUID BODY ──
    ctx.beginPath()
    ctx.moveTo(0, h)
    ctx.lineTo(0, getWaveY(0))
    for (let x = 0; x <= w; x += 2) {
      ctx.lineTo(x, getWaveY(x))
    }
    ctx.lineTo(w, h)
    ctx.closePath()

    // Semi-transparent gold gradient
    const gradient = ctx.createLinearGradient(0, fillY, 0, h)
    gradient.addColorStop(0, 'rgba(212,180,75,0.55)')
    gradient.addColorStop(0.15, 'rgba(201,168,76,0.45)')
    gradient.addColorStop(0.4, 'rgba(185,150,55,0.38)')
    gradient.addColorStop(0.7, 'rgba(170,135,45,0.32)')
    gradient.addColorStop(1, 'rgba(155,120,35,0.25)')
    ctx.fillStyle = gradient
    ctx.fill()

    // ── DEPTH VARIATION — darker bands within liquid ──
    ctx.save()
    ctx.beginPath()
    ctx.moveTo(0, h)
    ctx.lineTo(0, getWaveY(0))
    for (let x = 0; x <= w; x += 2) {
      ctx.lineTo(x, getWaveY(x))
    }
    ctx.lineTo(w, h)
    ctx.closePath()
    ctx.clip()

    // Internal depth bands
    for (let i = 0; i < 3; i++) {
      const bandY = fillY + (h - fillY) * (0.25 + i * 0.25)
      const bandH = (h - fillY) * 0.15
      const bandGrad = ctx.createLinearGradient(0, bandY, 0, bandY + bandH)
      bandGrad.addColorStop(0, 'rgba(140,110,30,0)')
      bandGrad.addColorStop(0.5, `rgba(140,110,30,${0.06 + 0.02 * Math.sin(time * 1.3 + i)})`)
      bandGrad.addColorStop(1, 'rgba(140,110,30,0)')
      ctx.fillStyle = bandGrad
      ctx.fillRect(0, bandY, w, bandH)
    }

    // ── CAUSTICS — shimmering light patches ──
    for (let i = 0; i < 6; i++) {
      const cx = (w * 0.15) + (w * 0.7) * ((Math.sin(time * 0.7 + i * 2.1) + 1) / 2)
      const cy = fillY + (h - fillY) * (0.15 + 0.6 * ((Math.sin(time * 0.5 + i * 1.7) + 1) / 2))
      const cr = 15 + 20 * ((Math.sin(time * 1.2 + i * 3.3) + 1) / 2)
      const causticAlpha = 0.04 + 0.06 * ((Math.sin(time * 1.8 + i * 2.5) + 1) / 2)

      const causticGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, cr)
      causticGrad.addColorStop(0, `rgba(255,240,180,${causticAlpha})`)
      causticGrad.addColorStop(0.6, `rgba(232,212,139,${causticAlpha * 0.4})`)
      causticGrad.addColorStop(1, 'rgba(232,212,139,0)')
      ctx.fillStyle = causticGrad
      ctx.fillRect(cx - cr, cy - cr, cr * 2, cr * 2)
    }

    // ── BUBBLES — tiny gold particles floating up ──
    // Spawn new bubbles
    if (fillLevel > 0.05 && Math.random() < 0.35) {
      bubblesRef.current.push({
        x: Math.random() * w,
        y: h - 5,
        size: 1.2 + Math.random() * 2.5,
        speed: 0.4 + Math.random() * 0.8,
        wobble: Math.random() * Math.PI * 2,
        wobbleSpeed: 1 + Math.random() * 2,
        alpha: 0.15 + Math.random() * 0.25,
      })
    }

    // Update and draw bubbles
    bubblesRef.current = bubblesRef.current.filter(b => {
      b.y -= b.speed
      b.x += Math.sin(time * b.wobbleSpeed + b.wobble) * 0.3

      // Remove if above liquid surface or off-screen
      const surfaceY = getWaveY(b.x)
      if (b.y < surfaceY - 2) return false

      // Draw bubble
      ctx.beginPath()
      ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(255,240,190,${b.alpha})`
      ctx.fill()

      // Tiny highlight on bubble
      ctx.beginPath()
      ctx.arc(b.x - b.size * 0.25, b.y - b.size * 0.25, b.size * 0.35, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(255,255,230,${b.alpha * 0.8})`
      ctx.fill()

      return true
    })

    ctx.restore()

    // ── SURFACE SHIMMER HIGHLIGHT — moves and pulses ──
    const shimmerOffset = Math.sin(time * 0.8) * w * 0.2
    ctx.beginPath()
    ctx.moveTo(0, getWaveY(0))
    for (let x = 0; x <= w; x += 2) {
      ctx.lineTo(x, getWaveY(x))
    }
    for (let x = w; x >= 0; x -= 2) {
      ctx.lineTo(x, getWaveY(x) + 4 + 2 * Math.sin(time * 2.5))
    }
    ctx.closePath()

    const hlGrad = ctx.createLinearGradient(shimmerOffset, fillY, w + shimmerOffset, fillY)
    const shimmerAlpha = 0.25 + 0.2 * Math.sin(time * 1.5)
    hlGrad.addColorStop(0, 'rgba(232,212,139,0)')
    hlGrad.addColorStop(0.2, `rgba(255,245,200,${shimmerAlpha * 0.3})`)
    hlGrad.addColorStop(0.35, `rgba(255,240,180,${shimmerAlpha})`)
    hlGrad.addColorStop(0.5, `rgba(255,250,220,${shimmerAlpha * 1.2})`)
    hlGrad.addColorStop(0.65, `rgba(255,240,180,${shimmerAlpha})`)
    hlGrad.addColorStop(0.8, `rgba(232,212,139,${shimmerAlpha * 0.3})`)
    hlGrad.addColorStop(1, 'rgba(232,212,139,0)')
    ctx.fillStyle = hlGrad
    ctx.fill()

    // ── SURFACE LIGHT GLINTS — small bright spots on wave peaks ──
    for (let x = 0; x <= w; x += 30) {
      const wy = getWaveY(x)
      const prevY = getWaveY(x - 4)
      const nextY = getWaveY(x + 4)
      // Detect local peaks (wave crest)
      if (wy < prevY && wy < nextY) {
        const glintAlpha = 0.15 + 0.2 * Math.sin(time * 3.5 + x * 0.05)
        if (glintAlpha > 0.15) {
          ctx.beginPath()
          ctx.arc(x, wy, 2 + Math.sin(time * 4 + x) * 1, 0, Math.PI * 2)
          ctx.fillStyle = `rgba(255,255,240,${glintAlpha})`
          ctx.fill()
        }
      }
    }

    if (progress < 1) {
      rafRef.current = requestAnimationFrame(animate)
    } else if (!completedRef.current) {
      completedRef.current = true
      if (onComplete) onComplete()
    }
  }, [onComplete])

  useEffect(() => {
    if (!active) {
      completedRef.current = false
      startRef.current = null
      bubblesRef.current = []
      return
    }

    const canvas = canvasRef.current
    if (!canvas) return

    // Size canvas to parent
    const rect = canvas.parentElement.getBoundingClientRect()
    canvas.width = rect.width * (window.devicePixelRatio > 1 ? 1.5 : 1)
    canvas.height = rect.height * (window.devicePixelRatio > 1 ? 1.5 : 1)

    startRef.current = null
    completedRef.current = false
    bubblesRef.current = []
    rafRef.current = requestAnimationFrame(animate)

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
    }
  }, [active, animate])

  if (!active) return null

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 25,
      }}
    />
  )
}
