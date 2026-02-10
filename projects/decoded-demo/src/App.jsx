import { useEffect } from 'react'
import Feed from './components/Feed'

function setVh() {
  document.documentElement.style.setProperty('--vh', window.innerHeight + 'px')
}

export default function App() {
  useEffect(() => {
    setVh()
    window.addEventListener('resize', setVh)
    window.addEventListener('orientationchange', () => setTimeout(setVh, 100))
    return () => window.removeEventListener('resize', setVh)
  }, [])

  return (
    <div className="grain relative h-full w-full overflow-hidden bg-[#0D0D0D]">
      <Feed />
    </div>
  )
}
