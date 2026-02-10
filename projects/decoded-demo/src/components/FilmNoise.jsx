import { useRef, useEffect, useCallback } from 'react'

/**
 * Effect 5: Film Noise Shader on Product Videos
 * Canvas-based noise generator at ~12fps (cinematic grain, not static).
 * Only renders when isActive to save performance.
 */
export default function FilmNoise({ isActive }) {
  const canvasRef = useRef(null)
  const rafRef = useRef(null)
  const lastFrameRef = useRef(0)
  const FRAME_INTERVAL = 1000 / 12 // ~12fps cinematic frame rate

  const renderNoise = useCallback((timestamp) => {
    if (!canvasRef.current) return

    const elapsed = timestamp - lastFrameRef.current
    if (elapsed < FRAME_INTERVAL) {
      rafRef.current = requestAnimationFrame(renderNoise)
      return
    }
    lastFrameRef.current = timestamp - (elapsed % FRAME_INTERVAL)

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Use a small canvas and let CSS scale it up (performance optimization)
    const w = 128
    const h = 128
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w
      canvas.height = h
    }

    const imageData = ctx.createImageData(w, h)
    const data = imageData.data
    for (let i = 0; i < data.length; i += 4) {
      const v = Math.random() * 255
      data[i] = v
      data[i + 1] = v
      data[i + 2] = v
      data[i + 3] = 255
    }
    ctx.putImageData(imageData, 0, 0)

    rafRef.current = requestAnimationFrame(renderNoise)
  }, [])

  useEffect(() => {
    if (!isActive) {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
      return
    }

    lastFrameRef.current = 0
    rafRef.current = requestAnimationFrame(renderNoise)

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
    }
  }, [isActive, renderNoise])

  if (!isActive) return null

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 1,
        opacity: 0.04,
        mixBlendMode: 'overlay',
        imageRendering: 'auto',
      }}
    />
  )
}
