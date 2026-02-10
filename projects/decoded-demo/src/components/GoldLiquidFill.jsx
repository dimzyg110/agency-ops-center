import { useRef, useEffect, useCallback } from 'react'

/**
 * Effect 3: Gold Liquid Fill
 * Canvas-based gold liquid that fills from bottom, waves at the top edge,
 * then drains back down to reveal the card behind it.
 * Total animation: ~2.5 seconds.
 */
export default function GoldLiquidFill({ active, onComplete }) {
  const canvasRef = useRef(null)
  const rafRef = useRef(null)
  const startRef = useRef(null)
  const completedRef = useRef(false)
  const DURATION = 2500

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

    // Fill level: rise to 60% then drain back down
    let fillLevel
    if (progress < 0.5) {
      // Rising phase: 0 to 0.6 of screen height
      const riseProgress = progress / 0.5
      // Ease out for rising
      fillLevel = 0.6 * (1 - Math.pow(1 - riseProgress, 3))
    } else {
      // Draining phase: 0.6 back to 0
      const drainProgress = (progress - 0.5) / 0.5
      // Ease in for draining
      fillLevel = 0.6 * (1 - Math.pow(drainProgress, 2.5))
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
    const time = elapsed / 1000

    // Draw the liquid body with wave top
    ctx.beginPath()
    ctx.moveTo(0, h)
    ctx.lineTo(0, fillY)

    // Wavy top edge using sin waves
    const waveAmplitude = 8 + fillLevel * 12
    const waveFreq1 = 0.015
    const waveFreq2 = 0.025
    for (let x = 0; x <= w; x += 2) {
      const wave1 = Math.sin(x * waveFreq1 + time * 3.5) * waveAmplitude
      const wave2 = Math.sin(x * waveFreq2 - time * 2.2) * (waveAmplitude * 0.5)
      const wave3 = Math.sin(x * 0.04 + time * 5) * (waveAmplitude * 0.2)
      ctx.lineTo(x, fillY + wave1 + wave2 + wave3)
    }

    ctx.lineTo(w, h)
    ctx.closePath()

    // Gold gradient fill
    const gradient = ctx.createLinearGradient(0, fillY, 0, h)
    gradient.addColorStop(0, 'rgba(201,168,76,0.85)')
    gradient.addColorStop(0.3, 'rgba(201,168,76,0.7)')
    gradient.addColorStop(0.6, 'rgba(180,145,55,0.6)')
    gradient.addColorStop(1, 'rgba(160,130,45,0.5)')
    ctx.fillStyle = gradient
    ctx.fill()

    // Bright highlight at the surface
    ctx.beginPath()
    ctx.moveTo(0, fillY + 2)
    for (let x = 0; x <= w; x += 2) {
      const wave1 = Math.sin(x * waveFreq1 + time * 3.5) * waveAmplitude
      const wave2 = Math.sin(x * waveFreq2 - time * 2.2) * (waveAmplitude * 0.5)
      const wave3 = Math.sin(x * 0.04 + time * 5) * (waveAmplitude * 0.2)
      ctx.lineTo(x, fillY + wave1 + wave2 + wave3)
    }
    for (let x = w; x >= 0; x -= 2) {
      const wave1 = Math.sin(x * waveFreq1 + time * 3.5) * waveAmplitude
      const wave2 = Math.sin(x * waveFreq2 - time * 2.2) * (waveAmplitude * 0.5)
      const wave3 = Math.sin(x * 0.04 + time * 5) * (waveAmplitude * 0.2)
      ctx.lineTo(x, fillY + wave1 + wave2 + wave3 + 6)
    }
    ctx.closePath()
    const highlightGrad = ctx.createLinearGradient(0, fillY, w, fillY)
    highlightGrad.addColorStop(0, 'rgba(232,212,139,0.0)')
    highlightGrad.addColorStop(0.3, 'rgba(232,212,139,0.4)')
    highlightGrad.addColorStop(0.5, 'rgba(255,240,180,0.5)')
    highlightGrad.addColorStop(0.7, 'rgba(232,212,139,0.4)')
    highlightGrad.addColorStop(1, 'rgba(232,212,139,0.0)')
    ctx.fillStyle = highlightGrad
    ctx.fill()

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
