import { useState, useCallback } from 'react'
import SplashScreen from './components/SplashScreen'
import Feed from './components/Feed'
import BottomNav from './components/BottomNav'
import VaultDrawer from './components/VaultDrawer'
import DropBanner from './components/DropBanner'

export default function App() {
  const [entered, setEntered] = useState(false)
  const [splashExiting, setSplashExiting] = useState(false)
  const [activeTab, setActiveTab] = useState('home')
  const [vaultItems, setVaultItems] = useState([])
  const [showVault, setShowVault] = useState(false)
  const [lastAdded, setLastAdded] = useState(null)

  const handleEnter = useCallback(() => {
    setSplashExiting(true)
    setTimeout(() => setEntered(true), 800)
  }, [])

  const handleAddToVault = useCallback((product) => {
    setVaultItems(prev => {
      const exists = prev.find(p => p.id === product.id)
      if (exists) return prev
      return [...prev, product]
    })
    setLastAdded(product)
    setShowVault(true)
  }, [])

  if (!entered) {
    return <SplashScreen onEnter={handleEnter} exiting={splashExiting} />
  }

  return (
    <div className="grain relative h-full w-full overflow-hidden bg-[#0D0D0D]">
      <DropBanner />
      <Feed onAddToVault={handleAddToVault} />
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} vaultCount={vaultItems.length} />
      <VaultDrawer
        visible={showVault}
        item={lastAdded}
        itemCount={vaultItems.length}
        onClose={() => setShowVault(false)}
      />
    </div>
  )
}
